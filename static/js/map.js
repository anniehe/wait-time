function initMap() {
  // Instantiate a map object and specify DOM element for displaying map
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 37.7886334, lng: -122.4114752},
    zoom: 10
  });

  var infoWindow = new google.maps.InfoWindow({map: map});

  var key, restaurant, yelpId, name, image, ratingImage, reviewCount;
  var address, city, stateCode, zipCode, phone, status;
  var html, marker, locationLat, locationLng;

  // Access each restaurant's info in the resultObject
  for (key in resultObject['result']) {

    restaurant = resultObject['result'][key];
    yelpId = resultObject['result'][key]['id'];
    name = resultObject['result'][key]['name'];
    image = resultObject['result'][key]['image_url'];
    ratingImage = resultObject['result'][key]['rating_img_url_small'];
    reviewCount = resultObject['result'][key]['review_count'];

    address = resultObject['result'][key]['location']['address'][0];
    city = resultObject['result'][key]['location']['city'];
    stateCode = resultObject['result'][key]['location']['state_code'];
    zipCode = resultObject['result'][key]['location']['postal_code'];
    phone = resultObject['result'][key]['display_phone'];
    status = resultObject['result'][key]['open_now'];

    locationLat = resultObject['result'][key]['location']['coordinate']['latitude'];
    locationLng = resultObject['result'][key]['location']['coordinate']['longitude'];

    // Define the markers for each restaurant
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(locationLat, locationLng),
        map: map,
        title: name
    });

    // Define the content of the infoWindow for each restaurant
    html = (
      '<div>' +
        '<img src="' + image + '" alt="restaurant">' +
        '<h3><b>' + name + '</b></h3>' +
        '<p><img src="' + ratingImage + '" alt="rating"> ' + reviewCount + ' Reviews on Yelp</p>' +
        '<p>' + address + '<br>' + city + ', ' + stateCode + ' ' + zipCode + '</p>' +
        '<p>' + phone + '</p>' +
        '<p><i>' + status + '</i></p>' +
      '</div>');

    bindInfoWindow(marker, map, infoWindow, html);
    jumpToResult(marker, yelpId);
  }

  // On mouseover, the content for the marker is set and the infoWindow is opened.
  // On mouseout, the infoWindow is closed. 
  function bindInfoWindow(marker, map, infoWindow, html) {
    google.maps.event.addListener(marker, 'mouseover', function() {
      infoWindow.setContent(html);
      infoWindow.open(map, marker);
    });
    google.maps.event.addListener(marker, 'mouseout', function() {
      infoWindow.close();
    });
  }

  // Clicking the marker will jump to the corresponding restaurant on the results page.
  function jumpToResult(marker, anchor) {
    google.maps.event.addListener(marker, 'click', function() {
      window.location = "#" + anchor;
    });
  }

  // console.log(resultObject);
  // console.log(resultObject['result'][0]);
  // console.log(resultObject['result'][0]['id']);
  // console.log(resultObject['result'][0]['location']['address'][0]);
  // console.log(resultObject['result'][0]['location']['coordinate']['latitude']);
  // console.log(resultObject['result'][0]['location']['coordinate']['longitude']);

  // Try HTML5 geolocation
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };

      infoWindow.setPosition(pos);
      infoWindow.setContent('Current location.');
      map.setCenter(pos);
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

// Handles Geolocation error
function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
}

// google.maps.event.addDomListener(window, 'load', initMap);