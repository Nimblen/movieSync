from django.utils.html import format_html
from django.contrib import admin
from src.apps.movie.models.movie import Movie, MovieUpload
from src.apps.gallery.models.movie import MovieImages
from src.apps.movie.tasks import process_movie_upload
from src.apps.core.constants import FileUploadStatus
# Register your models here.





class MovieImagesInline(admin.TabularInline):
    model = MovieImages



class MovieAdmin(admin.ModelAdmin):
    inlines = [MovieImagesInline]
    list_display = ['title', 'thumbnail']
    list_filter = ['categories']
    search_fields = ['title']

    def thumbnail(self, obj):
        first_image = obj.get_first_image()
        if first_image and first_image.image:  
            return format_html('<img src="{}" width="40" />'.format(first_image.image.url))
        return "No Image"


admin.site.register(Movie, MovieAdmin)




@admin.register(MovieUpload)
class MovieUploadAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    actions = ['retry_movie_upload']

    def retry_movie_upload(self, request, queryset):
        for upload in queryset:
            if upload.status == FileUploadStatus.FAILED:
                process_movie_upload.delay(upload.id)
                upload.status = FileUploadStatus.PENDING
                upload.save() 
            else:
                self.message_user(request, f"Movie upload with id {upload.id} has status {upload.status} and cannot be retried.")
    retry_movie_upload.short_description = "Retry convert to HLS"