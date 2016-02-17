function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 37.7886334, lng: -122.4114752},
    zoom: 12
  });

  var infoWindow = new google.maps.InfoWindow({map: map});

  var key, restaurant, yelpId, name, locationLat, locationLng, marker, html, anchor;
  var address, phone, image, ratingImage, reviewCount, status;

  for (key in resultObject['result']) {
    restaurant = resultObject['result'][key];
    yelpId = resultObject['result'][key]['id'];
    name = resultObject['result'][key]['name'];
    locationLat = resultObject['result'][key]['location']['coordinate']['latitude'];
    locationLng = resultObject['result'][key]['location']['coordinate']['longitude'];
    address = resultObject['result'][key]['location']['address'][0];
    city = resultObject['result'][key]['location']['city'];
    phone = resultObject['result'][key]['display_phone'];
    image = resultObject['result'][key]['image_url'];
    ratingImage = resultObject['result'][key]['rating_img_url'];
    reviewCount = resultObject['result'][key]['review_count'];
    status = resultObject['result'][key]['open_now'];

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
        '<h3><b>' + name + '</b></h3>' +
        '<p><img src="' + ratingImage + '" alt="rating"> ' + reviewCount + ' Reviews on Yelp</p>' +
        '<p>' + address + '</p>' +
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