$(document).ready(
	function()
	{
		$('[name=selectCourse]').click(selectCourse);
		$('.teachersDetails').each(showTeachersDetails);
		$('.helpersDetails').each(showHelpersDetails);
		//$('.teachersDetails').click(showTeachersDetails);
	}
);

function selectCourse()
{
	var tr = $(this).parent().parent();
	var action;

	if ($(this).is(':checked'))
	{
		tr.addClass('selected');
		$(this).attr('checked', true);
		action = 'select';
	}
	else
	{
		tr.removeClass('selected');
		$(this).removeAttr('checked');
		action = 'unselect';
	}

	$.ajax({
		type    : 'POST',
		url     : '/proposal/offer/select/',
		data    : {
			'action'    : action,
			'id'        : $(this).val()
		},
		success : function ()
		{
		},
		error : function()
		{
			if (action == "unselect")
			{
				tr.addClass('selected');
			}
			else
			{
				tr.removeClass('selected');
			}
			alert('Operacja wyboru nie powidła się');
		}
	});
}

function showTeachersDetails()
{
	var id = $(this).attr('course');

	$(this).colorbox({ "inline" : true, "href" : "#teachers" + id, "title" : ""});
}

function showHelpersDetails()
{
	var id = $(this).attr('course');

	$(this).colorbox({ "inline" : true, "href" : "#helpers" + id, "title" : ""});
}
