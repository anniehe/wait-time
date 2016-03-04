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