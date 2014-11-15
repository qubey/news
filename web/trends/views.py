from django.shortcuts import render

from trends.models import WordCount
import json

WORDS_PER_CITY = 10

class Result:
  def __init__(self, value, num):
    self.value = value
    self.count = num

# Create your views here.
def index(request):
  raw_word_list = WordCount.objects.order_by('location', '-avg_doc_freq')
  city_count = 0
  current_city = ''
  cities = []
  word_list = []
  for word in raw_word_list:
    if word.location != current_city:
      city_count = 0
      current_city = word.location
      word_list = []
      cities.append((word.location.replace('_', ' '), word_list))

    if city_count >= WORDS_PER_CITY:
      continue

    current_city = word.location
    word_list.append(word)
    city_count = city_count + 1
    
  context = {
    'city_words': cities
  }
  return render(request, 'trends/city_list.html', context)

def search(request):
  query = request.GET.get('q', '')
  raw_word_list = WordCount.objects.filter(word__iexact=query).order_by('-avg_doc_freq')
  data_dict = {}
  max_score = 0
  # get the max count
  for word in raw_word_list:
    if word.avg_doc_freq > max_score:
      max_score = word.avg_doc_freq

  for word in raw_word_list:
    if max_score > 0:
      data_dict[word.location] = word.avg_doc_freq / max_score

  context = {
    'query': query,
    'results': [
      Result(word.location.replace('_', ' '), word.total_count)
      for word in raw_word_list
    ],
    'word_data': json.dumps(data_dict),
    'search_text': query,
  }
  return render(request, 'trends/map_search.html', context)

def stuff(request):
  return render(request, 'trends/map_all.html', None)

def asyncCity(request, city):
  sanitized_city = city.replace(' ', '_').replace('.', '').lower()
  word_list = WordCount.objects.filter(
    location__iexact=sanitized_city
  ).order_by('-avg_doc_freq')[:40]
  context = {
    'query': city,
    'results': [ Result(word.word, word.total_count) for word in word_list ]
  }
  return render(request, 'trends/async_city.html', context)

