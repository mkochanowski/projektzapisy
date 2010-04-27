
$(document).ready(
    function()
    {
        $('[name=selectSubject]').click(selectSubject);
        $('.teachersDetails').each(showTeachersDetails);
        //$('.teachersDetails').click(showTeachersDetails);
    }
);

function selectSubject()
{
    var tr = $(this).parent().parent();
    var action;
    
    if ($(this).is(':checked'))
    {
        tr.addClass('selected');
        action = 'select';    
    }
    else
    {
        tr.removeClass('selected');
        action = 'unselect';
    }
    
    // TODO: Wysłać zapytanie zaznaczające / odznaczające
}

function showTeachersDetails()
{
    var id = $(this).attr('subject');
    
    $(this).colorbox({ "inline" : true, "href" : "#teachers" + id, "title" : ""});
}