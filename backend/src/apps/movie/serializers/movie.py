from rest_framework import serializers

from src.apps.movie.models import Movie, Category
from src.apps.gallery.models import MovieImages


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieImages
        fields = ["image"]


class MovieSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    images = MovieImageSerializer(many=True, required=False)

    class Meta:
        model = Movie
        fields = ["title", "description", "hls_playlist", "categories", "images"]

    def create(self, validated_data):
            categories_data = validated_data.pop("categories", [])
            images_data = validated_data.pop("images", [])

            movie = Movie.objects.create(**validated_data)

            for category_data in categories_data:
                category, _ = Category.objects.get_or_create(**category_data)
                movie.categories.add(category)


            MovieImages.objects.bulk_create([
                MovieImages(movie=movie, image=image_data["image"]) for image_data in images_data
            ])

            return movie

    def update(self, instance, validated_data):
        categories_data = validated_data.pop("categories", [])
        images_data = validated_data.pop("images", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.categories.clear()
        for category_data in categories_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.categories.add(category)

        MovieImages.objects.filter(movie=instance).delete()
        MovieImages.objects.bulk_create([
            MovieImages(movie=instance, image=image_data["image"]) for image_data in images_data
        ])

        return instance