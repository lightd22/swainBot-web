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

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.answer_text
