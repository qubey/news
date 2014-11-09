#!/usr/bin/python

import re
import sys
import time
import xml
import mysql.connector
import html.parser
from datetime import date, timedelta
from os import listdir, makedirs
from os.path import isfile, join
from xml.dom import minidom

DATABASE_NAME = 'news'
DATABASE_WORD_TABLE = 'trends_wordcount'
DATABASE_DOC_TABLE = 'trends_datasources'

INSERT_WORD_COUNTS_CMD = ("INSERT INTO " + DATABASE_WORD_TABLE +
              " (location, word, total_count, avg_doc_freq) "
              "VALUES (%s, %s, %s, %s)")
TRUNCATE_CMD = ("TRUNCATE TABLE %s" % DATABASE_WORD_TABLE)
INSERT_DOC_COUNTS_CMD = ("INSERT INTO " + DATABASE_DOC_TABLE +
                         "(location, doc_count) "
                         "VALUES (%s, %s)")
TRUNCATE_DOC_CMD = ("TRUNCATE TABLE %s" % DATABASE_DOC_TABLE)


INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
IGNORE_WORDS_FILE = sys.argv[3]
DB_CREDENTIALS_FILE = sys.argv[4]

# Returns the number of words counted
def countWords(sentence, count_dict, ignore_words):
    formatted = sentence.lower()
    formatted = formatted.split('<')[0]
    formatted = re.sub('[?.!,;:\'"$\(\)]', '', formatted)
    formatted = re.sub('\'s', '', formatted)
    formatted = re.sub('[\t-]', ' ', formatted)
    formatted = formatted.strip()
    words = formatted.split()

    total_words = 0
    for word in words:
        if word in ignore_words:
            continue

        if word not in count_dict.keys():
            count_dict[word] = 1
        else:
            count_dict[word] = count_dict[word] + 1
        total_words += 1

    return total_words

def combineWordCounts(in1, in2):
    for k, v in in2.items():
        if k not in in1:
            in1[k] = in2[k]
        else:
            in1[k] += in2[k]

    return in1

def updateAvgWordFreqs(word_freqs, item_word_counts, item_total_count, total_items):
    assert(total_items > 0)

    # Update all of the existing words in the dictionary
    for w, k in word_freqs.items():
        update = 0
        if w in item_word_counts:
            update = float(item_word_counts[w]) / item_total_count
            del item_word_counts[w]

        # Do a streaming average of the frequencies
        word_freqs[w] = word_freqs[w] * (float(total_items - 1) / total_items) + update * 1.0 / total_items 

    # Add the remaining words in item_word_counts since they were not
    # already in the aggregated dictionary
    for w, k in item_word_counts.items():
        assert(w not in word_freqs)
        word_freqs[w] = float(k) / item_total_count / total_items

# --
# Start of the main execution
# --
out_file_name = time.strftime('%Y-%m-%d.rss')
html = html.parser.HTMLParser()

# Get the set of words to ignore
ignore_words = []
ignore_file = open(IGNORE_WORDS_FILE, 'r')
for ignore_word in ignore_file:
    processed_ignore_word = ignore_word.strip().lower().replace(' ', '')
    ignore_words.append(processed_ignore_word)

directories = [ d for d in listdir(INPUT_DIR) if not isfile(join(INPUT_DIR, d))]

# Read the database credentials
db_file = open(DB_CREDENTIALS_FILE, 'r')
db_username = db_file.readline()
db_password = db_file.readline()
db_file.close()

# Database connection
db_connection = mysql.connector.connect(
  user=db_username,
  password=db_password,
  host='127.0.0.1',
  database=DATABASE_NAME)
db_cursor = db_connection.cursor()

db_cursor.execute(TRUNCATE_CMD)
db_cursor.execute(TRUNCATE_DOC_CMD)

for d in directories:
    output_file = join(OUTPUT_DIR, d, out_file_name)
    # make the output directory
    makedirs(name=join(OUTPUT_DIR, d), exist_ok=True)
    word_counts = {}
    total_docs = 0
    avg_word_freqs = {}

    # Aggregating over 30 days
    for i in range(30):
        in_file_date = date.today() - timedelta(days=i)
        in_file_name = in_file_date.strftime('%Y-%m-%d.rss')
        input_file = join(INPUT_DIR, d, in_file_name)

        if not isfile(input_file):
            print("Can't find " + input_file)
            continue

        try:
          rss_content = minidom.parse(input_file)
        except xml.parsers.expat.ExpatError as err:
          print("ERROR - Could not read file:" + input_file)
          continue
        channels = rss_content.getElementsByTagName('channel')

        for channel in channels:
            items = channel.getElementsByTagName('item')
            for item in items:
                doc_word_counts = {}
                doc_total_words = 0
                titleNodes = item.getElementsByTagName('title')
                if (len(titleNodes) > 0 and titleNodes[0].firstChild is not None):
                    title = titleNodes[0].firstChild.data
                    doc_total_words += countWords(html.unescape(title), doc_word_counts, ignore_words)

                descNodes = item.getElementsByTagName('description')
                if (len(descNodes) > 0 and descNodes[0].firstChild is not None):
                    desc = descNodes[0].firstChild.data
                    doc_total_words += countWords(html.unescape(desc), doc_word_counts, ignore_words)


                # Increment the number of documents for this location/directory
                total_docs += 1
                word_counts = combineWordCounts(word_counts, doc_word_counts)
                updateAvgWordFreqs(avg_word_freqs, doc_word_counts, doc_total_words, total_docs)
                

    # Write the word counts to the database
    f = open(output_file, 'w')
    for word in word_counts:
      assert(word in avg_word_freqs)
      try:
        db_cursor.execute(
          INSERT_WORD_COUNTS_CMD,
          (d, word, word_counts[word], avg_word_freqs[word])
        )
        f.write(word + "\t" + str(word_counts[word]) + "\n")
      except mysql.connector.Error as err:
        print("ERROR - Could not write to DB: " + word)
    f.close()

    try:
      db_cursor.execute(INSERT_DOC_COUNTS_CMD, (d, total_docs))
    except mysql.connector.Error as err:
      print(err)

    print("Wrote " + output_file)

db_connection.commit()
db_cursor.close()
db_connection.close()
