import uuid
from django.db import models
from django.contrib.auth.models import User
from pytils.translit import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ad(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads', verbose_name="Категория")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.PositiveIntegerField(verbose_name="Цена (в тенге)", help_text="Укажите 0, если бесплатно")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, verbose_name="Изображение")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_moderated = models.BooleanField(default=False, verbose_name="Прошло модерацию")
    is_top = models.BooleanField(default=False, verbose_name="Топ объявление (VIP)")

    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favorited_by')
    image = models.ImageField(upload_to='favorites/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        unique_together = ('user', 'ad')

class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('author', 'ad')
        ordering = ('-created_at',)

    def __str__(self):
        return f"Отзыв от {self.author.username} на '{self.ad.title}' ({self.rating}★)"
