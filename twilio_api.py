import os
from twilio.rest import TwilioRestClient


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def send_sms(phone_number):
    client.messages.create(to=phone_number,
                           from_=TWILIO_NUMBER,
                           body="Hello there! Thanks for reporting your wait time!")
