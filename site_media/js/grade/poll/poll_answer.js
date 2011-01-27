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
    
    $('#poll-form').submit(Poll.answer.cleanup);
    $('.poll-section-choicelimit-choice').change(Poll.answer.choices_limit)
}

Poll.answer.cleanup = function()
{
	$('.poll-section-radio-hideon:checked').each(function()
    {
    	$(this).parents('.poll-section-leading').nextAll().each(function()
    	{
    		$(this).find('input:checked').attr('checked', false);
			$(this).find('textarea').val('');
    	})
    })
}

Poll.answer.choices_limit = function()
{
	if( $(this).attr('checked') )
	{
		var parent  = $(this).parent().parent()
		var limit   = $(parent).siblings('.poll-section-answer-limit').val()
		var checked = $(parent).find('.poll-section-choicelimit-choice:checked').length
		
		if (limit == null || limit == 0)
		{
			limit = checked
		}
		if (limit < checked)
		{
			alert("Podałeś za dużo odpowiedzi");
			$(this).attr('checked', false);
		}
	}
}

$(Poll.answer.init)

