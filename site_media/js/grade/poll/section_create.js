if (typeof Poll == 'undefined'){
    Poll = new Object();﻿
}
Poll.section = Object();


jQuery.validator.addMethod("have_questions", function(value, element) {
  return $('.questionset').children().size() > 0;
}, "Sekcja nie zawiera pytań.");

jQuery.validator.addMethod("have_answers", function(value, element){
    if ( $(element).parents('.poll-question').find('input[name$="[type]"]').val() == 'open' )
    {
        return true;
    }
    return $(element).siblings('.answerset').children().size()>0;
}, "To pytanie musi mieć odpowiedzi.")


jQuery.validator.addClassRules("anyquestion", {
  have_questions: true
});

jQuery.validator.addClassRules("anyanswer", {
  have_answers: true
});

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

    $(".leading").attr('checked', false)
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
    $("#questionset").validate();
   /* $('#questionset-submit').click(function()
    {
        if( Poll.section.submitted )
        {
            return false;
        }
        Poll.section.submitted = true;
    });*/
    /* enter don't sending */
    $("form").keypress(function(e)
    {
          if (e.which == 13) // 13 == enter
          {
            return false;
          }
    });
    $(Poll.section.editParser);
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
    $('.poll-question').each(function(i, d){Poll.section.parse($(this))});

    Poll.section.questions = $('.poll-question').size()
    $('.autocomplete').each(function()
    {
        $(this).autocomplete(
        {
         source:'grade/poll/autocomplete',
         delay:10
         }
        );
    });
    $('.typeSelect').change(function()
    {
        Poll.section.changeType( li )
    });


    $('.ready').click(function()
    {
        var li   = $(this).parents('.poll-question');
        if ( Poll.section.validate(li) )
        {
            Poll.section.createView( li );
            $('.edit-mode').hide();
        }
    });
    $('.ready').click();
    $('.edit-mode').hide()
    $('.delete').click(function()
    {
        var li = $(this).parents('.poll-question');
        Poll.section.remove( li );
        Poll.section.validate( li );
    });

    $('.delete-answer').click(function(){

         $(this).parents('.poll-question-answer').remove();
    })
}

Poll.section.parse = function(li)
{

    var type = $(li).find('input[name$="[type]"]').val();

    /* type selectbox configuration */
    for( var t in poll_types)
    {
        $.tmpl( "type_option", poll_types[t])
            .appendTo( $(li).find('.options') )
    }

    $(li).find('.options').val(type);
    Poll.section.changeType( li );
    $(li).find('.edit-mode')
         .click(function()
            {
                Poll.section.createEdit( li );
            });
    

}

//////////////////////////////////////////////////////////////
//// Question creation
/////////////////////////////////////////////////////////////


/*
* Create new question in section and put at end of questionContainer
*
* @author mjablonski
*
 */

Poll.section.createQuestion = function( )
{
    if( Poll.section.havelastLi)
    {
        if( !Poll.section.validate( Poll.section.lastLi))
        {
            return false;
        }
    }

    Poll.section.questions++;
    var data = {
        id: Poll.section.questions
    }
    Poll.section.questionCreator('last', data);
    $('.edit-mode').hide()
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


    // create object in position:
    var li;

    if ( position == 'top')
    {
        $.tmpl( "question_edit", data)
                .prependTo( Poll.section.questionContainer );
        li = $(Poll.section.questionContainer)
                .children()
                .first()
    }
    else if ( position == 'last')
    {
        $.tmpl( "question_edit", data)
                .appendTo( Poll.section.questionContainer );
        li = $(Poll.section.questionContainer)
                .children()
                .last()
    }


    for( var t in poll_types)
    {
        $.tmpl( "type_option", poll_types[t])
                .appendTo( $(li).find('.options') )
    }
    
    //
    if ( Poll.section.havelastLi )
    {
        Poll.section.createView(Poll.section.lastLi)
    }
    Poll.section.lastLi = $(Poll.section.questionContainer)
                        .find('.poll-question')
                        .last();

    Poll.section.havelastLi = true;

    // buttons events

    $('.ready').click(function(){
        var li = $(this).parents('.poll-question');
        if( Poll.section.validate(li) )
        {
            Poll.section.createView( li );
            $('.edit-mode').hide()
        }

    })
    $('.delete').click(function(){
                    var li = $(this).parents('.poll-question');
                    $(li).remove()
                });
    $('select[name$="[formtype]"]').change(function()
                {
                    var li = $(this).parents('.poll-question');
                    Poll.section.changeType( li )
                })

}

/*
* Add answer to question.
*
* @author mjablonski
* @param dom-node li - questionset element
 */
Poll.section.addAnswer = function( li, data )
{
     // Prepare data
    var type      = $(li).find('input[name$="[type]"]').val();
    var answerset = $(li).find('.answerset');

    var leading = Poll.section.isLeadingQuestion( li );


    data.id      = $(li).find('input[name="poll[question][order][]"]').val()
    data.size    = $(answerset).children().size() + 1
    data.leading = leading
    if (typeof data.name == 'undefined'){
        data.name = '';﻿
    }

    // create object
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
///// Edit and View mode
///////////////////////////////////////////////////////////////

/*
* Change to view-mode
*
* @author mjablonski
* @param dom-node li - element of questionset
 */

Poll.section.createView = function( li )
{
    $('.edit-mode').hide()
    // clean old view
    $(li).children('.section-show')
        .remove();
    Poll.section.havelastLi = false;
    var data = {
        type:  $(li).find('input[name$="[type]"]').val(),
        title: $(li).find('input[name$="[title]"]').val(),
        desc:  $(li).find('input[name$="[description]"]').val(),
        questionset: Poll.section.makeQuestionset( li ),
        optionset: Poll.section.makeOptionset( li )
    }
    $.tmpl( "question_view", data ).appendTo( li );
    $(li).children('.section-edit').hide();

    $(li).find('.section-show')
            .dblclick(function()
                {
                    Poll.section.createEdit(li)
                })
    $(li).find('.edit-mode')
         .click(function()
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
* Change mode to edit
*
* @author mjablonski
* @param dom-node li - element of questionset
 */

Poll.section.createEdit = function( li )
{
    if( !Poll.section.validate(Poll.section.lastLi))
    {
        return false;
    }
     if ( Poll.section.havelastLi )
     {
        Poll.section.createView(Poll.section.lastLi)
     }
     Poll.section.havelastLi = true;
     Poll.section.lastLi     = li;
    $(li).find('.section-show').remove();
    $(li).children('.section-edit').show();
    $("#questionset").validate().element('.anyquestion');
}

/*
* Change type event
*
* @author mjablonski
* @param dom-node li - element of questionset
 */

Poll.section.changeType = function( li )
{
    var formtype  = $(li).find('select[name$="[formtype]"]').val();
    var type      = poll_types[formtype].realtype;
    $(li).find('input[name$="[type]"]').val( type );
    
    var div       = $(li).children('.section-edit');
    var answerset = $(li).find('.answerset');


    $(li).find('.option').hide();
    $(poll_types[formtype].options).each(function(index, value)
    {
        $(li).find('.' + value).show();
    })
    $(poll_types[formtype].optionOn).each(function(index, value)
    {
        $(li).find('.' + value).attr('checked', true)
    })

    $(li).find('input[name="addQuestion"]').remove();
    if( !poll_types[formtype].haveAnswers)
    {
        $(answerset).empty();
    }
    else
    {
        if( $(poll_types[formtype].answers).size() > 0)
        {
            $(answerset).empty();
            $(poll_types[formtype].answers).each(function(index, value)
            {
                var data = {
                    name: value
                }
                Poll.section.addAnswer( li, data );
            })
        }
        else if ($(answerset).children().size() == 0)
        {

            Poll.section.addAnswer( li, new Object() );
        }
        var data = {
            id: $(li).find('input[name="poll[question][order][]"]').val(),
            size: $(answerset).children().size()
        }
        $.tmpl( "question_add", data ).insertAfter( answerset );
        $('.addQuestion').click(function()
            {
                var li = $(this).parents('.poll-question');
                Poll.section.addAnswer( li, new Object );
            });
    }

    $('.autocomplete').autocomplete(
    {
        source:'/grade/poll/autocomplete',
        delay:10
    });
}


$(Poll.section.init);


/////////////////////////////////////////////////////////////
//// Help functions
/////////////////////////////////////////////////////////////


/*
* Prepare json with state of optionset
*
* @author mjablonski
* @param dom-node li - questionset element
* @return json  - optionset state
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
* Prepare json with answer state
*
* @author mjablonski
* @param dom-node li - element of questionset
* @return json - answers for question
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
    if( ! Poll.section.validate( Poll.section.lastLi ) )
    {
        $(".leading").attr('checked', false)
        return false;
    }
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
        $("#questionset").validate().element('.anyquestion');
        $("#questionset").valid();
    }
}


Poll.section.validate = function(li)
{
    var element_tilte   = $(li).find('input[name$="[title]"]');
    var element_answers = $(li).find('.anyanswer');
    var a = $("#questionset").validate().element(element_tilte);
    var b = $("#questionset").validate().element(element_answers);

    var c = true;

    $(li).find('.question-answer').each(function(i, elem)
    {
        c = c && $("#questionset").validate().element(elem);
    })

    return a && b && c;
}
