from yelpapi import YelpAPI
import os
import pprint


consumer_key = os.environ['YELP_CONSUMER_KEY']
consumer_secret = os.environ['YELP_CONSUMER_SECRET']
token = os.environ['YELP_TOKEN']
token_secret = os.environ['YELP_TOKEN_SECRET']

yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)


def yelp_search(term, location='San Francisco'):
    search_results = yelp_api.search_query(term=term, location=location)

    # pprint.pprint(search_results)

    # name = search_results['businesses'][0]['name']
    # print "NAME", name

    # business_id = search_results['businesses'][0]['id']
    # print "BUSINESS ID", business_id

    # review_count = search_results['businesses'][0]['review_count']
    # print "REVIEW COUNT", review_count

    # rating = search_results['businesses'][0]['rating']
    # print "RATING", rating

    # rating_image = search_results['businesses'][0]['rating_img_url']
    # print "RATING IMAGE", rating_image

    # location = search_results['businesses'][0]['location']['display_address']

    return search_results
