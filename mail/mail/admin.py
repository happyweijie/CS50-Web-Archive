from django.contrib import admin
from .models import *

# Register your models here.
class EmailAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "all_recipients", "subject")

admin.site.site_header = "Mail"
admin.site.register(User)
admin.site.register(Email, EmailAdmin)
