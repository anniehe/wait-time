import os
import twilio
from twilio.rest import TwilioRestClient
import phonenumbers


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def send_thank_you_sms(phone_number, restaurant_name, quoted_time):
    """Sends thank you text message to the user."""

    body = ("Hello, there! Thanks for reporting your wait time for %s. "
            "We know you want to nom now, but just remember, good things "
            "happen to those who wait. We'll send you a reminder when "
            "your quoted wait time of %s is up. Hang in there!") % (restaurant_name, quoted_time)

    try:
        client.messages.create(to=phone_number,
                               from_=TWILIO_NUMBER,
                               body=body)

    except twilio.TwilioRestException as e:
        print e
        return "Error"


def send_reminder_sms(phone_number, quoted_time, restaurant_name):
    """Sends reminder text message to the user."""

    body = ("It's time to nom now! You waited %s already. You should "
            "check if your table is ready at %s. Enjoy your nomming! "
            "Nom nom nom!") % (quoted_time, restaurant_name)

    try:
        client.messages.create(to=phone_number,
                               from_=TWILIO_NUMBER,
                               body=body)

    except twilio.TwilioRestException as e:
        print e
        return "Error"


def convert_to_e164(raw_phone):
    """Formats phone numbers to E.164 format for Twilio.

        >>> convert_to_e164("4235432224")
        u'+14235432224'

        >>> convert_to_e164("(423)543-2224")
        u'+14235432224'

        >>> convert_to_e164("423.543.2224")
        u'+14235432224'

    """

    if not raw_phone:
        return

    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # If no country code information present, assume it's a US number
        parse_type = "US"

    phone_representation = phonenumbers.parse(raw_phone, parse_type)

    return phonenumbers.format_number(phone_representation,
                                      phonenumbers.PhoneNumberFormat.E164)
