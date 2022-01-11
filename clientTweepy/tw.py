import datetime
import tweepy
import re
from textblob import TextBlob
from login import *
import logging
import typing

logger = logging.getLogger()


class Tweets:
    def __init__(self, usernames: typing.List[str]):
        self.usernames = usernames
        self.accounts = dict()
        self.full_data = []

        self.tweets_data = dict()

        for username in self.usernames:
            self.getUsers(username)

    def getClient(self):
        client = tweepy.Client(bearer_token=BEARER_TOKEN,
                               consumer_key=API_KEY,
                               consumer_secret=API_SECRET,
                               access_token=ACCESS_TOKEN,
                               access_token_secret=ACCESS_SECRET)
        return client

    def getUsers(self, username):
        client = self.getClient()
        users = client.get_user(username=username, user_fields='created_at')
        self.accounts[username] = users.data.id
        logger.warning('Requesting users | getting %s', username)

    def getTweets(self, id, user):
        try:
            client = self.getClient()
            d = client.get_users_tweets(id=id, max_results=5, tweet_fields=['created_at'])
            if d is not None:
                tweet = d.data[0]
                self.tweets_data['username'] = user
                self.tweets_data['tweet'] = tweet.text
                date = datetime.datetime.strftime(tweet.created_at,'%Y-%m-%d %H:%M')
                self.tweets_data['tweeted'] = date
            else:
                logger.warning('No data from %s', user)
                print(d)
        except RuntimeError:
            pass

    def cleanTwt(self, twt):
        twt = re.sub('\\n', '', twt)
        # twt = re.sub('#[A-Za-z0-9]+', '', twt)
        twt = re.sub(r"http\S+", '', twt)
        return twt

    def getSubj(self, twt):
        return TextBlob(twt).sentiment.subjectivity

    def getPol(self, twt):
        return TextBlob(twt).sentiment.polarity

    def getSent(self, score):
        if score < 0:
            return 'Negative'
        elif score == 0:
            return 'Neutral'
        else:
            return 'Positive'

    def getSent2(self, score):
        if score == 0:
            return 'Objective'
        elif score > 0 and score < 1.0:
            return 'Subjective'
        else:
            return 'Very Subjective'
