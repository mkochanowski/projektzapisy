if (typeof Ticket == 'undefined')
    Ticket = new Object();
    
Ticket.keys_generate = new Object()

Ticket.keys_generate.init = function()
{

    if( $(".main-message:contains('Liczba utworzonych ankiet:')").size() > 0) // TODO: ej, tego się tak nie robi
    {
        $('#screen').css({  "display": "block", opacity: 0.7, "width":$(document).width(),"height":$(document).height()});
        $('#box').css({"display": "block"}).click(function(){$(this).css("display", "none");$('#screen').css("display", "none")});
    	$("#progressbar").progressbar({ value: 0 });
	    Ticket.keys_generate.keys   = $('#all-keys').text();
        Ticket.keys_generate.start();
    }
}

Ticket.keys_generate.start = function()
{
	$.ajax({
        type: "POST",
        url: url_generate,
        success: Ticket.keys_generate.finish
    });
    Ticket.keys_generate.interval = setInterval( "Ticket.keys_generate.progress()", 2000 );
}

Ticket.keys_generate.progress = function()
{
	$.ajax({
        type: "POST",
        url: url_progress,
        success: Ticket.keys_generate.update
    });
}

Ticket.keys_generate.finish = function(result)
{
	clearInterval(Ticket.keys_generate.interval)
	$( "#progressbar" ).progressbar( "option", "value", 100 );
	$( "#keys-percent" ).text('100');
	$( "#generated-keys" ).text(Ticket.keys_generate.keys);
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

