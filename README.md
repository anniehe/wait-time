# NomNow!
NomNow! is a user-driven web app that provides the ability to make informed decisions on choosing a restaurant based on current wait times, popularity, and proximity. Time is precious and unexpected long waits at restaurants can be frustrating. NomNow! aims to make the process of choosing a restaurant simpler so you can nom now!

## Technologies Used
* Python
* Flask
* PostgresSQL
* SQLAlchemy
* JavaScript
* jQuery
* Jinja2
* Bootstrap
* HTML/CSS
* Yelp API
* Google Places API
* Google Maps API
* Twilio API

## How NomNow! Works

### Search
Users can search for a restaurant or cuisine at their location of choice.
<img src="/static/img/nomnow_ss.png" alt="NomNow!">

### Results
The response from the server renders a map and list of restaurants with the most recent user-reported wait times. NomNow! relies on data from the Yelp API, Google Places API, and user-reported wait time information stored in a PostgreSQL database. The Yelp API is queried with the search terms and returns the 10 best matched restaurants. For each restaurant in the result, NomNow! queries the Google Places API for the restaurant's current open status and the PostgreSQL database to fetch the most recent wait time information for the restaurant, if available. The Google Maps API is used to show the location of each restaurant with respect to the user's current location. Users can weigh the factors of reported wait time, ratings, reviews, and proximity to choose a restaurant.  
<img src="/static/img/results_list_map.gif" alt="Results">

#### Sort and Filter
For more tailored results, users can sort by most recently reported, shortest wait time, highest rating, and most reviews, and filter by open now and wait time (&le; 15min, 30min, 45min, 60min). Pusheen cat can keep users company while the server returns the response.
<img src="/static/img/sort_filter.gif" alt="Sort and Filter">

### Reporting Wait Time
When users report their wait time, the autocomplete feature of the Places Library in Google Maps Javascript API allow for a type-ahead-search to find their restaurant at the correct location.
<img src="/static/img/report_wait.gif" alt="Report">

### Text Reminder
In addition to reporting wait time, users can enter their phone number to receive text notifications for reminders when their wait time is up, allowing for more control over their time instead of hovering outside a restaurant. This is accomplished using the Twilio API and the Timer class of the Threading module in the Python Standard Library. The Timer object executes the sending of the reminder text after the specified interval of the quoted wait time has elapsed.
<img src="/static/img/thankyou_ss.png" alt="Thank you text">
<img src="/static/img/reminder_ss.png" alt="Reminder text">

## Version 2.0
* Incorporate Celery (asynchronous task queue and task scheduling) and Redis (message broker) to handle the execution of sending text reminders after the quoted wait time has elapsed
* Improve load time performance
* Implement Chart.js to visualize the flow of wait time throughout the day

## Author
Annie He 
https://www.linkedin.com/in/annieheyt