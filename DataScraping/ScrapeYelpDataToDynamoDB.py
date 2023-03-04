import boto3
from datetime import datetime
import json
import simplejson as json
import requests
from decimal import *

AWS_ACCESS_KEY=''
AWS_SECRET_KEY=''
REGION_NAME='us-east-1'

def check_empty(input):
	if len(str(input)) == 0:
		return 'N/A'
	else:
		return input


dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
table = dynamodb.Table('yelp-restaurants')

API_KEY = 'mNlLYCQtXp8LZPBtExE1KXmfqn3Z-TFaMdSTby6mkSbpcIWy9VybwkeEpFu0-Bd3u6Kv-HYXICCtbp580JdsNjkBQJoa5X5dLgzKG1HkNB9jSns3wZhFO5S9gy0AZHYx' 
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

PARAMETERS = {'term': 'food', 'location': 'Manhattan', 'radius': 15000, 'limit': 50, 'offset': 400}

cuisines = ['italian', 'chinese', 'french', 'indian', 'japanese', 'korean', 'thai', 'vietnamese', 'american', 'mexican']

manhattan_neighborhoods = ['Lower East Side, Manhattan','Upper East Side, Manhattan','Upper West Side, Manhattan','Washington Heights, Manhattan','Central Harlem, Manhattan','Chelsea, Manhattan','East Harlem, Manhattan','Gramercy Park, Manhattan','Greenwich, Manhattan','Lower Manhattan, Manhattan']

for neighborhood in manhattan_neighborhoods:
	PARAMETERS['location'] = neighborhood
	for cuisine in cuisines: 
		PARAMETERS['term'] = cuisine
		
		response = requests.get(url = ENDPOINT, params =  PARAMETERS, headers=HEADERS)
		business_data = response.json()['businesses']
		for business in business_data:
			now = datetime.now()
			restauraunt_data = {}
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			table.put_item(
			Item = {
				'ID':business['id'],
				'TimeStampInserted': check_empty(dt_string),
				'Name':  check_empty(business['name']),
				'Cuisine': cuisine,
				'Rating': check_empty(Decimal(business['rating'])),
				'Number of Reviews' : check_empty(Decimal(business['review_count'])),
				'Address': check_empty(business['location']['address1']),
				'Zip Code': check_empty(business['location']['zip_code']),
				'Latitude': check_empty(str(business['coordinates']['latitude'])),
				'Longitude': check_empty(str(business['coordinates']['longitude']))
			}
			)

