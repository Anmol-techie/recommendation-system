from django.db import models


# create you model here.
# Transaction Model
class Transaction(models.Model):
    uid = models.CharField(max_length=264)
    pid = models.CharField(max_length=264)

    def __str__(self):
        return self.pid
