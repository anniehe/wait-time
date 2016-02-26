import os
from twilio.rest import TwilioRestClient


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def send_thank_you_sms(phone_number, restaurant_name, quoted_time):
    body = ("Hello, there! Thanks for reporting your wait time for %s. "
            "We know you want to nom now, but just remember, good things "
            "happen to those who wait. We'll send you a reminder when "
            "your quoted wait time of %s is up. Hang in there!") % (restaurant_name, quoted_time)

    client.messages.create(to=phone_number,
                           from_=TWILIO_NUMBER,
                           body=body)


def send_reminder_sms(phone_number, quoted_time, restaurant_name):
    body = ("It's time to nom now! You waited %s already. You should "
            "check if your table is ready at %s. Enjoy your nomming! "
            "Nom nom nom!") % (quoted_time, restaurant_name)

    client.messages.create(to=phone_number,
                           from_=TWILIO_NUMBER,
                           body=body)
