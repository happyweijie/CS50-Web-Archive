from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    followers = models.ManyToManyField("self", blank=True, default=None, symmetrical=False, related_name="following")

    def followers_count(self):
        return len(self.followers.all())
    
    def following_count(self):
        return len(self.following.all())
    
class Post(models.Model):
    poster = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="posts")
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(default=datetime.now)
    likes = models.ManyToManyField(User, blank=True, default=None, related_name="liked_posts")

    def __str__(self):
        return f"{self.poster} posted '{self.content}' at {self.timestamp}."
    
    def likes_count(self):
        return len(self.likes.all())
    
    def serialize(self):
        return {
            "poster": self.poster.username,
            "content": self.content,
            "likes": self.likes_count(),
            "timestamp": self.timestamp
        }


class Comment(models.Model):
    post = models.ForeignKey(Post, null=True, on_delete=models.SET_NULL, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=500)
    posted_time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user.username} posted {self.text} on {self.post.content}."