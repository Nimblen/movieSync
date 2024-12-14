from django.utils.html import format_html
from django.contrib import admin
from src.apps.movie.models.movie import Movie
from src.apps.gallery.models.movie import MovieImages
# Register your models here.





class MovieImagesInline(admin.TabularInline):
    model = MovieImages



class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieImagesInline]
    list_display = ['title', 'thumbnail']
    list_filter = ['categories']
    search_fields = ['title']

    def thumbnail(self, obj):
        return format_html('<img src="{}" width="40" />'.format(obj.get_first_image().image.url))
    


admin.site.register(Movie, MovieAdmin)