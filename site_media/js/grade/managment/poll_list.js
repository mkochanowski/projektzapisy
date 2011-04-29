if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.list = new Object();


Poll.list.init = function()
{
    $('.poll_list_a').click(function()
    {
        poll = Poll.list.getPoll( $(this).attr('href') )
        $('#box').html( poll );
        $('#screen').css({  "display": "block", opacity: 0.7, "width":$(document).width(),"height":$(document).height()});
        $('#box').css({"display": "block"}).click(function(){$(this).css("display", "none");$('#screen').css("display", "none")});
        return false;
    })
}

$(Poll.list.init);

Poll.list.getPoll = function( link )
{
	var result;
	$.ajax({
        type: "POST",
        url: link,
        async: false,
        success: function(data)
        {
			result = data;
        }
    });
    return result
}

