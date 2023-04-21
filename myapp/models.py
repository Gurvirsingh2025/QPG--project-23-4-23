# from django.db import models

# Create your models here.

# this model is make for store the questions
# class question_bank(models.Model):
#     question=models.CharField(max_length=100)
#     question_id=models.CharField(max_length=100)
#     question_type=models.CharField(max_length=100)
#     question_topic=models.CharField(max_length=100)
#     question_subject=models.CharField(max_length=100)
#     question_marks=models.IntegerField(1)
#     question_difficulty=models.CharField(max_length=100)
#     question_lavel=models.CharField(max_length=100)


from django.db import models


class Question(models.Model):
    question = models.CharField(max_length=255)
    question_subject = models.CharField(max_length=50)
    question_topic = models.CharField(max_length=50)
    # question_type = models.CharField(max_length=20)
    question_difficulty = models.CharField(max_length=20) # Use ArrayField to store an array of bloom taxonomy values


    def __str__(self):
        return self.question