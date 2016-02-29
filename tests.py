import unittest
import doctest
import server
from twilio_api import convert_to_e164, send_thank_you_sms, send_reminder_sms

# To test:
# python tests.py

# Coverage and Report:
# coverage run --source=. --omit=env* tests.py
# coverage report -m


def load_tests(loader, tests, ignore):
    """Also run doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    # tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class TwilioUnitTestCase(unittest.TestCase):
    """Unit tests on Twilio."""

    def test_convert_to_e164(self):
        self.assertEqual(convert_to_e164("4235432224"), u'+14235432224')

    def test_convert_to_e164_plus(self):
        self.assertEqual(convert_to_e164("+14235432224"), u'+14235432224')

    def test_convert_to_e164_parens(self):
        self.assertEqual(convert_to_e164("(423)543-2224)"), u'+14235432224')

    def test_convert_to_e164_period(self):
        self.assertEqual(convert_to_e164("423.543.2224"), u'+14235432224')

    def test_convert_to_e164_dash(self):
        self.assertEqual(convert_to_e164("423-543-2224"), u'+14235432224')

    def test_convert_to_e164_empty(self):
        self.assertEqual(convert_to_e164(""), None)

    def test_send_thank_you_sms(self):
        self.assertEqual(send_thank_you_sms("+14235432224", "Sanraku", "15 min"), None)

    def test_send_thank_you_sms_invalid_number(self):
        self.assertEqual(send_thank_you_sms("+1231231223", "Sanraku", "15 min"), "Error")

    def test_send_reminder_sms(self):
        self.assertEqual(send_reminder_sms("+14235432224", "Sanraku", "15 min"), None)

    def test_send_reminder_sms_invalid_number(self):
        self.assertEqual(send_reminder_sms("+1231231223", "Sanraku", "15 min"), "Error")


class MyAppIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        """Do before every test."""

        self.client = server.app.test_client()

        def _mock_add_open_status(restaurant):
            pass

        def _mock_add_wait_info(restaurant):
            pass

        def _mock_sorted_result(result, sort_value):
            pass

        def _mock_filtered_result(result, selected_filters):
            pass

        def _mock_is_open_now(keyword, location):
            pass

        def _mock_get_yelp_search_results():
            pass

        self._old_add_open_status = server.add_open_status
        server.add_open_status = _mock_add_open_status

    def tearDown(self):
        """Do at the end of every test."""
        server.add_open_status = self._old_state_to_code


if __name__ == '__main__':
    unittest.main()
