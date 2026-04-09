from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Ad, Category, City, Review
from .serializers import AdListSerializer, AdDetailSerializer, AdCreateSerializer, CategorySerializer, CitySerializer, ReviewSerializer

class StandardPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class AdViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = Ad.objects.filter(is_moderated=True).select_related('author', 'category', 'city').prefetch_related('reviews')

        # Фильтрация по категории
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Поиск
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        # Сортировка
        sort = self.request.query_params.get('sort', '-is_top')
        if sort == 'cheap':
            queryset = queryset.order_by('price', '-created_at')
        elif sort == 'expensive':
            queryset = queryset.order_by('-price', '-created_at')
        elif sort == 'free':
            queryset = queryset.filter(price=0).order_by('-created_at')
        else:
            queryset = queryset.order_by('-is_top', '-created_at')

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return AdCreateSerializer
        elif self.action == 'retrieve':
            return AdDetailSerializer
        return AdListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'detail': 'У вас нет прав для удаления этого объявления'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_ads(self, request):
        """Получить свои объявления (требует авторизации)"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)

        ads = Ad.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(ads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(ads, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Если есть query параметр ad_uuid, фильтруем по нему
        ad_uuid = self.request.query_params.get('ad_uuid')
        if ad_uuid:
            return Review.objects.filter(ad__uuid=ad_uuid).select_related('author', 'ad')
        return Review.objects.all().select_related('author', 'ad')

    def perform_create(self, serializer):
        # Проверяем есть ли ad_uuid в query параметрах или в данных
        ad_uuid = self.request.query_params.get('ad_uuid') or self.request.data.get('ad_uuid')
        if not ad_uuid:
            return Response({'detail': 'Требуется ad_uuid'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ad = Ad.objects.get(uuid=ad_uuid)
        except Ad.DoesNotExist:
            return Response({'detail': 'Объявление не найдено'}, status=status.HTTP_404_NOT_FOUND)

        serializer.save(author=self.request.user, ad=ad)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

