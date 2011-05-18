
Offer = new Object();

Offer.init = function()
{
    $('.course-state').change(Offer.changeState);
    $('.show-teachers').click(Offer.showTeachers);
    $('.show-helpers').click(Offer.showHelpers);
    $('.show-fans').click(Offer.showFans);
}

$(Offer.init);

Offer.changeState = function()
{
    var new_value = $(this).val();

    var type = ''
    switch ( new_value )
    {
        case '0':
            type = 'none'
            break;

        case '1':
            type = 'offer'
            break;

        case '2':
            type = 'vote'
            break;
    }
    var tr = $(this).parent().parent()
    $(tr).removeClass()
    $(tr).addClass('selected-' + type)
}

Offer.showHelpers = function()
{
    Offer.show('Helpers', $(this).attr('link') )
    return false;
}

Offer.showTeachers = function()
{
    Offer.show('Teachers', $(this).attr('link') )
    return false;
}

Offer.showFans = function()
{
    Offer.show('Fans', $(this).attr('link') )
    return false;
}

Offer.show = function(group, id)
{
    $.ajax({
        type: "POST",
        dataType: "html",
        url: "/proposal/get" + group +"/" + id + "/",
        success: function(resp){
            Fereol.dialog.setHTML(resp);
            Fereol.dialog.setTitle("Podgląd ankiety");
            Fereol.dialog.show();
        }
    });
}
