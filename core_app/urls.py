from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

# REST API Router
router = DefaultRouter()
router.register(r'ads', api.AdViewSet, basename='api-ad')
router.register(r'reviews', api.ReviewViewSet, basename='api-review')
router.register(r'categories', api.CategoryViewSet, basename='api-category')
router.register(r'cities', api.CityViewSet, basename='api-city')

urlpatterns = [
    # API
    path('api/v1/', include(router.urls)),

    # Главная страница и категории
    path('', views.ad_list_view, name='ad_list'),
    path('category/<slug:slug>/', views.ad_list_view, name='category_list'),

    # CRUD объявлений и избранное
    path('ad/new/', views.ad_create_view, name='ad_create'),
    path('ad/<uuid:uuid>/', views.ad_detail_view, name='ad_detail'),
    path('ad/<uuid:uuid>/edit/', views.ad_update_view, name='ad_update'),
    path('ad/<uuid:uuid>/delete/', views.ad_delete_view, name='ad_delete'),
    path('ad/<uuid:uuid>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('ad/<uuid:uuid>/review/', views.create_review, name='create_review'),

    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),

    # Авторизация и регистрация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]