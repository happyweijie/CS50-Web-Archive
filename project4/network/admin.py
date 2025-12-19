from django.contrib import admin
from .models import *

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "poster", "content",)
    list_filter = ("timestamp",)

admin.site.site_header = "Network"
admin.site.register(User)
admin.site.register(Post, PostAdmin)