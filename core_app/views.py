from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Ad, Category, Favorite, Banner, Review
from .forms import UserRegisterForm, AdForm, ReviewForm

# --- АВТОРИЗАЦИЯ ---

def register_view(request):
    if request.user.is_authenticated: return redirect('ad_list')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт создан! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('profile')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('ad_list')

# --- ПРОФИЛЬ ---

@login_required
def profile_view(request):
    my_ads = Ad.objects.filter(author=request.user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=request.user).select_related('ad')
    return render(request, 'profile.html', {'my_ads': my_ads, 'favorites': favorites})

# --- ОБЪЯВЛЕНИЯ (КАТАЛОГ И ДЕТАЛИ) ---

def ad_list_view(request, slug=None):
    ads = Ad.objects.filter(is_moderated=True)
    if slug: ads = ads.filter(category__slug=slug)

    # Поиск
    q = request.GET.get('q')
    if q: ads = ads.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Сортировка
    sort = request.GET.get('sort')
    if sort == 'cheap': ads = ads.order_by('price', '-created_at')
    elif sort == 'expensive': ads = ads.order_by('-price', '-created_at')
    elif sort == 'free': ads = ads.filter(price=0).order_by('-created_at')
    else: ads = ads.order_by('-is_top', '-created_at')

    # Пагинация
    page_obj = Paginator(ads, 9).get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'banners': Banner.objects.filter(is_active=True),
        'current_category': slug,
        'query_params': request.GET.copy().pop('page', True) and request.GET.urlencode()
    }
    return render(request, 'ad_list.html', context)

def ad_detail_view(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, ad=ad).exists()
    return render(request, 'ad_detail.html', {'ad': ad, 'is_favorite': is_favorite})

# --- CRUD ОБЪЯВЛЕНИЙ ---

@login_required
def ad_create_view(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES) # request.FILES обязателен для картинок!
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.is_moderated = False # Отправляем на модерацию
            ad.save()
            messages.success(request, 'Объявление отправлено на проверку.')
            return redirect('profile')
    else:
        form = AdForm()
    return render(request, 'ad_form.html', {'form': form})

@login_required
def ad_update_view(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    if ad.author != request.user: return HttpResponseForbidden("Доступ запрещен.")

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено.')
            return redirect('ad_detail', uuid=ad.uuid)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ad_form.html', {'form': form})

@login_required
def ad_delete_view(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    if ad.author != request.user: return HttpResponseForbidden("Доступ запрещен.")

    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление удалено.')
        return redirect('profile')
    return render(request, 'ad_confirm_delete.html', {'ad': ad})

# --- ИЗБРАННОЕ ---

@login_required
def toggle_favorite(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    fav, created = Favorite.objects.get_or_create(user=request.user, ad=ad)
    if not created: fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'ad_list'))

@login_required
def create_review(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid)
    
    # Проверяем есть ли уже отзыв от этого пользователя
    existing_review = Review.objects.filter(author=request.user, ad=ad).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.ad = ad
            review.save()
            messages.success(request, 'Ваш отзыв сохранён.')
            return redirect('ad_detail', uuid=ad.uuid)
    else:
        form = ReviewForm(instance=existing_review)
    
    return render(request, 'review_form.html', {'form': form, 'ad': ad})
