from django.db import models

# Create your models here.
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=20)
    email = models.EmailField()
    course = models.CharField(max_length=100)

    def __str__(self):
        return self.name
