import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('lexv2-runtime', region_name='us-east-1')
    response = client.recognize_text(
        botId='',
        botAliasId='',
        localeId = 'en_US',
        sessionId ='12345',
        # userId= 'bot',
        # sessionAttributes={
            # },
        # requestAttributes={
        # },
        # intentName='GreetingIntent'
        text = event["messages"][0]["unstructured"]["text"]
    )
    
    return {
        'statusCode': 200,
        'messages':[{
                'type': 'unstructured',
                'unstructured': {'text': response['messages'][0]['content']}
                }]
    }
