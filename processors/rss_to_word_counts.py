#!/usr/bin/python

import sys
import time
from os import listdir, makedirs
from os.path import isfile, join
from xml.dom import minidom

# read xml file
# get all elements by tag name 'channel'
# get all elements by tag name 'item'
# item.title, item.description

input_dir = sys.argv[1]
output_dir = sys.argv[2]
out_file = time.strftime('%Y-%m-%d.rss')

directories = [ d for d in listdir(input_dir) if not isfile(join(input_dir, d))]
for d in directories:
    input_file = join(input_dir, d, out_file)
    output_file = join(output_dir, d, out_file)
    
    # make the output directory
    makedirs(name=join(output_dir, d), exist_ok=True)

    rss_content = minidom.parse(input_file)
    channels = rss_content.getElementsByTagName('channel')

    print("===================")
    print(output_file)
    print("===================")
    for channel in channels:
        items = channel.getElementsByTagName('item')
        for item in items:
            titleNodes = item.getElementsByTagName('title')
            title = 'No title'
            if (len(titleNodes) > 0):
                title = titleNodes[0].firstChild.data
            desc = 'No description'
            descNodes = item.getElementsByTagName('description')
            if (len(descNodes) > 0 and descNodes[0].firstChild is not None):
                desc = descNodes[0].firstChild.data

            print("Title: " + title)
            print("Desc: " + desc)
            print("--")
