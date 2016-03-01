import unittest
import doctest
import server
from server import app, sorted_result, filtered_result, add_open_status
from unittest import TestCase
from twilio_api import convert_to_e164, send_thank_you_sms, send_reminder_sms
from google_api import is_open_now

# To test:
# python tests.py

# Coverage and Report:
# coverage run --source=. --omit=env* tests.py
# coverage report -m




restaurant_mock = {
                    "rating": 4.0,
                    "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png",
                    "review_count": 1983,
                    "name": "Ryoko's",
                    "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png",
                    "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
                    "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg",
                    "display_phone": "+1-415-775-1028",
                    "id": "ryokos-san-francisco",
                    "location": {
                        "city": "San Francisco",
                        "postal_code": "94102",
                        "address": [
                            "619 Taylor St"
                        ],
                        "coordinate": {
                            "latitude": 37.788008004427,
                            "longitude": -122.411782890558
                        },
                        "state_code": "CA"
                    }
                }





def load_tests(loader, tests, ignore):
    """Also run doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    # tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class TwilioUnitTestCase(TestCase):
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


class MockFlaskTests(TestCase):
    """Mock flask tests for Google and Yelp."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Make mocks

        restaurant_mock = {
                            "rating": 4.0,
                            "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png",
                            "review_count": 1983,
                            "name": "Ryoko's",
                            "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png",
                            "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
                            "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg",
                            "display_phone": "+1-415-775-1028",
                            "id": "ryokos-san-francisco",
                            "location": {
                                "city": "San Francisco",
                                "postal_code": "94102",
                                "address": [
                                    "619 Taylor St"
                                ],
                                "coordinate": {
                                    "latitude": 37.788008004427,
                                    "longitude": -122.411782890558
                                },
                                "state_code": "CA"
                            }
                        }

        def _mock_get_yelp_search_results(term, location, category_filter, limit):
            search_results = {
                "businesses": [
                    {
                        "rating": 4.0,
                        "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png",
                        "review_count": 1983,
                        "name": "Ryoko's",
                        "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png",
                        "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
                        "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg",
                        "display_phone": "+1-415-775-1028",
                        "id": "ryokos-san-francisco",
                        "location": {
                            "city": "San Francisco",
                            "postal_code": "94102",
                            "address": [
                                "619 Taylor St"
                            ],
                            "coordinate": {
                                "latitude": 37.788008004427,
                                "longitude": -122.411782890558
                            },
                            "state_code": "CA"
                        }
                    },
                    {
                        "rating": 4.5,
                        "rating_img_url": "https://s3-media2.fl.yelpcdn.com/assets/2/www/img/99493c12711e/ico/stars/v1/stars_4_half.png",
                        "review_count": 547,
                        "name": "Saru Sushi Bar",
                        "rating_img_url_small": "https://s3-media2.fl.yelpcdn.com/assets/2/www/img/a5221e66bc70/ico/stars/v1/stars_small_4_half.png",
                        "url": "http://www.yelp.com/biz/saru-sushi-bar-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
                        "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/5-ugy01zjSvudVsfdhmCsA/ms.jpg",
                        "display_phone": "+1-415-400-4510",
                        "id": "saru-sushi-bar-san-francisco",
                        "location": {
                            "city": "San Francisco",
                            "postal_code": "94114",
                            "country_code": "US",
                            "address": [
                                "3856 24th St"
                            ],
                            "coordinate": {
                                "latitude": 37.751706,
                                "longitude": -122.4288283
                            },
                            "state_code": "CA"
                        }
                    }
                ]
            }

            return search_results

        def _mock_is_open_now(keyword, location):
            return True

        self.old_get_yelp_search_results = server.yelp.search_query
        server.yelp.search_query = _mock_get_yelp_search_results

        self.old_is_open_now = server.is_open_now
        server.is_open_now = _mock_is_open_now

    def tearDown(self):
        """Do at the end of every test."""

        server.yelp.search_query = self.old_get_yelp_search_results
        server.is_open_now = self.old_is_open_now

    def test_add_open_status_with_mock(self):
        add_open_status(restaurant_mock)
        self.assertEqual(restaurant_mock["open_now"], "Open now")

    def test_add_wait_info_with_mock(restaurant):
        pass

    # def test_sorted_result_with_mock(result, sort_value):
    #     result = _mock_get_yelp_search_results["businesses"]
    #     self.assertEqual(sorted_result()

    # def test_filtered_result_with_mock(result, selected_filters):
    #     pass


if __name__ == '__main__':
    unittest.main()
