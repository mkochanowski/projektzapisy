if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.answer = Object()

Poll.answer.init = function()
{
	$('.poll-section-radio-hideon:checked').each(function()
    {

    	$(this).parents('.poll-section-leading').nextAll().hide()
    })
    $('.poll-section-radio-hideon').change(function()
    {

    	$(this).parents('.poll-section-leading').nextAll().hide()
    })
    
    $('.poll-section-radio-all').change(function()
    {

    	var father = $(this).parents('.poll-section-leading');
        $(father).nextAll().show()
    })
}

$(Poll.answer.init)