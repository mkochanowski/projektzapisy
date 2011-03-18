if (typeof Poll == 'undefined'){
    Poll = new Object();﻿
}
Poll.section = Object();


///////////////////////////////////////////////////////////
//// Metody wykonywane po zaladowaniu strony
///////////////////////////////////////////////////////////

Poll.section.init = function()
{
    /* set vars */
    Poll.section.submitted         = false; // no double-send
    Poll.section.questions         = 0;     // number of questions
    Poll.section.questionContainer = $("#poll-form");
    Poll.section.havelastLi        = false; // to change active question

    /* bahaviors */
    Poll.section.toggleLeading();

    $(Poll.section.questionContainer).sortable({
            handle : 'div',
            zIndex: 5,
            tolerance: 'pointer',
            deactivate: function(event, ui)
                        {
                            Poll.section.toggleLeading();
                        }

    });
    /* set events */
    $("#add-question").click(Poll.section.createQuestion)
    $("input[type=text]").focus(function(){ this.select(); });
    $("textarea").focus(function(){ this.select(); });
    $(".leading").change(Poll.section.toggleHideOn);
    
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
* Metoda stosowana przy widoku edycji sekcji
* parsuje istniejace juz pytania ustawia
* zmienne oraz zdarzenia tak, aby skrypt dzialal
* rowniez tam.
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
* Co zaskakujace, metoda ta sluzy do tworzenia nowego pytania
* zarowno od strony htmla jak i przypisania zdarzen
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
    $.tmpl( "question_edit", data).appendTo( Poll.section.questionContainer );

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
* Metoda dodaje przycisk dodajacy odpowiedzi do pytania
*
* @author mjablonski
* @param dom-node li - element listy pytań
 */
Poll.section.addOptionButton = function( li )
{
     // Przygotowanie danych do szablonu
     var type      = $(li).find('select[name$="[type]"]').val();
     var answerset = $(li).find('.answerset');
     var data = {
        id: $(li).find('input[name="poll[question][order][]"]').val(),
                size: $(answerset).children().size() + 1
     }
    // zastosowanie szablonu:
     $.tmpl( "question", data ).appendTo( answerset );
     $('.remove').click(function()
     {
        $(this).parents('.poll-question-answer').remove();
     });
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
            $(li).find('input[name$="[leading]"]').click( function()
            {
                if (jQuery(this).is(':checked'))
                {
                    $(li).find('input[name$="[hideOn][]"]').show();
                    $(li).find('label[for$="[hideOn][]"]').show();                    
                }
                else
                {
                    $(li).find('input[name$="[hideOn][]"]').hide();
                    $(li).find('label[for$="[hideOn][]"]').hide();
                }
            } );
            $('.autocomplete').autocomplete(
            {
                source:'/grade/poll/autocomplete',
                delay:10
            });
        }
        
    }
    $(answerset).find('.hideOnCheckbox').hide();
    Poll.section.toggleLeading();
    Poll.section.toggleHideOn();
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
 * Wywolanie tej metody powoduje wyswietlenie/ukrycie
 * pytania o uzycie 'pytania wiodacego'.
 * Pytanie jest pokazywane, jezeli pierwsza pozycja
 * jest typu 'single'
 *
 * @author mjablonski
 * */

Poll.section.toggleLeading = function( )
{
    var type = $(Poll.section.questionContainer)
                .find('select[name$="[type]"]')
                .first()
                .val();

    if ( type == 'single' )
    {
        $(".leading").show();

    }
    else
    {
        $(".leading").hide();
    }
}

/*
* Kolejna metoda obslugujaca pytania wiodace
* ukrywa / pokazuje przyciski obslugi wiodacych
*
* @author mjablonski
*
 */

Poll.section.toggleHideOn = function()
{

    var answerset = $(Poll.section.questionContainer)
                    .find('.answerset')
                    .first();
    if ( $('input[name$="[leading]"]:checked').val() !== undefined )
    {
        $(answerset).find('.hideOnCheckbox').show()
    }
    else
    {
        $(answerset).find('.hideOnCheckbox').hide();
    }
}