function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 37.7886334, lng: -122.4114752},
    zoom: 12
  });

  var infoWindow = new google.maps.InfoWindow({map: map});

  var key, restaurant, name, locationLat, locationLng, marker, html;
  var address, phone, image;
  var city, stateCode, zipCode;

  for (key in resultObject['result']) {
    restaurant = resultObject['result'][key];
    name = resultObject['result'][key]['name'];
    locationLat = resultObject['result'][key]['location']['coordinate']['latitude'];
    locationLng = resultObject['result'][key]['location']['coordinate']['longitude'];
    address = resultObject['result'][key]['location']['address'][0];
    city = resultObject['result'][key]['location']['city'];
    // stateCode = resultObject['result'][key]['location']['state_code'];
    // zipCode = resultObject['result'][key]['location']['postal_code'];
    phone = resultObject['result'][key]['display_phone'];
    image = resultObject['result'][key]['image_url'];

    // Define the markers for each restaurant
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(locationLat, locationLng),
        map: map,
        title: name
    });

    // Define the content of the infoWindow
    html = (
      '<div>' +
        '<img src="' + image + '" alt="restaurant">' +
        '<p><b>' + name + '</b></p>' +
        '<p>' + address + '</p>' +
        '<p>' + phone + '</p>' +
        // '<p>' + city + ', ' + stateCode + ' ' + zipCode + '</p>' +
      '</div>');

    bindInfoWindow(marker, map, infoWindow, html);
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

  // console.log(resultObject);
  // console.log(resultObject['result'][0]);
  // console.log(resultObject['result'][0]['id']);
  // console.log(resultObject['result'][0]['location']['address'][0]);
  // console.log(resultObject['result'][0]['location']['coordinate']['latitude']);
  // console.log(resultObject['result'][0]['location']['coordinate']['longitude']);

  // Try HTML5 geolocation.
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };

      infoWindow.setPosition(pos);
      infoWindow.setContent('Location found.');
      map.setCenter(pos);
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
}

// google.maps.event.addDomListener(window, 'load', initMap);