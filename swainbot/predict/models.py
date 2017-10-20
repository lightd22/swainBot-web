from django.db import models

# Create your models here.
class Champion(models.Model):
    champ_id = models.IntegerField(name='id', primary_key=True)
    display_name = models.TextField(name='display_name', max_length=200)
    image = None
    def __str__(self):
        return self.display_name

class Position(models.Model):
    position_id = models.IntegerField(name='id', primary_key=True)
    display_name = models.TextField(name='display_name', max_length=200)
    image = None
    def __str__(self):
        return self.display_name
