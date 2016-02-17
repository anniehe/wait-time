function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 37.7886334, lng: -122.4114752},
    zoom: 12
  });

  var infoWindow = new google.maps.InfoWindow({map: map});

  var key, restaurant, name, locationLat, locationLng, marker;

  for (key in resultObject['result']) {
    restaurant = resultObject['result'][key];
    name = resultObject['result'][key]['name'];
    locationLat = resultObject['result'][key]['location']['coordinate']['latitude'];
    locationLng = resultObject['result'][key]['location']['coordinate']['longitude'];

    // Define the markers for each restaurant
    marker = new google.maps.Marker({
        position: new google.maps.LatLng(locationLat, locationLng),
        map: map,
        title: name
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