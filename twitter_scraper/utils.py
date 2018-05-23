import requests
import logging
from lxml import html
from bs4 import BeautifulSoup
from twitter_scraper import HEADER

logger = logging.getLogger('TwitAnalysis')


def parse_response(html_to_parse):
    """Parses the html text of a request to twitter. The text can either be a
    full page or the response to an ajax call.
    The parser returns a list of dictionaries. Each element will have the
    following keys:
    * text: The text of the tweet
    * id: The id of the tweet. It is a unique identifier for the tweet
    * timestamp: The timestamp, in Twitter time zone
    * replies: Number of replies at the time of the scan
    * favorite: Number of favorites
    * retweet: Number of retweets
    """
    soup = BeautifulSoup(html_to_parse, "html5lib")

    tweets_list = []

    tweets = soup.find_all('li', {'data-item-type': 'tweet'})
    for tweet in tweets:
        try:
            text = tweet.find('p').text
            if text == '':
                continue

            tweet_data = tweet.find('div',{'class':'tweet'})

            # If it is a retweet, the ID of the original tweet:
            data_retweet_id = tweet_data.get('data-retweet-id')
            if data_retweet_id:
                id = int(data_retweet_id)
                retweet = {'id': int(tweet_data['data-tweet-id']),
                           'user-id': int(tweet_data['data-user-id'])}
            else:
                id = int(tweet_data['data-tweet-id'])
                retweet = None

            # If the article has links, it includes hashtags and mentions
            links = tweet.find('p').find_all('a', href=True)
            tweet_links = None
            if links:
                tweet_links = []
                for link in links:
                    tweet_links.append({'url':link['data-expanded-url'],
                                        'text': link.text})

            timestamp = int(tweet_data.find('span',{'class':'_timestamp'})['data-time'])
            replies = int(tweet_data.find('span',{'class':'ProfileTweet-action--reply'}).find('span')['data-tweet-stat-count'])
            favorites = int(tweet_data.find('span',{'class':'ProfileTweet-action--favorite'}).find('span')['data-tweet-stat-count'])
            retweets = int(tweet_data.find('span',{'class':'ProfileTweet-action--retweet'}).find('span')['data-tweet-stat-count'])
            tweets_list.append(dict(id=id,
                text=text,
                timestamp=timestamp,
                replies=replies,
                favorites=favorites,
                retweets=retweets,
                retweet=retweet,
                tweet_links=tweet_links))
        except:
            pass

    return tweets_list


def get_tweets(query):
    """ Gets all the tweets based on a flexible query.
    """
    headers = HEADER
    BASE_API = "https://twitter.com/i/search/timeline?"
    base_query = "vertical=default&q={}&src=typd&include_available_features=1&include_entities=1".format(query)
    tweets = []
    # min_tweet = None
    payload = base_query
    logger.debug(payload)
    r = requests.get(BASE_API+payload, headers=headers)
    data = r.json()
    while r is not None and data['new_latent_count'] != 0:
        new_tweets = parse_response(data['items_html'])
        logger.debug('Got {} new tweets'.format(len(new_tweets)))
        if len(new_tweets) == 0:
            break
        tweets += new_tweets

        min_tweet = new_tweets[-1]
        logger.debug('Min tweet id: {}'.format(min_tweet['id']))

        max_tweet = new_tweets[0]
        logger.debug('Max tweet id: {}'.format(max_tweet['id']))

        if min_tweet['id'] is not max_tweet['id']:
            if 'min_position' in data.keys():
                logger.debug('min_position in data')
                max_position = "&max_position={}".format(data['min_position'])
            else:
                logger.debug('using max position from tweets')
                max_position = "&max_position=TWEET-{}-{}".format(min_tweet['id'], max_tweet['id'])

            logger.debug(max_position)
            query = base_query + max_position
            payload = query
            logger.debug(payload)
            r = requests.get(BASE_API+payload, headers=headers)
            data = r.json()
        else:
            logger.debug('Min tweet is max tweet')
    logger.debug(data)
    return tweets


def get_timeline_user(username, min_id=0, max_tweets=0):
    """ Get all the tweets of a given username

    :param username: the username to scan
    :type username: string
    :param min_id: the minimum id of the tweet to retrieve. In order to limit the scan to the latest known tweet
    :type min_id: int
    :param max_tweets: maximum number of tweets to retrieve. If left to 0, no maximum
    :type max_tweets: int
    :return: list of tweets
    :rtype: list
    """
    if username.startswith('@'):
        username = username.replace('@', '')

    headers = HEADER
    BASE_API = "https://twitter.com/i/profiles/show/{username}/timeline/tweets?".format(username=username)
    base_query = "composed_count=0&include_available_features=1&include_entities=1&include_new_items_bar=true&interval=30000&latent_count=0"

    tweets = []
    payload = BASE_API + base_query
    logger.debug(payload)
    r = requests.get(payload, headers=headers)
    data = r.json()
    while r is not None and data['new_latent_count'] != 0:
        new_tweets = parse_response(data['items_html'])
        logger.debug('Got {} new tweets'.format(len(new_tweets)))
        if len(new_tweets) == 0:
            break
        tweets += new_tweets

        if max_tweets and len(tweets)>=max_tweets:
            break

        min_tweet = new_tweets[-1]
        if min_tweet['id'] <= min_id:
            break

        logger.debug('Min tweet id: {}'.format(min_tweet['id']))

        max_tweet = new_tweets[0]
        logger.debug('Max tweet id: {}'.format(max_tweet['id']))

        if min_tweet['id'] is not max_tweet['id']:
            if 'min_position' in data.keys():
                logger.debug('min_position in data')
                max_position = "&max_position={}".format(data['min_position'])

            else:
                logger.debug('using max position from tweets')
                max_position = "&max_position=TWEET-{}-{}".format(min_tweet['id'], max_tweet['id'])


            logger.debug(max_position)
            query = base_query + max_position
            payload = query
            logger.debug(payload)
            r = requests.get(BASE_API + payload, headers=headers)
            data = r.json()
        else:
            logger.debug('Min tweet is max tweet')
    return tweets

if __name__ == "__main__":
    logger = logging.getLogger('TwitAnalysis')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    my_tweets = get_timeline_user('_aquic_', max_tweets=50)
    print(len(my_tweets))