// Display hungry pusheen gif once submit button is clicked
function showPusheen(evt) {
  evt.preventDefault();
  $("#hungry_pusheen").show();
  $(this).unbind('submit').submit();
}
$("#search-form").submit(showPusheen);


// Display curious pusheen gif while results page loads
$(window).load(function() {
  $("#curious_pusheen").fadeOut("slow");
});


// If open status is "Open now", change color to green
$(".open_status").each(function () {
  if ($(this).text() == "Open now") {
    $(this).css("color", "#0acc52");
    $(this).css("font-weight", "bold");
  }
});


// If open status is "Closed", change color to red
$(".open_status").each(function () {
  if ($(this).text() == "Closed") {
    $(this).css("color", "red");
    $(this).css("font-weight", "bold");
  }
});


// If open status is "Open now unknown", change color to gray
$(".open_status").each(function () {
  if ($(this).text() == "Open now unknown") {
    $(this).css("color", "gray");
    $(this).css("font-weight", "bold");
  }
});


// Change border color when hovering over a result
var key, yelpId;

for (key in resultObject['result']) {
  yelpId = resultObject['result'][key]['id'];

  $("#" + yelpId).hover(
    function() {
      $( this ).css("border", "2px solid #e73f3f");
    }, function() {
      $( this ).css("border", "2px solid #F0F0F0");
    }
  );
}


// Toggle sorting selections
$(".show_radio").hide();

function toggleRadioBtns(evt) {
  $(".show_radio").toggle();
}
  
$("#sort_by_btn").click(toggleRadioBtns);


// Toggle filtering selections
$(".show_checkbox").hide();

function toggleCheckBoxBtns(evt) {
  $(".show_checkbox").toggle();
}
  
$("#filter_by_btn").click(toggleCheckBoxBtns);
