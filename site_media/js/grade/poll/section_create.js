if (typeof Poll == 'undefined'){
    Poll = new Object();﻿
}
Poll.section = Object();


///////////////////////////////////////////////////////////
//// Functions  run after page load
///////////////////////////////////////////////////////////

Poll.section.init = function()
{
    /* set vars */
    Poll.section.submitted         = false; // no double-send
    Poll.section.questions         = 0;     // number of questions
    Poll.section.questionContainer = $("#poll-form");
    Poll.section.havelastLi        = false; // to change active question


    $(Poll.section.questionContainer).sortable({
            handle : 'div',
            zIndex: 5,
            tolerance: 'pointer',
            items: '> li:not(.firstQuestion)'

    });
    /* set events */
    $("#add-question").click(Poll.section.createQuestion)
    $("input[type=text]").focus(function(){ this.select(); });
    $("textarea").focus(function(){ this.select(); });
    $(".leading").change(Poll.section.changeLeading);
    
    // send form
    $('#questionset-submit').click(function()
    {
        if( Poll.section.submitted )
        {
            return false;
        }
        Poll.section.submitted = true;
    });
    /* enter don't sending */
    $("form").keypress(function(e)
    {
          if (e.which == 13) // 13 == enter
          {
            return false;
          }
    });
}

/*
* Function using during section edit.
* It parse html and set events and variables
*
* @author mjablonski
*
 */
Poll.section.editParser = function()
{
    $('.autocomplete').each(function()
    {
        $(this).autocomplete(
        {
         source:'grade/poll/autocomplete',
         delay:10
         }
        );
    });
    $('.answerset').sortable({handle : 'div'});
    $('.typeSelect').change(function()
    {
        var li = $(this).parents('.poll-question');
        Poll.section.changeType( li )
    });
    Poll.section.questions = $('.poll-question').size()

    $('.ready').click(function()
    {
        var li   = $(this).parents('.poll-question');
        Poll.section.createView( li );
        
    });
    $('.ready').click();
    $('.delete').click(function()
    {
        var li = $(this).parents('.poll-question');
        Poll.section.remove( li );
    });    

    $('.addQuestion').click(function()
    {
        var li = $(this).parents('.poll-question');
        Poll.section.addOptionButton( li );
    });
    $('.delete-answer').click(function(){

         $(this).parents('.poll-question-answer').remove();
    })
}

//////////////////////////////////////////////////////////////
//// Metody poswiecone tworzeniu nowych pytan
/////////////////////////////////////////////////////////////


/*
* Create new question in section and put at end of questionContainer
*
* @author mjablonski
*
 */

Poll.section.createQuestion = function( )
{
    Poll.section.questions++;
    var data = {
        id: Poll.section.questions
    }
    Poll.section.questionCreator('last', data);


}

/*
* Create question.
*
* @author mjablonski
*
* @param string position  - position of question in place: top or last
* @param json data - with id of question
*
 */

Poll.section.questionCreator = function( position, data )
{
    if ( position == 'top')
    {
        $.tmpl( "question_edit", data)
                .prependTo( Poll.section.questionContainer );
    }
    else if ( position == 'last')
    {
        $.tmpl( "question_edit", data)
                .appendTo( Poll.section.questionContainer );
    }

    if ( Poll.section.havelastLi )
    {
        Poll.section.createView(Poll.section.lastLi)
    }
    Poll.section.lastLi = $(Poll.section.questionContainer)
                        .find('.poll-question')
                        .last();

    Poll.section.havelastLi = true;

    $('.ready').click(function(){
                    var li = $(this).parents('.poll-question');
                    Poll.section.createView( li );
                })
    $('.delete').click(function(){
                    var li = $(this).parents('.poll-question');
                    Poll.section.remove( li );
                });
    $('select[name$="[type]"]').change(function()
                {
                    var li = $(this).parents('.poll-question');
                    Poll.section.changeType( li )
                })

}

/*
* Add button to new answer to question.
*
* @author mjablonski
* @param dom-node li - questionset element
 */
Poll.section.addOptionButton = function( li )
{
     // Przygotowanie danych do szablonu
     var type      = $(li).find('select[name$="[type]"]').val();
     var answerset = $(li).find('.answerset');

     var leading = Poll.section.isLeadingQuestion( li );


     var data = {
        id: $(li).find('input[name="poll[question][order][]"]').val(),
        size: $(answerset).children().size() + 1,
        leading: leading
     }
    // zastosowanie szablonu:
     $.tmpl( "question", data ).appendTo( answerset );
     $('.remove').click(function()
     {
        $(this).parents('.poll-question-answer').remove();
     });
}


/*
* Function to check leading
*
* @author mjablonski
*
* @param dom-node li - element of questionset
* @return bool - true if li is leading question, false if not
 */

Poll.section.isLeadingQuestion = function( li)
{
    if ( ! $(".leading").is(':checked') )
    {
        return false;
    }
    if ($(li).find('input[name="poll[question][order][]"]').val() == 0)
    {
        return true;
    }
    return false;
}

///////////////////////////////////////////////////////////////
///// Obsługa trybów: edycji i widoku zwykłego
///////////////////////////////////////////////////////////////

/*
* Metoda przelacza tryb pytania z edycji do widoku zwyklego
*
* @author mjablonski
* @param dom-node li - element listy pytań
 */

Poll.section.createView = function( li )
{

    // clean old view
    $(li).children('.section-show')
        .remove();
    Poll.section.havelastLi = false;
    var data = {
        type:  $(li).find('select[name$="[type]"]').val(),
        title: $(li).find('input[name$="[title]"]').val(),
        desc:  $(li).find('input[name$="[description]"]').val(),
        questionset: Poll.section.makeQuestionset( li ),
        optionset: Poll.section.makeOptionset( li )
    }
    $.tmpl( "question_view", data ).appendTo( li );
    $(li).children('.section-edit').hide();
    $(li).find('.section-show').dblclick(function(){Poll.section.createEdit(li)})
    $(li).find('.edit-mode').click(function()
        {
            Poll.section.createEdit( li );
        });
    $(li).children('.section-show').mouseover(function(){
        $(this).addClass('section-mouseover');
        $(this).find('.edit-mode').show()
        });
    $(li).children('.section-show').mouseout(function(){
        $(this).removeClass('section-mouseover');
        $(this).find('.edit-mode').hide()        
        });
}

/*
* Metoda zmienia tryb pytania na 'edycja'
*
* @author mjablonski
* @param dom-node li - element listy pytan
 */

Poll.section.createEdit = function( li )
{
     if ( Poll.section.havelastLi )
     {
        Poll.section.createView(Poll.section.lastLi)
     }
     Poll.section.havelastLi = true;
     Poll.section.lastLi     = li;
    $(li).find('.section-show').remove();
    $(li).children('.section-edit').show();
}

/*
* Metoda wykonywana jest po zmianie typu pytania
* dostosowuje pytanie do wybranego typu
*
* @author mjablonski
* @param dom-node li - element listy pytan
 */

Poll.section.changeType = function( li )
{
    var type      = $(li).find('select[name$="[type]"]').val();
    var div       = $(li).children('.section-edit');
    var answerset = $(li).find('.answerset');
    Poll.section.hideOptions( li, type );
    
    if (type == 'open')
    {
        $(answerset).empty();
        $(li).find('input[name="addQuestion"]').remove();
    }
    else
    {
        if( $(answerset).children().size() == 0 )
        {
            var data = {
                id: $(li).find('input[name="poll[question][order][]"]').val(),
                size: 0
            } 
            Poll.section.addOptionButton( li );
            
            $.tmpl( "question_add", data ).insertAfter( answerset );
            $('.addQuestion').click(function()
            {
                var li = $(this).parents('.poll-question');
                Poll.section.addOptionButton( li );
            });
            $('.autocomplete').autocomplete(
            {
                source:'/grade/poll/autocomplete',
                delay:10
            });
        }
        
    }
}


$(Poll.section.init);


/////////////////////////////////////////////////////////////
//// Różne medoty pomocnicze
/////////////////////////////////////////////////////////////

/*
* Po zmianie typu pytania przelacza opcje dodatkowe
*
* @author: mjablonski
 */
Poll.section.hideOptions = function( li, type )
{

    $(li).find('.' + type).show();
    $(li).find('.not-' + type).hide();
}

/*
* Przygotowuje informacje o ustawieniach pytania do przeslania do szablonu
* Wykorzystywane przy zmianie widoku
*
* @author mjablonski
* @param dom-node li - element listy pytań
 */
Poll.section.makeOptionset = function( li )
{
    return {
        isScale:     $(li).find('input[name$="[isScale]"]').val(),
        hasOther:    $(li).find('input[name$="[hasOther]"]').val(),
        choiceLimit: $(li).find('input[name$="[choiceLimit]"]').val()
    }
}

/*
* Przygotowuje liste odpowiedzi
* wykorzystywane przy zmianie widoku pytania
*
* @author mjablonski
* @param dom-node li - element listy pytań
* */
Poll.section.makeQuestionset = function( li )
{
    var questions = new Array();
    $(li).find('.poll-question-answer')
         .children('div')
         .each(function()
               {
                 questions.push(
                    {
                        title:   $(this).find('input[name$="[answers][]"]').val(),
                        isHiden: $(this).find('input[name$="[hideOn][]"]').val()
                   })
               });
    return questions;
}

/*
 * Function show leading question
 *
 * @author mjablonski
 */

Poll.section.changeLeading = function()
{
    if ( $(this).is(':checked') )
    {
        //
        var data = {
            id: 0
        }
        Poll.section.questionCreator('top', data);

        var leadingQuestion = $(Poll.section.questionContainer)
                .children()
                .first();
        // change and hide type

        Poll.section.lastLi = leadingQuestion;
        $(leadingQuestion)
                .find('.typeSelect')
                .val("single")
                .hide()
                .change()

        // hide delete button
        $(leadingQuestion)
                .find('.delete')
                .hide();
        
        // don't sort first in questionset
        $(leadingQuestion)
                .addClass('firstQuestion');

    }
    else
    {
        // delete first
        $(Poll.section.questionContainer)
                .children()
                .first()
                .remove();
    }
}


