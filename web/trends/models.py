from django.db import models

# Create your models here.
class WordCount(models.Model):
  location = models.CharField(max_length=30)
  word = models.CharField(max_length=128)
  total_count = models.IntegerField()
  avg_doc_freq = models.FloatField()

class DataSources(models.Model):
  location = models.CharField(max_length=30, primary_key=True)
  doc_count = models.IntegerField()

  def __str__(self):
    return self.location + ", " + self.word + ": " + str(self.total_count)
    
