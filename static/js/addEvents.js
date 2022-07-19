var intGlobalPkEventsId = 0;
$(document).ready(function () {
    // focus on first field
    $("#txtIdEventName").focus()
    //Date Picker
    // $(function () {
    //     $('#datetimepicker6').datetimepicker();
    //     $('#datetimepicker7').datetimepicker({
    // useCurrent: false //Important! See issue #1075
    // });
    //     $("#datetimepicker6").on("dp.change", function (e) {
    //         $('#datetimepicker7').data("DateTimePicker").minDate(e.date);
    //     });
    //     $("#datetimepicker7").on("dp.change", function (e) {
    //         $('#datetimepicker6').data("DateTimePicker").maxDate(e.date);
    //     });
    // });

    onNewButtonCase();
   
    //On Update Mode
    var objEventDetails = sessionStorage.getItem("objEventDetails");
    if(objEventDetails){
        var objJsonEventDetails = JSON.parse(objEventDetails);
        fnLoadEventDataToGui(objJsonEventDetails);
        sessionStorage.setItem("objEventDetails", '');
    }
});


function fnLoadEventDataToGui(objJsonEventDetails){
    $("#btnIdCreateEvent").hide();
    $("#btnIdUpdateEvent").show();
    intGlobalPkEventsId = objJsonEventDetails.intPkEventId;
    $('#txtIdEventName').val(objJsonEventDetails.strEventName);
    $('#strEventEndTime').val(objJsonEventDetails.strEventEndDateTime);
    $('#strEventStartTime').val(objJsonEventDetails.strEventStartDateTime);
    $('#cmbIdEventLocation').val(objJsonEventDetails.intEventLocation);

    $('#txtIdEventLocation').val(objJsonEventDetails.strEventVenue);
    $('#txaIdEventDesc').val(objJsonEventDetails.strEventDescription);
    //$('#uploadFile').val(objJsonEventDetails.strEventPoster);

}

// On create event Button Click
$('#btnIdCreateEvent').click(function(event) {
    event.preventDefault();
    document.getElementById("btnIdCreateEvent").disabled = true;
    //Check General validations
    if($.trim($('#txtIdEventName').val()) == ''){
        alert("Event Name is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    if($.trim($('#strEventStartTime').val()) == ''){
        alert("Event Start Date and Time is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    if($.trim($('#strEventEndTime').val()) == ''){
        alert("Event End Date and Time is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    if($.trim($('#txtIdEventLocation').val()) == ''){
        alert("Event Location is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    if($.trim($('#txaIdEventDesc').val()) == ''){
        alert("Event Description is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    if($('#uploadFile')[0].files[0] == ''){
        alert("Event Poster is Required");
        document.getElementById("btnIdCreateEvent").disabled = false;
        return false;
    }
    
    // Get All Data from GUI
    var arrCreateEventData = getDataFromGui();
    
    var fileSize = ($('#uploadFile')[0].files[0].size/1024);
    var fileName = $('#uploadFile')[0].files[0].name;
    var realSize = fileSize;
    var formData = new FormData();    
    formData.append('file', $('input[type=file]')[0].files[0]);
    formData.append('strFileName', fileName);
    var jsnCreateEventData = JSON.stringify(arrCreateEventData);
    formData.append('arrCreateEventData', jsnCreateEventData);
    $.ajax({
        url: 'addEvent',
        type: 'post',
        data:formData,
        csrfmiddlewaretoken: csrftoken,
        cache: false,
        processData: false,
        async: false,
        contentType: false,
        enctype: 'multipart/form-data',
        success: function(data){
            if(data.strStatus == 'SUCCESS'){
                onNewButtonCase();
                alert('Event Added successfully');
            }else{
                alert('Event Add Error');
            }
        }
});

document.getElementById("btnIdCreateEvent").disabled = false;
})

function getDataFromGui(){

    var strEventName = $.trim($('#txtIdEventName').val());
    var strEventStartTime = $('#strEventStartTime').val();
    var strEventEndTime = $('#strEventEndTime').val();
    var intEventLocation = parseInt($('#cmbIdEventLocation').val()); 
    var strEventLocation = $.trim($('#txtIdEventLocation').val());
    var strEventDescription = $.trim($('#txaIdEventDesc').val());
    var strEventPoster = $('#txaIdEventDesc').val();
    var intLastAction = 0;//New Event
    var intIfPaid = 0;
    
    // Build New Event Data array
    var arrCreateEventData = {
        'intPkEventsId':intGlobalPkEventsId,
        'strEventName'    : strEventName,
        'strEventStartTime'     : strEventStartTime,
        'strEventEndTime' : strEventEndTime,
        'intEventLocation' : intEventLocation,
        'strEventLocation' : strEventLocation,
        'strEventDescription' : strEventDescription,
        'strEventPoster' : strEventPoster,
        'intLastAction' : intLastAction,
        'intIfPaid' : intIfPaid
}
return arrCreateEventData;
}

function onNewButtonCase(){
    // Clear Inputs
    $('#txtIdEventName').val('');
    document.getElementById("formIdCreateEvent").reset();
    // Focus first widget
    $("#txtIdEventName").focus()
    intGlobalPkEventsId = 0;
    $("#btnIdCreateEvent").show();
    $("#btnIdUpdateEvent").hide();
}

// On create event Button Click
$('#btnIdUpdateEvent').click(function(event) {
    event.preventDefault();
    document.getElementById("btnIdUpdateEvent").disabled = true;

    //Check General validations
    if($.trim($('#txtIdEventName').val()) == ''){
        alert("Event Name is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }
    if($.trim($('#strEventStartTime').val()) == ''){
        alert("Event Start Date and Time is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }
    if($.trim($('#strEventEndTime').val()) == ''){
        alert("Event End Date and Time is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }
    if($.trim($('#txtIdEventLocation').val()) == ''){
        alert("Event Location is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }
    if($.trim($('#txaIdEventDesc').val()) == ''){
        alert("Event Description is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }
    if(typeof($('#uploadFile')[0].files[0])=='undefined'){
        alert("Event Poster is Required");
        document.getElementById("btnIdUpdateEvent").disabled = false;
        return false;
    }

    // Get All Data from GUI
    var arrCreateEventData = getDataFromGui();

    var fileSize = ($('#uploadFile')[0].files[0].size/1024);
    var fileName = $('#uploadFile')[0].files[0].name;
    var realSize = fileSize;
    var formData = new FormData();
    formData.append('file', $('input[type=file]')[0].files[0]);
    formData.append('strFileName', fileName);
    var jsnCreateEventData = JSON.stringify(arrCreateEventData);
    formData.append('arrCreateEventData', jsnCreateEventData);
    $.ajax({
        url: 'updateEvent',
        type: 'POST',
        data:formData,
        csrfmiddlewaretoken: csrftoken,
        cache: false,
        processData: false,
        contentType: false,
        async: false,
        enctype: 'multipart/form-data',
        success: function(data){
            if(data.strStatus == 'SUCCESS'){
                onNewButtonCase();
                alert('Event Updated successfully');
                window.open('eventsList');
            }else{
                alert('Event Update Error');
            }
        }
});

document.getElementById("btnIdUpdateEvent").disabled = false;


})

// Sites injection control
var csrftoken = getCookie('csrftoken');
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}