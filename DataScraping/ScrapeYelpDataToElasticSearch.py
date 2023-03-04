import boto3
import json
import simplejson as json
import requests
from decimal import *
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

AWS_ACCESS_KEY=''
AWS_SECRET_KEY=''
region='us-east-1'
service='es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

es = Elasticsearch(
    hosts = "https://username:password@search-restaurants-amptynpi75fpqdmuarqhyp6iz4.us-east-1.es.amazonaws.com:443/",
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    request_timeout=30
)


API_KEY = 'mNlLYCQtXp8LZPBtExE1KXmfqn3Z-TFaMdSTby6mkSbpcIWy9VybwkeEpFu0-Bd3u6Kv-HYXICCtbp580JdsNjkBQJoa5X5dLgzKG1HkNB9jSns3wZhFO5S9gy0AZHYx' 
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

PARAMETERS = {'term': 'food', 'location': 'Manhattan', 'radius': 15000, 'limit': 50, 'offset': 400}

cuisines = ['italian', 'chinese', 'french', 'indian', 'japanese', 'korean', 'thai', 'vietnamese', 'american', 'mexican']

manhattan_neighborhoods = ['Lower East Side, Manhattan','Upper East Side, Manhattan','Upper West Side, Manhattan','Washington Heights, Manhattan','Central Harlem, Manhattan','Chelsea, Manhattan','East Harlem, Manhattan','Gramercy Park, Manhattan','Greenwich, Manhattan','Lower Manhattan, Manhattan']

business_ids={}

for neighborhood in manhattan_neighborhoods:
	PARAMETERS['location'] = neighborhood
	for cuisine in cuisines: 
		PARAMETERS['term'] = cuisine
		
		response = requests.get(url = ENDPOINT, params =  PARAMETERS, headers=HEADERS)
		business_data = response.json()['businesses']
		for business in business_data:
			if business_id not in business_ids:
				business_ids[business_id]=1
				index_data = {
					'ID': business_id,
					'Cuisine': cuisine
				}

				restaurant_data = {
					'Restaurant': index_data
				}

				es.index(index="restaurants", doc_type="_doc", id=count, body=restaurant_data, refresh=True)



