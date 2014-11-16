#1/bin/bash
python $NEWS_HOME/processors/rss_to_word_counts.py \
       $NEWS_HOME/data/raw_feeds/ \
       $NEWS_HOME/data/word_counts \
       $NEWS_HOME/data/configs/stupid_words.txt \
       $NEWS_HOME/data/configs/db_credentials.txt
