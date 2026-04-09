from rest_framework import serializers
from .models import Ad, Category, City, Review
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')

class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'author', 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class AdListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('uuid', 'title', 'price', 'author', 'category', 'city', 'image', 'created_at', 'is_top', 'is_moderated', 'average_rating', 'reviews_count')
        read_only_fields = ('uuid', 'created_at', 'updated_at', 'is_moderated')

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)

    def get_reviews_count(self, obj):
        return obj.reviews.count()

class AdDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ('uuid', 'author', 'created_at', 'updated_at', 'is_moderated')

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)

class AdCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()
    city_id = serializers.IntegerField()

    class Meta:
        model = Ad
        fields = ('title', 'description', 'price', 'image', 'category_id', 'city_id')

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Категория не найдена")
        return value

    def validate_city_id(self, value):
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("Город не найден")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        city_id = validated_data.pop('city_id')

        ad = Ad.objects.create(
            author=self.context['request'].user,
            category_id=category_id,
            city_id=city_id,
            **validated_data
        )
        return ad

