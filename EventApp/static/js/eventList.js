var arrAllEventLocationType = ['','Physical venue','Online','Recorded Events'];
var objGlobalAllEvents = {};
$(document).ready(function () {
    // Show List Data
    showAllEventsData();
});

function showAllEventsData(){
    $("#tbyIdListAllEvents").empty();
    for (var i = 0; i < arrGloHtmlAllEventsData.length; i++) {

        objGlobalAllEvents[arrGloHtmlAllEventsData[i].intPkEventId] = arrGloHtmlAllEventsData[i];
    }
}

// Load Payment
function fnLoadPayment(intPkEventId){
    sessionStorage.setItem("intPkEventId", intPkEventId);
    sessionStorage.setItem("strEventName", objGlobalAllEvents[intPkEventId]['strEventName']);
    window.open('loadPaymentMethod', '_self');

}

// List Delete Icon Click
function onDeleteIconClick(intPkEventId,strEventName,intLastAction){
    $("#divIdMessages").empty()

    var arrDeleteEventData = new Array();
   
    arrDeleteEventData = {
            'strEventName' : strEventName,
            'intPkEventId' : intPkEventId,
            'intLastAction' : intLastAction,
   }

 // Y/N
 if (!(confirm('Do you want to delete the Event ?'))) {
    return;
}

 // Build JSON and Delete
 var jsnEventDeleteData = JSON.stringify(arrDeleteEventData)
 $.ajax({
    type: 'POST',
    url: '/delete_event',
    dataType: 'json',
    data: {'jsnEventDeleteData' : jsnEventDeleteData,
           'csrfmiddlewaretoken' : csrftoken,
    },
    success: function (data) {
        if(data.strStatus=='ERROR') {
            $('.toast').toast('show');
            $("#divIdMessages").append(data.strMessage)
        }
        else if(data.strStatus=='SUCCESS') {
            $('.toast').toast('show');
            $("#divIdMessages").append(data.strMessage)

            // Remove record in List
            $('#trId' + intPkEventId).remove();
           //Remove deleted element in global array "objGloHtmlAllEventsData" using 'delete' method
           delete arrGloHtmlAllEventsData[intPkEventId]
        }
       
    }
});

}

//On Edit Icon Click Function
function onEditIconClick(intPkEventId){
    $("#divIdMessages").empty()
    var objEventDetails = objGlobalAllEvents[intPkEventId];
    // # Set Session Data
    sessionStorage.setItem("objEventDetails", JSON.stringify(objEventDetails));
    window.open('edit-event/id='+intPkEventId, '_self');

}

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