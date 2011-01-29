if (typeof Ticket == 'undefined')
    Ticket = new Object();
    
Ticket.keys_generate = new Object()

Ticket.keys_generate.init = function()
{
	$("#progressbar").progressbar({ value: 0 });
	Ticket.keys_generate.keys   = $('#all-keys').text();
    Ticket.keys_generate.closed = false
	// TODO: only one click!
	$("#keys_generate_button").click(function(){ Ticket.keys_generate.start(this); return false;});
}

Ticket.keys_generate.start = function(button)
{
    if ( Ticket.keys_generate.closed ) return false;
    Ticket.keys_generate.closed = true;
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
        success: Ticket.keys_generate.update
    });
}

Ticket.keys_generate.finish = function(result)
{
	clearInterval(Ticket.keys_generate.interval)
	$( "#progressbar" ).progressbar( "option", "value", 100 );
	if( result == "ok")
	{
		alert("Operacja zakończona powodzeniem")
	}
	else
	{
		alert("Wystąpił błąd")
	}
}

Ticket.keys_generate.update = function(result)
{
	var done    = parseInt(result);
	var all     = Ticket.keys_generate.keys
	var percent = parseInt ((done/all) * 100)
	$('#generated-keys').text(done);
	$('#keys-percent').text(percent);
	$( "#progressbar" ).progressbar( "option", "value", percent );
	
}

$(Ticket.keys_generate.init);
