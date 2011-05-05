if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.list = new Object();


Poll.list.init = function()
{
    $('.poll_list_a').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.show();
        return false;
    })
    $('.section_list_a').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.show();
        $('#box-belt-edit').remove();
        if(! $(this).parent().parent().find('._selected_action').attr('disabled') )
        {
            $('#box-belt').append($("<input type='button' value='Edytuj' id='box-belt-edit'>"));
        }
        Poll.section.showEdit();


        $('#box-belt-edit').click(function()
        {
            Poll.section.init();
            $(this).hide();
        });
        return false;
    })

    $('#new-section').click(function()
    {
        var html = Poll.list.getCreateSection();
        Fereol.dialog.setHTML(html);
        Fereol.dialog.show();
        Poll.section.init();
        return false;
    })

    $('#new-poll').click(function()
    {
        var html = Poll.list.getCreatePoll();
        Fereol.dialog.setHTML( html )
        Fereol.dialog.show();
        Poll.create.init();
        return false;
    })

    $('#new-template').click(function()
    {
        var html = Poll.list.getCreateTemplate();
        Fereol.dialog.setHTML( html )
        Fereol.dialog.show();
        Poll.create.init();
        return false;
    })

    $('.show_template').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.show();
        return false;
    });
}

$(Poll.list.init);

Poll.list.getCreateTemplate = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/templates/form/');
}

Poll.list.getCreateSection = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/section/form/');
}

Poll.list.getCreatePoll = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/poll/form/');
}

Poll.list.getHTML = function( link )
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

