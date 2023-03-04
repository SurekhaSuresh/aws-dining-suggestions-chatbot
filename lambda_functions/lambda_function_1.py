import json
import boto3
import re
import datetime
import random
import math
from zoneinfo import ZoneInfo
import dateutil

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def isvalid_date(date):
    print(date)
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

        
def validate_time(time):
    
    currentTime = datetime.datetime.now(ZoneInfo("America/New_York"))
    currentHour = currentTime.hour
    currentMinute = currentTime.minute
    if len(time) == 5:
        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        
        if not (math.isnan(hour) or math.isnan(minute)):

            if hour == currentHour and minute < currentMinute:
                return False
            if hour < currentHour and minute < currentMinute:
                return False
            else: 
                return True
        else:
            return False
        return True
    return True
    
def validate_people(people):
    
    ppl = people.get("value").get("originalValue")
    if int(ppl) < 1 or int(ppl) > 20:
        return False
    else:
        return True
    
def save_to_sqs(city_name,cuisine,people,time,number,date):
    
    sqs_client = boto3.client('sqs')
    queue_url = "https://sqs.us-east-1.amazonaws.com/304550935268/Q1"

    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageAttributes={
            'Location': {
                'DataType': 'String',
                'StringValue': city_name
            },
            'Cuisine': {
                'DataType': 'String',
                'StringValue': cuisine
            },
            'People': {
                'DataType': 'Number',
                'StringValue': "{}".format(people)
            },
            'Date': {
                'DataType': 'String',
                'StringValue': "{}".format(date)
            },
            'Time': {
                'DataType': 'String',
                'StringValue': time
            },
            'ContactNumber': {
                'DataType': 'Number',
                'StringValue': "{}".format(number)
            }
        },
        MessageBody=(
            'Values filled in by the customer.'
        )
    )

    front_response = "We have received your request. You will receive a text shortly"
    return {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": front_response
            }
        }
    }
def lambda_handler(event, context):
    # TODO implement
    print(event)
    # intent_name = event.get("proposedNextState").get("intent").get("name")
    intent_name = event.get("interpretations")[0].get("intent").get("name")

    time_validate = 0

    if intent_name == "GreetingIntent":
        response = "Hello, I am a Dining Concierge Chatbot. I can suggest you restaurants based on their rating and location, how can I help you today?"
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled",
                    "message": {
                    "contentType": "PlainText",
                    "content": response
                    }
                }
            }
        }
                

    if intent_name == "ThankYouIntent":

        response = "I am glad that I could be of help, have a nice day!"
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled",
                    "message": {
                    "contentType": "PlainText",
                    "content": response
                    }
                }
            }
        }

    if intent_name == "DiningSuggestionsIntent":

        city_name = event.get("interpretations")[0].get("intent").get("slots").get("Location")
        cuisine = event.get("interpretations")[0].get("intent").get("slots").get("Cuisine")
        print("The Cuisine is {}".format(cuisine))
        time = event.get("interpretations")[0].get("intent").get("slots").get("DiningTime")
        date = event.get("interpretations")[0].get("intent").get("slots").get("DiningDate")
        people = event.get("interpretations")[0].get("intent").get("slots").get("peoplecount")
        number = event.get("interpretations")[0].get("intent").get("slots").get("phone")
        # elicit = event.get("proposedNextState").get("dialogAction").get("slotToElicit")
        date_now = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(ZoneInfo("America/New_York")))
        date_current = date_now.split(" ")[0].split("-")
        date_today = datetime.datetime(int(date_current[0]), int(date_current[1]), int(date_current[2])).date()
        if city_name is None:
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "Location",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "What area would you like to dine in? You can enter any of the boroughs in New York City - Manhattan, Brooklyn, Queens, etc."
                        }
                    ]
                }

        elif people is None:
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "peoplecount",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "How many people are planning to join you (including you)? Please Note - Due to the COVID guidelines, no restaurant can seat more than 20 people at a time"
                        }
                    ]
                }
        
        elif((people is not None) and  (not validate_people(people))):
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "peoplecount",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "You entered a number higher than 20, please enter a number less than 20. How many people intend to join you (including you)? "
                        }
                    ]
                }
            
        elif date is None: 
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "DiningDate",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "What date would you like to be seated. Please enter the date (eg. 5 March 2022)?"
                        }
                    ]
                }
                

        elif date is not None and (not isvalid_date(date.get("value").get("originalValue"))):
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "DiningDate",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "The date you entered is invalid. The date should be greater than today's date."
                        }
                    ]
                }
 
            
        elif time is None:
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "DiningTime",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "At what time would you like to be seated?"
                        }
                    ]
                }
 
            
        elif time is not None and not validate_time(time.get("value").get("originalValue")) and ((not isvalid_date(date.get("value").get("originalValue")))):
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "DiningTime",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "The time you entered is not valid. Please enter a valid time."
                        }
                    ]
                }
 
                    
                
        elif cuisine is None:
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "Cuisine",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "What cuisine would you like to try? Your cuisine options for today are - Chinese, Japanese, Italian, American, Mexican, Korean, Indian, and French."
                        }
                    ]
                }
 
        elif number is None:
            return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "phone",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "What is your contact number?(Please enter 10 digit US mobile number)"
                        }
                    ]
                }
 

        elif number is not None:
            PHONE_REGEX = re.compile(r'[0-9]{10}')
            print(number)
            if not PHONE_REGEX.match(number.get("value").get("originalValue")):
                return {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": "phone",
                            "type": "ElicitSlot",
                        },
                        "intent": {
                            "name": "DiningSuggestionsIntent",
                            "slots": {
        "Cuisine": cuisine,
        "DiningDate": date,
        "phone": number,
        "peoplecount": people,
        "DiningTime": time,
        "Location": city_name
      }
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "You have entered an invalid contact number. Please enter 10 digit US mobile number."
                        }
                    ]
                }
                
 
            else:
                return save_to_sqs(city_name.get("value").get("originalValue"),cuisine.get("value").get("originalValue"),people.get("value").get("originalValue"),time.get("value").get("originalValue"),number.get("value").get("originalValue"),date.get("value").get("originalValue"))
                
                
        else:
            return save_to_sqs(city_name.get("value").get("originalValue"),cuisine.get("value").get("originalValue"),people.get("value").get("originalValue"),time.get("value").get("originalValue"),number.get("value").get("originalValue"),date.get("value").get("originalValue"))
            
