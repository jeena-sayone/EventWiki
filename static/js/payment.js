var IntGlobalEventId = 0;
var strGlobalEventName = '';

// # Ready Function
$(document).ready(function() {
    var IntEventId = sessionStorage.getItem("intPkEventId");
    if(IntEventId){
        IntGlobalEventId = IntEventId;
        strGlobalEventName = sessionStorage.getItem("strEventName");
    }
    $("#divIdPayment").empty();
    var strDiv = "<input type = 'hidden' name = 'txtEventId' value = '"+IntGlobalEventId+"' ><br/><input type = 'hidden' name = 'txtEventName' value = '"+strGlobalEventName+"'>";

    $("#divIdPayment").append(strDiv);
    
});

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