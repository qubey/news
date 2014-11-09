from django.shortcuts import render

from trends.models import WordCount

WORDS_PER_CITY = 10

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

def search(request, query):
  raw_word_list = WordCount.objects.filter(word__iexact=query).order_by('-avg_doc_freq')
  context = {
    'word_list': raw_word_list,
  }
  return render(request, 'trends/word_list.html', context)

def stuff(request):
  return render(request, 'trends/test.html', None)

def asyncCity(request, city):
  sanitized_city = city.replace(' ', '_').replace('.', '').lower()
  word_list = WordCount.objects.filter(
    location__iexact=sanitized_city
  ).order_by('-avg_doc_freq')
  context = {
    'city': city,
    'results': word_list
  }
  return render(request, 'trends/async_city.html', context)

