if (typeof Poll == 'undefined'){
    Poll = new Object();﻿
}
Poll.section = Object();

Poll.section.init = function()
{
    Poll.section.submitted         = false;
    Poll.section.questions         = 0;
    Poll.section.questionContainer = $("#poll-form");
    Poll.section.havelastLi        = false;
    $("#add-question").click(Poll.section.createQuestion)
    $("input[type=text]").focus(function(){
        this.select();
    });
    $("textarea").focus(function(){
        this.select();
    });
    $(Poll.section.questionContainer).sortable({handle : 'div', zIndex: 5, tolerance: 'pointer' });
    $('#questionset-submit').click(function()
    {
        if( Poll.section.submitted )
        {
            return false;
        }
        Poll.section.submitted = true;
    })
    Poll.section.editParser();
    
    $("form").keypress(function(e)
    {
          if (e.which == 13)
          {
            return false;
          }
    });
}

Poll.section.editParser = function()
{
    $('.autocomplete').each(function()
    {
        $(this).autocomplete(
        {
         source:'http://localhost:8000/grade/poll/autocomplete',
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
        Poll.section.addQuestion( li );
    });
    $('.delete-answer').click(function(){

         $(this).parents('.poll-question-answer').remove();
    })
}

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
     Poll.section.lastLi = $(Poll.section.questionContainer).find('.poll-question').last();
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

Poll.section.createView = function( li )
{

    Poll.section.havelastLi = false;
    var data = {
        type:  $(li).find('select[name$="[type]"]').val(),
        title: $(li).find('input[name$="[title]"]').val(),
        desc:  $(li).find('input[name$="[description]"]').val(),
        questionset: Poll.section.questionset( li ),
        optionset: Poll.section.optionset( li )
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

Poll.section.questionset = function( li )
{
    var questions = new Array();
    $(li).find('.poll-question-answer').children('div').each(function()
                {
                 questions.push({
                                   title:  $(this).find('input[name$="[answers][]"]').val(),
                                   isHiden: $(this).find('input[name$="[hideOn][]"]').val()
                                   })
                });
    return questions;
    
}

Poll.section.optionset = function( li )
{
    return {
        isScale: $(li).find('input[name$="[isScale]"]').val(),
        choiceLimit: $(li).find('input[name$="[choiceLimit]"]').val(),
        hasOther: $(li).find('input[name$="[hasOther]"]').val()
    }
}

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
            Poll.section.addQuestion( li );
            
            $.tmpl( "question_add", data ).insertAfter( answerset );
            $('.addQuestion').click(function()
            {
                var li = $(this).parents('.poll-question');
                Poll.section.addQuestion( li );
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
            if(($(li).find('input[name$="[leading]"]:checked').val() !== undefined))
            {
                if(type !='single')
                {
                 $(answerset).find('input[name$="[hideOn][]"]').hide();
                 $(answerset).find('label[for$="[hideOn][]"]').hide();
                } else
                {
                  $(answerset).find('input[name$="[hideOn][]"]').show();
                 $(answerset).find('label[for$="[hideOn][]"]').show();
                
                }
            } 
        
    }
}

Poll.section.addQuestion = function( li )
{
     var type      = $(li).find('select[name$="[type]"]').val();
     var answerset = $(li).find('.answerset');
     var data = {
        id: $(li).find('input[name="poll[question][order][]"]').val(),
                size: $(answerset).children().size() + 1
     }
     $.tmpl( "question", data ).appendTo( answerset );
     $('.remove').click(function()
     {
        $(this).parents('.poll-question-answer').remove();
     });
     
     if( (type == 'single') && ($(li).find('input[name$="[leading]"]:checked').val() !== undefined))
     {
         $(answerset).find('input[name$="[hideOn][]"]').show();
         $(answerset).find('label[for$="[hideOn][]"]').show();
     }
     else
     {
         $(answerset).find('input[name$="[hideOn][]"]').hide();
         $(answerset).find('label[for$="[hideOn][]"]').hide();
     }
}

Poll.section.hideOptions = function( li, type )
{

    var isScale     = $(li).find('.isScale');
    var hasOther    = $(li).find('.hasOther');
    var choiceLimit = $(li).find('.choiceLimit');
    var leading     = $(li).find('.leading');
    
    if (type == 'single')
    {
        $(isScale).show();
        $(leading).show();
        $(choiceLimit).hide();
        $(hasOther).hide()
    }
    else if (type == 'multi')
    {
        $(isScale).hide();
        $(leading).hide();
        $(choiceLimit).show();
        $(hasOther).show();
    }
    else if (type == 'open')
    {
        $(isScale).hide();
        $(leading).hide();
        $(choiceLimit).hide();
        $(hasOther).hide();
    }
    else
    {
        $(isScale).show();
        $(choiceLimit).hide();
        $(hasOther).hide();
        $(leading).hide();
    }
}


$(Poll.section.init);


