if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.results = Object()

Poll.results.init = function()
{
    var pid  = $('#poll-id').val();
    var mode = $('#display-mode').val();
    
    $('.hidden-answers').hide();
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
    
    if (pid != -1) {
        if (mode == 'subject'){
            $('#results-by-subject-list').show();
        }
        else if (mode == 'teacher'){
            $('#results-by-teacher-list').show();
        }
    }
    
    $('.show-ans-link').click(function(){
        $(this).siblings('.hidden-answers').slideToggle(250);
        return false;
    })
    
    $('.show-other-ans-link').click(function(){
        $(this).parent().siblings('.hidden-answers').slideToggle(250);
        return false;
    })
    
    $('.section-link').click(function(){
        $(this).parent().siblings('table').slideToggle(250);
        return false;
    })
}

$(Poll.results.init)

