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
Users can search for nearby restaurants or by cuisine.
<img src="/static/img/nomnow_ss.png" alt="NomNow!">

### Results
The response from the server renders a map and list of restaurants with the most recent user-reported wait times. Wait time information (reported wait time, party size, parties ahead) is user reported and stored in a PostgreSQL database, where the most recent wait time is fetched for dispaly on the results page. Rating and reviews come from the Yelp API and current open status comes from the Google Places API. The Google Maps API is used to show the location of each restaurant with respect to the user's current location.
<img src="/static/img/results_list_map.gif" alt="Results">

#### Sort and Filter
For more tailored results, users can sort by most recently reported wait time, shortest wait time, highest rating, and most reviews, and filter by open now and wait time (&le; 15min, 30min, 45min, 60min). Pusheen cat can keep users company while the server returns the response.
<img src="/static/img/sort_filter.gif" alt="Sort and Filter">

### Report Your Wait Time
When users report their wait time, the autocomplete feature of the Places Library in Google Maps Javascript API allow for a type-ahead-search to find their restaurant at their location.
<img src="/static/img/report_wait.gif" alt="Report">

### Text Reminder
In addition to reporting wait time, users can enter their phone number to receive text notifications for reminders when their wait time is up, allowing for more control over their time instead of hovering outside a restaurant. This is accomplished using the Twilio API for text messaging capabilities and the Timer class of the Threading module in the Python Standard Library. The Timer object excutes sending of the reminder text after the specified interval of the reported wait time has elapsed.
<img src="/static/img/thankyou_ss.png" alt="Thank you text">
<img src="/static/img/reminder_ss.png" alt="Reminder text">


## Author
Annie He 
https://www.linkedin.com/in/annieheyt