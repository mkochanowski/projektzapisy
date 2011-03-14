if (typeof Ticket == 'undefined')
    Ticket = new Object();
    
Ticket.keys_generate = new Object()

Ticket.keys_generate.init = function()
{
	$("#progressbar").progressbar({ value: 0 });
	Ticket.keys_generate.keys   = $('#all-keys').text();
    Ticket.keys_generate.start();
}

Ticket.keys_generate.start = function()
{
	$.ajax({
        type: "POST",
        url: "grade/ticket/ajax_keys_generate",
        success: Ticket.keys_generate.finish
    });
    Ticket.keys_generate.interval = setInterval( "Ticket.keys_generate.progress()", 2000 );
}

Ticket.keys_generate.progress = function()
{
	$.ajax({
        type: "POST",
        url: "grade/ticket/ajax_keys_progress",
        success: Ticket.keys_generate.update,
    });
}

Ticket.keys_generate.finish = function(result)
{
	clearInterval(Ticket.keys_generate.interval)
	$( "#progressbar" ).progressbar( "option", "value", 100 );
}

Ticket.keys_generate.update = function(result)
{
	var done    = parseInt(result);
	var all     = Ticket.keys_generate.keys
	var percent = parseInt ((done/all) * 100)
	$( "#generated-keys" ).text(done);
	$( "#keys-percent" ).text(percent);
	$( "#progressbar" ).progressbar( "option", "value", percent );
	
}

$(Ticket.keys_generate.init);

$('html').ajaxSend(function(event, xhr, settings) {
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
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
