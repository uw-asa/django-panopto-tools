from django.db import models

# Create your models here.


class PersistentData(models.Model):
    name = models.CharField(max_length=128)
    value = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
