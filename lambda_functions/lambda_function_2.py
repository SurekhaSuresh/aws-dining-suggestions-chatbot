import boto3
import json
import requests
import random
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

AWS_ACCESS_KEY='AKIAUN2FGPLSJY6VADDC'
AWS_SECRET_KEY='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'
REGION_NAME='us-east-1'

def receiveMsgFromSqsQueue():
    sqs = boto3.client('sqs', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    queue_url = 'https://sqs.us-east-1.amazonaws.com/304550935268/Q1'
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
        )
    return response

def findRestaurantFromElasticSearch(cuisine):
    
    service='es'

    awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION_NAME, service)

    es = Elasticsearch(
        hosts = "https://username:password@search-restaurants-amptynpi75fpqdmuarqhyp6iz4.us-east-1.es.amazonaws.com:443/",
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        request_timeout=30
    )
    
    res = es.search(index="restaurants", body={"query": {"query_string": {"query":cuisine}}})
    
    hits = res['hits']['hits']
    buisinessIds = []
    for hit in hits:
        buisinessIds.append(str(hit['_source']['Restaurant']['ID']))
    return buisinessIds

def getRestaurantFromDb(restaurantIds):
    res = []
    client = boto3.resource('dynamodb', region_name=REGION_NAME,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    table = client.Table('yelp-restaurants')
    for id in restaurantIds:
        response = table.get_item(Key={'ID': id})
        res.append(response)
    return res

def getMsgToSend(restaurantDetails,message):
    noOfPeople = message['MessageAttributes']['People']['StringValue']
    date = message['MessageAttributes']['Date']['StringValue']
    time = message['MessageAttributes']['Time']['StringValue']
    cuisine = message['MessageAttributes']['Cuisine']['StringValue']
    separator = ', '
    resOneName = restaurantDetails[0]['Item']['Name']
    resOneAdd = restaurantDetails[0]['Item']['Address']
    resTwoName = restaurantDetails[1]['Item']['Name']
    resTwoAdd = restaurantDetails[1]['Item']['Address']
    resThreeName = restaurantDetails[2]['Item']['Name']
    resThreeAdd = restaurantDetails[2]['Item']['Address']
    msg = 'Hello! Here are my {0} restaurant suggestions for {1} people, for {2} at {3} : 1. {4}, located at {5}, 2. {6}, located at {7},3. {8}, located at {9}. Enjoy your meal!'.format(cuisine,noOfPeople,date,time,resOneName,resOneAdd,resTwoName,resTwoAdd,resThreeName,resThreeAdd)
    return msg
    
def sendEmail(mailToSend):
    client = boto3.client("sns", region_name=REGION_NAME,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    client.publish(TopicArn='arn:aws:sns:us-east-1:304550935268:message', Message=mailToSend)
    
def deleteMsg(receipt_handle):
    sqs = boto3.client('sqs',region_name=REGION_NAME,aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)
    queue_url = 'https://sqs.us-east-1.amazonaws.com/304550935268/Q1'
    sqs.delete_message(QueueUrl=queue_url,ReceiptHandle=receipt_handle)

def lambda_handler(event, context):
    sqsQueueResponse = receiveMsgFromSqsQueue()
    if "Messages" in sqsQueueResponse.keys():
        for message in sqsQueueResponse['Messages']:
            cuisine = message['MessageAttributes']['Cuisine']['StringValue']
            restaurantIds = findRestaurantFromElasticSearch(cuisine)
            restaurantIds = random.sample(restaurantIds, 3)
            restaurantDetails = getRestaurantFromDb(restaurantIds)
            mailToSend = getMsgToSend(restaurantDetails,message)
            sendEmail(mailToSend)
            receipt_handle = message['ReceiptHandle']
            deleteMsg(receipt_handle)
