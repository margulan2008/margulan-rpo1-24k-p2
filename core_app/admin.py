from django.contrib import admin
from .models import Category, City, Ad, Favorite, Banner, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'city', 'price', 'is_moderated', 'is_top', 'created_at')
    list_filter = ('is_moderated', 'is_top', 'category', 'city')
    search_fields = ('title', 'description', 'author__username')
    list_editable = ('is_moderated', 'is_top')
    ordering = ('-is_top', '-created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'link')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'ad', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('author__username', 'ad__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
