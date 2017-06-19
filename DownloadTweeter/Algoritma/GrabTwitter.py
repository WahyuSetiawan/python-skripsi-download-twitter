import tweepy
from tweepy import OAuthHandler
import datetime as dt
import time
import os, sys, urllib, re
import argparse, codecs, unicodedata
import csv, json
from PyQt5.QtCore import pyqtSignal

class DownloadTweet():
    update = pyqtSignal(str)

    '''
    time_limit = 20                          # runtime limit in hours
    max_tweets = 100                           # number of tweets per search (will be
                                                # iterated over) - maximum is 100
    min_days_old, max_days_old = 0,10          # search limits e.g., from 7 to 8
                                                # gives current weekday from last week,
                                                # min_days_old=0 will search from right now
    JBD = '-6.2891084,106.7560364,1000km'       # this geocode includes nearly all American
    '''

    time_limit = 0
    max_tweets = 0
    min_days_old, max_days_old = 0,10          
    JBD = ""

    def load_api(self):
        ''' 

        consumer_key = 'AHflU3eUHFptyTUQa36LIh51h'
        consumer_secret = 'yLip0yMALlJBZhmWqG3yMwMZ1kk7UbMBJXy4gHXJOfSAvxD6BW'
        access_token = '99135508-bI8CfvBd9doKyxQs5iVdLgUMiYorA7mT12Zh9nJHG'
        access_secret = 'rmqbrYHkYKHr3Z14qgPCBnbjVIn3EWO0aYfA52phFInb0'

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        '''

        config = {}
        # from file args
        if os.path.exists('config.json'):
            with open('config.json') as f:
                config.update(json.load(f))
        else:
            # may be from command line
            parser = argparse.ArgumentParser()

            parser.add_argument('-ck', '--consumer_key', default=None, help='Your developper `Consumer Key`')
            parser.add_argument('-cs', '--consumer_secret', default=None, help='Your developper `Consumer Secret`')
            parser.add_argument('-at', '--access_token', default=None, help='A client `Access Token`')
            parser.add_argument('-ats', '--access_token_secret', default=None, help='A client `Access Token Secret`')

            args_ = parser.parse_args()
            def val(key):
                return config.get(key)\
                    or getattr(args_, key)\
                    or raw_input('Your developper `%s`: ' % key)
            config.update({
                'consumer_key': val('consumer_key'),
                'consumer_secret': val('consumer_secret'),
                'access_token': val('access_token'),
                'access_token_secret': val('access_token_secret'),
            })
        # should have something now

        auth = OAuthHandler(config.get('consumer_key'), config.get('consumer_secret'))
        auth.set_access_token(config.get('access_token'), config.get('access_token_secret'))
        # load the twitter API via tweepy
        return tweepy.API(auth)

    
    def tweet_search(self, api, query, max_tweets, max_id, since_id,geocode):
        searched_tweets = []
        while len(searched_tweets) < max_tweets:
            remaining_tweets = max_tweets - len(searched_tweets)
            try:
                new_tweets = api.search(q=query+" -filter:retweets", count=remaining_tweets,
                                        since_id=str(since_id),
				        max_id=str(max_id-1),geocode=geocode)
                #print('found',len(new_tweets),'tweets')
                if not new_tweets:
                    #print('no tweets found')
                    break
                searched_tweets.extend(new_tweets)
                max_id = new_tweets[-1].id
            except tweepy.TweepError:
                #print('exception raised, waiting 15 minutes')
                #print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
                time.sleep(15*60)
                break # stop the loop
        return searched_tweets, max_id


    def get_tweet_id(self, api, date='', days_ago=9, query='a'):
        if date:
            # return an ID from the start of the given day
            td = date + dt.timedelta(days=1)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            tweet = api.search(q=query, count=1, until=tweet_date)
        else:
            # return an ID from __ days ago
            td = dt.datetime.now() - dt.timedelta(days=days_ago)
            tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
            # get list of up to 10 tweets
            tweet = api.search(q=query, count=10, until=tweet_date)
            #print('search limit (start/stop):',tweet[0].created_at)
            # return the id of the first tweet in the list
            return tweet[0].id

    def write_tweets(self, tweets, filename, csvfile):
        with open(filename, 'a') as f:
            for tweet in tweets:
                json.dump(tweet._json, f)
                f.write('\n')

        with open(csvfile, 'w', newline='') as csvfile:
            cv = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for tweet in tweets:
                cv.writerow([tweet.text.encode('ascii', 'ignore').decode('unicode_escape')])

    def getTweet(self, search_phrase):
        self.cetak('Search phrase ='.join(search_phrase))
        
        #''' other variables 
        name = search_phrase.split()[0]
        json_file_root = name + '/'  + name
        os.makedirs(os.path.dirname(json_file_root), exist_ok=True)
        read_IDs = False
        #'''
        
        #''' open a file in which to store the tweets
        if self.max_days_old - self.min_days_old == 1:
            d = dt.datetime.now() - dt.timedelta(days = self.min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
        else:
            d1 = dt.datetime.now() - dt.timedelta(days = self.max_days_old-1)
            d2 = dt.datetime.now() - dt.timedelta(days = self.min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                    d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
        #'''

        #'''
        json_file = json_file_root + '_' + day + '.json'
        if os.path.isfile(json_file):
            #print('Appending tweets to file named: ', json_file)
            read_IDs = True

        csv_file = json_file_root + '_' + day + '.csv'
        if os.path.isfile(csv_file):
            #print('Appending tweets to file named: ', csv_file)
            read_IDs = True
        #'''
        
        #''' authorize and load the twitter API
        api = self.load_api()
        #'''

        #''' set the 'starting point' ID for tweet collection
        if read_IDs:
            # open the json file and get the latest tweet ID
            with open(json_file, 'r') as f:
                lines = f.readlines()
                #print(json.loads(lines[-1])['id'])
                max_id = int(json.loads(lines[-1])['id'])
                #print('Searching from the bottom ID in file')
        else:
            # get the ID of a tweet that is min_days_old
            if self.min_days_old == 0:
                max_id = -1
            else:
                max_id = self.get_tweet_id(api, days_ago=(self.min_days_old-1))

        # set the smallest ID to search for
        since_id = self.get_tweet_id(api, days_ago=(self.max_days_old-1))
        #print('max id (starting point) =', max_id)
        #print('since id (ending point) =', since_id)
        #'''

        #''' tweet gathering loop 
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=self.time_limit)
        count, exitcount = 0, 0
        while dt.datetime.now() < end:
            count += 1
            print('count =',count)
            # collect tweets and update max_id
            tweets, max_id = self.tweet_search(api, search_phrase, self.max_tweets,
                                            max_id=max_id, since_id=since_id
                                            ,geocode=self.JBD)
            # write tweets to file in JSON format
            if tweets:
                self.write_tweets(tweets, json_file, csv_file)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if search_phrase == search_phrases[-1]:
                        sys.exit('Maximum number of empty tweet strings reached - exiting')
                    else:
                        self.cetak('Maximum number of empty tweet strings reached - breaking')
                        break
            time.sleep(1)
        #'''
        return

    def run(self, nama):
        self.cetak(nama)
        self.getTweet(nama)
        return

    def cetak(self, pesan):
        print(pesan)
        self.update.emit(pesan)


