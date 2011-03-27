if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.results = Object()

Poll.results.init = function()
{
    var pid  = $('#poll-id').val();
    var mode = $('#display-mode').val();
    
    $('.result-groupped-list').hide();
	$('#results-by-subject-list').hide();
    $('#subjects-list-link').click( function(){
        $('#results-by-subject-list').slideToggle(250);
        return false;
    });
    $('#results-by-teacher-list').hide();
    $('#teachers-list-link').click( function(){
        $('#results-by-teacher-list').slideToggle(250);
        return false;
    });
    $('.list-link').click(function(){
		$(this).parent().siblings('.result-groupped-list').slideToggle(250);
        return false;
	})

    $('#results-by-'+mode+'-'+pid).show();
    $('#results-by-'+mode+'-'+pid).parent().show();
    $('#results-by-'+mode+'-'+pid).parent().parent().show();
    
    if (mode == 'subject'){
        $('#results-by-subject-list').show();
    }
    else if (mode == 'teacher'){
        $('#results-by-teacher-list').show();
    }
}

$(Poll.results.init)

