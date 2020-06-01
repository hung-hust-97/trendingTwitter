import socket
import sys
import requests
import requests_oauthlib
import json

# Token access API
ACCESS_TOKEN = '1024537560125648896-Bb9QdAOyhfmMFcDXX9TZStPVyihQYA'
ACCESS_SECRET = '4n5or8oS5PlrTEHVK8OOf46fZAZqGfrLaBH4AG0f2R9BN'
CONSUMER_KEY = 'vEhTyKeZfpMmdqbLmUNMsM8yA'
CONSUMER_SECRET = 'IDKxxdYyzvyBricqeRq7ko5D1SV8f4PHfZESG4qGNiOAQDhLcT'

my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_SECRET)

# Sent data tweet to spark_app
def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            tweet_text = full_tweet['text'] # pyspark can't accept stream, add '\n'
            tweet_city = full_tweet['place']['name']
            tweet_country = full_tweet['place']['country']
            time_create = full_tweet['created_at']
            data = {
                'tweet_text':tweet_text,
                'tweet_city':tweet_city,
                'tweet_country':tweet_country,
                'tweet_time_create':time_create
            }
            print("Tweet Text: " + full_tweet['text'])
            print ("------------------------------------------")
            tcp_connection.send(tweet_text.encode('utf-8'))
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

# Get data tweet follow language, location, and track '#' (is hashtags)
def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '-122.75,36.8,-122.451816,37.763006,-74,40,-73,41'),('track','#')] #San Francisco & NYC
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp,conn)



