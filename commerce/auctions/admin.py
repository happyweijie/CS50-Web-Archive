from django.contrib import admin
from .models import *

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "creator")
    list_filter = ("publish_time",)


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "user", "price",)
    list_filter = ("acceptance",)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "auction")

admin.site.site_header = "Auctions"
admin.site.register(User)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
