from django.db import models


# Create your models here.

class Shelf(models.Model):
    
    shelf_name = models.CharField(max_length=50)
    total_number_of_books = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return self.shelf_name

    