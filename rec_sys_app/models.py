from django.db import models
from django.contrib.auth.models import User


# create you model here.

# Transaction Model
class Transaction(models.Model):
    uid = models.CharField(max_length=264)
    pid = models.CharField(max_length=264)

    def __str__(self):
        return self.pid


class UserProfileInfo(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    portfolio_site = models.URLField(blank=True)
    # pip install pillow to use this!
    # Optional: pip install pillow --global-option=”build_ext” --global-option=”--disable-jpeg”
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True)

    def __str__(self):
        return self.user.username
