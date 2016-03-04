function initAutocomplete() {
    // Get the HTML input element for the autocomplete search box.
    var input = document.getElementById('find_restaurant');

    // Create the autocomplete object.
    var autocomplete = new google.maps.places.Autocomplete(input);
    
    // When the user selects the place from the dropdown, get the place details.
    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        var address = place.formatted_address;
        var name = place.name;

        // Fill the corresponding fields with the restaurant name and address.
        document.getElementById('restaurant_name').value = name;
        document.getElementById('location').value = address;
    });
}

google.maps.event.addDomListener(window, 'load', initAutocomplete);


function validatePhoneNumber(phoneNumberInput) {
  var phoneNumberFormat = /^[\+]?[1]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4}$/;
  // Enable report button if phone number is in valid format.
  if (phoneNumberInput.match(phoneNumberFormat)) {
    $("#report").prop("disabled", false);
    $("#report").focus();
  // Enable report button if no phone number inputted.
  } else if (phoneNumberInput === "") {
    $("#report").prop("disabled", false);
    $("#report").focus();
  // Report button remains disabled if invalid phone number.
  } else {
    alert("Phone number is invalid.");
    $("#phone_number").focus();
  }
}