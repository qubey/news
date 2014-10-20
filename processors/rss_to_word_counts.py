#!/usr/bin/python

import re
import sys
import time
from datetime import date, timedelta
from os import listdir, makedirs
from os.path import isfile, join
from xml.dom import minidom

def countWords(sentence, countDict):
    formatted = sentence.lower()
    formatted = formatted[:formatted.find('<')]
    formatted = re.sub('[.!,;]', '', formatted)
    formatted = re.sub('\t', ' ', formatted)
    formatted = formatted.strip()
    words = formatted.split()
    for word in words:
        if word not in countDict.keys():
            countDict[word] = 1
        else:
            countDict[word] = countDict[word] + 1

input_dir = sys.argv[1]
output_dir = sys.argv[2]
out_file_name = time.strftime('%Y-%m-%d.rss')

directories = [ d for d in listdir(input_dir) if not isfile(join(input_dir, d))]

for d in directories:
    output_file = join(output_dir, d, out_file_name)
    # make the output directory
    makedirs(name=join(output_dir, d), exist_ok=True)

    # Aggregating over 30 days
    for i in range(30):
        in_file_date = date.today() - timedelta(days=i)
        in_file_name = in_file_date.strftime('%Y-%m-%d.rss')
        input_file = join(input_dir, d, in_file_name)

        if not isfile(input_file):
            print("Can't find " + input_file)
            continue

        word_counts = {}
        rss_content = minidom.parse(input_file)
        channels = rss_content.getElementsByTagName('channel')

        for channel in channels:
            items = channel.getElementsByTagName('item')
            for item in items:
                titleNodes = item.getElementsByTagName('title')
                if (len(titleNodes) > 0):
                    title = titleNodes[0].firstChild.data
                    countWords(title, word_counts)

                descNodes = item.getElementsByTagName('description')
                if (len(descNodes) > 0 and descNodes[0].firstChild is not None):
                    desc = descNodes[0].firstChild.data
                    countWords(desc, word_counts)
                

    f = open(output_file, 'w')
    for word in word_counts:
        f.write(word + "\t" + str(word_counts[word]) + "\n")
    f.close()
    print("Wrote " + output_file)
