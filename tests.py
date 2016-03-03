"""Test suite for NomNow! app."""

import unittest
import doctest
import server
from server import app
from process_results import sorted_result, filtered_result, add_wait_info, add_open_status
import process_results
from unittest import TestCase
from twilio_api import convert_to_e164, send_thank_you_sms, send_reminder_sms
from datetime import datetime
from model import connect_to_db, WaitTime, db

# To test:
# python tests.py

# Coverage and Report:
# coverage run --source=. --omit=env* tests.py
# coverage report -m


def load_tests(loader, tests, ignore):
    """Also run doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    return tests


class TwilioUnitTestCase(TestCase):
    """Unit tests on Twilio text messaging and phone number conversion."""

    def test_convert_to_e164(self):
        """Tests phone number conversion."""

        self.assertEqual(convert_to_e164("4235432224"), u'+14235432224')
        print "phone number conversion tested"

    def test_convert_to_e164_plus(self):
        """Tests phone number conversion with plus sign."""

        self.assertEqual(convert_to_e164("+14235432224"), u'+14235432224')
        print "phone number conversion with plus sign tested"

    def test_convert_to_e164_parens(self):
        """Tests phone number conversion with parens."""

        self.assertEqual(convert_to_e164("(423)543-2224)"), u'+14235432224')
        print "phone number conversion with parens tested"

    def test_convert_to_e164_period(self):
        """Tests phone number conversion with periods."""

        self.assertEqual(convert_to_e164("423.543.2224"), u'+14235432224')
        print "phone number conversion with periods tested"

    def test_convert_to_e164_dash(self):
        """Tests phone number conversion with dashes."""

        self.assertEqual(convert_to_e164("423-543-2224"), u'+14235432224')
        print "phone number conversion with dashes tested"

    def test_convert_to_e164_empty(self):
        """Tests phone number conversion for an empty string."""

        self.assertEqual(convert_to_e164(""), None)
        print "phone number conversion with empty string tested"

    def test_send_thank_you_sms(self):
        """Tests sending a thank you sms."""

        self.assertEqual(send_thank_you_sms("+14235432224", "Sanraku", "15 min"), None)
        print "send thank you sms tested"

    def test_send_thank_you_sms_invalid_number(self):
        """Tests sending a thank you sms to an invalid phone number."""

        self.assertEqual(send_thank_you_sms("+1231231223", "Sanraku", "15 min"), "Error")
        print "send thank you sms for invalid number tested"

    def test_send_reminder_sms(self):
        """Tests sending a reminder sms."""

        self.assertEqual(send_reminder_sms("+14235432224", "Sanraku", "15 min"), None)
        print "send reminder sms tested"

    def test_send_reminder_sms_invalid_number(self):
        """Tests sending a reminder sms to an invalid phone number."""

        self.assertEqual(send_reminder_sms("+1231231223", "Sanraku", "15 min"), "Error")
        print "send reminder sms for invalid number tested"


class SortedResultUnitTestCase(TestCase):
    """Unit tests on returning a sorted result."""

    def test_sorted_result_by_wait_time(self):
        """Tests returning sorted results by shortest wait time."""

        result = [{"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 15},
                  {"id": "ryokos-san-francisco", "quoted_wait_time": 1}]
        result_sorted = sorted_result(result, "wait_time")

        self.assertEqual(result_sorted[0]["quoted_wait_time"], 1)
        print "sorted result by wait time tested"

    def test_sorted_result_by_rating(self):
        """Tests returning sorted results by highest rating."""

        result = [{"id": "ryokos-san-francisco", "rating": 4.0},
                  {"id": "saru-sushi-bar-san-francisco", "rating": 4.5}]
        result_sorted = sorted_result(result, "rating")

        self.assertEqual(result_sorted[0]["rating"], 4.5)
        print "sorted result by rating tested"

    def test_sorted_result_by_review_count(self):
        """Tests returning sorted results by highest review count."""

        result = [{"id": "saru-sushi-bar-san-francisco", "review_count": 547},
                  {"id": "ryokos-san-francisco", "review_count": 1983}]
        result_sorted = sorted_result(result, "review_count")

        self.assertEqual(result_sorted[0]["review_count"], 1983)
        print "sorted result by review count tested"

    def test_sorted_result_by_recently_reported(self):
        """Tests returning sorted results by most recently reported wait time."""

        result = [{"id": "ryokos-san-francisco",
                   "timestamp_value": datetime(2016, 3, 1, 1, 27, 53, 200319),
                   "timestamp": "18 hours ago"},
                  {"id": "saru-sushi-bar-san-francisco",
                   "timestamp_value": datetime(2016, 3, 1, 20, 5, 55, 643065),
                   "timestamp": "2 minutes ago"}]
        result_sorted = sorted_result(result, "recently_reported")

        self.assertEqual(result_sorted[0]["timestamp_value"], datetime(2016, 3, 1, 20, 5, 55, 643065))
        print "sorted result by recently reported tested"


class FilteredResultUnitTestCase(TestCase):
    """Unit tests on returning a filtered result."""

    def test_filtered_result_by_open_now(self):
        """Tests returning filtered result by open now status."""

        result = [{"id": "ryokos-san-francisco", "open_now": "Closed"},
                  {"id": "saru-sushi-bar-san-francisco", "open_now": "Open now"}]
        result_filtered = filtered_result(result, ["open_now"])

        self.assertIn({"id": "saru-sushi-bar-san-francisco", "open_now": "Open now"}, result_filtered)
        self.assertNotIn({"id": "ryokos-san-francisco", "open_now": "Closed"}, result_filtered)
        print "filtered result by open now tested"

    def test_filtered_result_by_15_min_wait(self):
        """Tests returning filtered result by <=15 min wait."""

        result = [{"id": "sanraku-san-francisco-2", "quoted_wait_time": 10},
                  {"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 15},
                  {"id": "ryokos-san-francisco", "quoted_wait_time": 20}]
        result_filtered = filtered_result(result, ["15_min_wait"])

        self.assertIn({"id": "sanraku-san-francisco-2", "quoted_wait_time": 10}, result_filtered)
        self.assertIn({"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 15}, result_filtered)
        self.assertNotIn({"id": "ryokos-san-francisco", "quoted_wait_time": 20}, result_filtered)
        print "filtered result by <=15 min wait tested"

    def test_filtered_result_by_30_min_wait(self):
        """Tests returning filtered result by <=30 min wait."""

        result = [{"id": "sanraku-san-francisco-2", "quoted_wait_time": 10},
                  {"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 30},
                  {"id": "ryokos-san-francisco", "quoted_wait_time": 45}]
        result_filtered = filtered_result(result, ["30_min_wait"])

        self.assertIn({"id": "sanraku-san-francisco-2", "quoted_wait_time": 10}, result_filtered)
        self.assertIn({"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 30}, result_filtered)
        self.assertNotIn({"id": "ryokos-san-francisco", "quoted_wait_time": 45}, result_filtered)
        print "filtered result by <=30 min wait tested"

    def test_filtered_result_by_45_min_wait(self):
        """Tests returning filtered result by <=45 min wait."""

        result = [{"id": "sanraku-san-francisco-2", "quoted_wait_time": 10},
                  {"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 45},
                  {"id": "ryokos-san-francisco", "quoted_wait_time": 60}]
        result_filtered = filtered_result(result, ["45_min_wait"])

        self.assertIn({"id": "sanraku-san-francisco-2", "quoted_wait_time": 10}, result_filtered)
        self.assertIn({"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 45}, result_filtered)
        self.assertNotIn({"id": "ryokos-san-francisco", "quoted_wait_time": 60}, result_filtered)
        print "filtered result by <=45 min wait tested"

    def test_filtered_result_by_60_min_wait(self):
        """Tests returning filtered result by <=60 min wait."""

        result = [{"id": "sanraku-san-francisco-2", "quoted_wait_time": 10},
                  {"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 60},
                  {"id": "ryokos-san-francisco", "quoted_wait_time": 120}]
        result_filtered = filtered_result(result, ["60_min_wait"])

        self.assertIn({"id": "sanraku-san-francisco-2", "quoted_wait_time": 10}, result_filtered)
        self.assertIn({"id": "saru-sushi-bar-san-francisco", "quoted_wait_time": 60}, result_filtered)
        self.assertNotIn({"id": "ryokos-san-francisco", "quoted_wait_time": 120}, result_filtered)
        print "filtered result by <=60 min wait tested"


class AddOpenStatusTrueTestCase(TestCase):
    """Unit test for adding open status with a mock True value for is open now."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        def _mock_is_open_now_true(keyword, location):
            return True

        self._old_is_open_now = process_results.is_open_now
        # Bind is_open_now to _mock_is_open_now_true
        process_results.is_open_now = _mock_is_open_now_true

    def tearDown(self):
        """Do at the end of every test."""

        # Rebind to original is_open_now
        process_results.is_open_now = self._old_is_open_now

    def test_add_open_status_with_mock_true(self):
        """Tests adding open status ("Open now") to restaurant dictionary."""

        restaurant_mock = {"rating": 4.0, "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png", "review_count": 1983, "name": "Ryoko's", "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png", "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg", "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg", "display_phone": "+1-415-775-1028", "id": "ryokos-san-francisco", "location": {"city": "San Francisco", "postal_code": "94102", "address": ["619 Taylor St"], "coordinate": {"latitude": 37.788008004427, "longitude": -122.411782890558}, "state_code": "CA"}}
        add_open_status(restaurant_mock)
        self.assertEqual(restaurant_mock["open_now"], "Open now")
        print"add open status ('Open now') for true value tested"


class AddOpenStatusFalseTestCase(TestCase):
    """Unit test for adding open status with mock False value for is open now."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        def _mock_is_open_now_false(keyword, location):
            return False

        self._old_is_open_now = process_results.is_open_now
        # Bind is_open_now to _mock_is_open_now_false
        process_results.is_open_now = _mock_is_open_now_false

    def tearDown(self):
        """Do at the end of every test."""

        # Rebind to original is_open_now
        process_results.is_open_now = self._old_is_open_now

    def test_add_open_status_with_mock_false(self):
        """Tests adding open status ("Closed") to restaurant dictionary."""

        restaurant_mock = {"rating": 4.0, "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png", "review_count": 1983, "name": "Ryoko's", "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png", "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg", "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg", "display_phone": "+1-415-775-1028", "id": "ryokos-san-francisco", "location": {"city": "San Francisco", "postal_code": "94102", "address": ["619 Taylor St"], "coordinate": {"latitude": 37.788008004427, "longitude": -122.411782890558}, "state_code": "CA"}}
        add_open_status(restaurant_mock)
        self.assertEqual(restaurant_mock["open_now"], "Closed")
        print"add open status ('Closed') for false value tested"


class AddOpenStatusNoneTestCase(TestCase):
    """Unit test for adding open status with mock None value for is open now."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        def _mock_is_open_now_none(keyword, location):
            return None

        self._old_is_open_now = process_results.is_open_now
        # Bind is_open_now to _mock_is_open_now_false
        process_results.is_open_now = _mock_is_open_now_none

    def tearDown(self):
        """Do at the end of every test."""

        # Rebind to original is_open_now
        process_results.is_open_now = self._old_is_open_now

    def test_add_open_status_with_mock_none(self):
        """Tests adding open status ("Open now unknown") to restaurant dictionary."""

        restaurant_mock = {"rating": 4.0, "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png", "review_count": 1983, "name": "Ryoko's", "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png", "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg", "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg", "display_phone": "+1-415-775-1028", "id": "ryokos-san-francisco", "location": {"city": "San Francisco", "postal_code": "94102", "address": ["619 Taylor St"], "coordinate": {"latitude": 37.788008004427, "longitude": -122.411782890558}, "state_code": "CA"}}
        add_open_status(restaurant_mock)
        self.assertEqual(restaurant_mock["open_now"], "Open now unknown")
        print"add open status ('Open now unknown') for none value tested"


class AddWaitInfoTestCase(TestCase):
    """Unit test for add wait info with test database."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_add_wait_info_true(self):
        """Tests adding wait info from database to a matching restaurant's dictionary."""

        new_wait = WaitTime(yelp_id="ryokos-san-francisco",
                            party_size=3,
                            parties_ahead=10,
                            quoted_minutes=120,
                            timestamp=datetime(2016, 3, 2, 1, 27, 53, 200319))
        db.session.add(new_wait)
        db.session.commit()

        restaurant_mock = {"id": "ryokos-san-francisco", "name": "Ryoko's"}
        add_wait_info(restaurant_mock)
        self.assertEqual(restaurant_mock["quoted_wait_time"], 120)
        self.assertEqual(restaurant_mock["timestamp_value"], datetime(2016, 3, 2, 1, 27, 53, 200319))
        print "add wait info for matching restaurant tested"

    def test_add_wait_info_false(self):
        """Tests adding wait info to a restaurant's dictionary with no matching wait info from database."""

        restaurant_mock = {"id": "little-star-pizza-san-francisco", "name": "Little Star Pizza"}
        add_wait_info(restaurant_mock)
        self.assertEqual(restaurant_mock["quoted_wait_time"], "Not available")
        self.assertEqual(restaurant_mock["timestamp_value"], datetime(2000, 2, 2))
        print "add wait info for no match tested"

    def test_add_wait_info_multiple(self):
        """Tests adding the most recent wait info to a restaurant's dictionary for multiple matches in the database."""

        wait1 = WaitTime(yelp_id="ryokos-san-francisco",
                         party_size=3,
                         parties_ahead=10,
                         quoted_minutes=120,
                         timestamp=datetime(2016, 3, 2, 1, 27, 53, 200319))

        wait2 = WaitTime(yelp_id="ryokos-san-francisco",
                         party_size=4,
                         parties_ahead=2,
                         quoted_minutes=60,
                         timestamp=datetime(2016, 3, 1, 1, 26, 00, 200319))

        db.session.add_all([wait1, wait2])
        db.session.commit()

        restaurant_mock = {"id": "ryokos-san-francisco", "name": "Ryoko's"}
        add_wait_info(restaurant_mock)
        self.assertEqual(restaurant_mock["quoted_wait_time"], 120)
        self.assertEqual(restaurant_mock["timestamp_value"], datetime(2016, 3, 2, 1, 27, 53, 200319))
        print "add wait info with multiple restaurants tested"

    def test_add_wait_info_null(self):
        """Tests adding wait info with null values from database to a matching restaurant's dictionary."""

        new_wait = WaitTime(yelp_id="ryokos-san-francisco",
                            quoted_minutes=120,
                            timestamp=datetime(2016, 3, 2, 1, 27, 53, 200319))
        db.session.add(new_wait)
        db.session.commit()

        restaurant_mock = {"id": "ryokos-san-francisco", "name": "Ryoko's"}
        add_wait_info(restaurant_mock)
        self.assertEqual(restaurant_mock["party_size"], "N/A")
        self.assertEqual(restaurant_mock["parties_ahead"], "N/A")
        print "add wait info with null values for matching restaurant tested"


class DatabaseTestCase(TestCase):
    """Test adding record with nullable fields"""


class IntegerationTestCase(TestCase):
    """Integration tests on Flask server."""

    def setUp(self):
        """Do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()

        print "setUp ran for testing flask server."

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_homepage(self):
        """Tests result of homepage."""

        result = self.client.get("/")
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        print "homepage tested"

    def test_report(self):
        """Tests result of wait time form page."""

        result = self.client.get("/report")
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<h2>Report Your Wait Time</h2>', result.data)
        print "display report form tested"

    def test_process_report(self):
        """Tests if wait time form will process the report properly."""

        result = self.client.post("/process_report",
                                  data={"restaurant_name": "Sanraku",
                                        "location": "704 Sutter St, San Francisco, CA 94109, United States",
                                        "quoted_hr": 1,
                                        "quoted_min": 30},
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn('Thanks for reporting your wait time!', result.data)
        print "process report tested"


# class MockFlaskTests(TestCase):
#     """Mock flask tests for Yelp."""

#     def setUp(self):
#         """Do before every test."""

#         # Get the Flask test client
#         self.client = app.test_client()

#         # Show Flask errors that happen during tests
#         app.config['TESTING'] = True

#         # Make mocks

#         def _mock_get_yelp_search_results(term, location, category_filter, limit):
#             search_results = {
#                 "businesses": [
#                     {
#                         "rating": 4.0,
#                         "rating_img_url": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/c2f3dd9799a5/ico/stars/v1/stars_4.png",
#                         "review_count": 1983,
#                         "name": "Ryoko's",
#                         "rating_img_url_small": "https://s3-media4.fl.yelpcdn.com/assets/2/www/img/f62a5be2f902/ico/stars/v1/stars_small_4.png",
#                         "url": "http://www.yelp.com/biz/ryokos-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
#                         "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/El1KekyVFSqrtKLAyjcfNA/ms.jpg",
#                         "display_phone": "+1-415-775-1028",
#                         "id": "ryokos-san-francisco",
#                         "location": {
#                             "city": "San Francisco",
#                             "postal_code": "94102",
#                             "address": [
#                                 "619 Taylor St"
#                             ],
#                             "coordinate": {
#                                 "latitude": 37.788008004427,
#                                 "longitude": -122.411782890558
#                             },
#                             "state_code": "CA"
#                         }
#                     },
#                     {
#                         "rating": 4.5,
#                         "rating_img_url": "https://s3-media2.fl.yelpcdn.com/assets/2/www/img/99493c12711e/ico/stars/v1/stars_4_half.png",
#                         "review_count": 547,
#                         "name": "Saru Sushi Bar",
#                         "rating_img_url_small": "https://s3-media2.fl.yelpcdn.com/assets/2/www/img/a5221e66bc70/ico/stars/v1/stars_small_4_half.png",
#                         "url": "http://www.yelp.com/biz/saru-sushi-bar-san-francisco?utm_campaign=yelp_api&utm_medium=api_v2_search&utm_source=6XuCRI2pZ5pIvcWc9SI3Yg",
#                         "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/5-ugy01zjSvudVsfdhmCsA/ms.jpg",
#                         "display_phone": "+1-415-400-4510",
#                         "id": "saru-sushi-bar-san-francisco",
#                         "location": {
#                             "city": "San Francisco",
#                             "postal_code": "94114",
#                             "country_code": "US",
#                             "address": [
#                                 "3856 24th St"
#                             ],
#                             "coordinate": {
#                                 "latitude": 37.751706,
#                                 "longitude": -122.4288283
#                             },
#                             "state_code": "CA"
#                         }
#                     }
#                 ]
#             }

#             return search_results

#         self.old_get_yelp_search_results = server.yelp.search_query
#         server.yelp.search_query = _mock_get_yelp_search_results

#     def tearDown(self):
#         """Do at the end of every test."""

#         server.yelp.search_query = self.old_get_yelp_search_results


if __name__ == '__main__':
    unittest.main()
