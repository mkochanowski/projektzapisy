if (typeof Poll == 'undefined')
    Poll = new Object();﻿

Poll.section = Object();

Poll.section.init = function()
{
    Poll.section.submitted         = false;
	Poll.section.questions         = 0;
    Poll.section.questionContainer = $("#poll-form");

	$("#add-question").click(Poll.section.addQuestion)
    $("input[type=text]").focus(function(){
        // Select field contents
        this.select();
    });
    $("textarea").focus(function(){
        this.select();
    });
    $(Poll.section.questionContainer).sortable({handle : 'div'});
    $('#questionset-submit').click(function()
    {
        if( Poll.section.submitted )
        {
            return false;
        }
        Poll.section.submitted = true;
    })
	
}

Poll.section.addQuestion = function()
{
	Poll.section.questions++;
    
    var type            = 'open'
	var div             = document.createElement('div');
    var li              = document.createElement('li');
    var answerset       = document.createElement('ul');
    var optionset       = document.createElement('ul');
    $(answerset).addClass('answerset');


	li.className = "poll-question";

    Poll.section.createQuestionPosition(li);

    var table = document.createElement('table');
    var tbody = document.createElement('tbody');

    var title = Poll.section.createInput     ('title', 'Podaj treść pytania');
    var desc  = Poll.section.createInput     ('description', '');
    var type  = Poll.section.createTypeSelect();

    Poll.section.createTr(tbody, title, 'Podaj treść pytania: ')
    Poll.section.createTr(tbody, desc,  'Opis pytania: ')
    Poll.section.createTr(tbody, type,  'Typ pytania: ')
    
    $(table).append(tbody);
    var isScale     = Poll.section.createSectionOption('isScale', 'checkbox', 'Odpowiedź w formie skali')
    var choiceLimit = Poll.section.createSectionOption('choiceLimit', 'text', 'Limit odpowiedzi')
    var hasOther    = Poll.section.createSectionOption('hasOther', 'checkbox', 'Odpowiedź inne')



    $(optionset).append(isScale)
    $(optionset).append(choiceLimit)
    $(optionset).append(hasOther)
    $(optionset).addClass('optionset')

    $(answerset).sortable({handle : 'input'});

    $(isScale).hide();
    $(choiceLimit).hide();
    $(hasOther).hide();

    $(div).append(table);
    $(div).append(answerset);
    $(div).append(optionset);
    $(li).append(div);
    $(Poll.section.questionContainer).append(li);

    var ready = Poll.section.createButton('Gotowe', 'section-question-ready');
    var del   = Poll.section.createButton('Usuń',   'section-question-delete');

    $(div).append(ready);
    $(div).append(del);

    $(ready).click(function()
    { 
        $(div).removeClass('section-edit');
        $(div).addClass('section-show');
        Poll.section.makeStandardView(li, div, type);
    });
    $(del).click(function()
    {
        Poll.section.remove(li);
    });
    $(li).mouseover(function(){ $(div).addClass('section-mouseover'); });
    $(type).change(function(){Poll.section.changeType(div, type, answerset, isScale, choiceLimit, hasOther)});
    

    $(div).addClass('section-edit');
    return li; 
}

Poll.section.createTr = function(parent, element, label)
{
    var tr       = document.createElement('tr')
    var td_label = document.createElement('td')
    var td_value = document.createElement('td')

    $(td_label).text(label)
    $(td_value).append(element)
    $(tr).append(td_label);
    $(tr).append(td_value);
    $(parent).append(tr);
   
}

Poll.section.createSectionOption = function(name, type, text)
{
    var li    = document.createElement('li');
    var label = document.createElement('label');
    var input = document.createElement('input');
    var id = 'poll[question][' + Poll.section.questions + '][' + name +']'

    $(input).attr(
    {
        id: id,
        name: id,
        type: type
    }
    );

    $(label).attr(
    {
        for: id
    });
    $(label).text(text);

    $(li).append(input);
    $(li).append(label);
    return li;
}

Poll.section.changeType = function(parent, type, answerset, isScale, choiceLimit, hasOther)
{
    var id = $(parent).parent().children('input[name="poll[question][order][]"]').val();
    if ($(type).val() == 'single')
    {
        $(answerset).children('li').children('.hideOnCheckbox, label').hide();
        $(isScale).show();
        $(choiceLimit).hide();
        $(hasOther).hide();
        if ( $(answerset).children().size() == 0 )
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź', type);
            Poll.section.createAddOptionButton(parent, answerset, id, type);
        }

    }
    else if ($(type).val() == 'multi')
    {
        //$(isLeading).parent().children('label').hide();
        $(answerset).children('li').children('.hideOnCheckbox, label').hide();
        $(isScale).hide();
        $(choiceLimit).show();
        $(hasOther).show();
        if ( $(answerset).children().size() == 0 )
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź', type);
            Poll.section.createAddOptionButton(parent, answerset, id, type);
        }
    }
    else if ($(type).val() == 'leading')
    {

        $(isScale).show();
        $(choiceLimit).hide();
        $(hasOther).hide();
        if ( $(answerset).children().size() == 0 )
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź', type );
            Poll.section.createAddOptionButton(parent, answerset, id, type );
        }
        $(answerset).children('li').children().show();
    }
    else
    {
        $(answerset).children('li').children('.hideOnCheckbox, label').hide();
        $(isScale).hide();
        $(choiceLimit).hide();
        $(hasOther).hide();
        $(parent).children('input[name$="addQuestion"]').remove();        
        $(answerset).children().remove();
    }
}

Poll.section.removeElement = function(element, name)
{
    var el  =  $(element).children('input[name$="['+ name +']"]');
    $(element).children('label[for="'+ $(el).attr('id') +'"]').remove()
    $(el).remove()
}


Poll.section.createTypeSelect = function()
{
    var select = document.createElement('select')
    $(select).attr('name', 'poll[question][' + Poll.section.questions + '][type]');
    Poll.section.createOption(select, 'open', 'Otwarte')
    Poll.section.createOption(select, 'single', 'Jednokrotnego wyboru')
    Poll.section.createOption(select, 'multi', 'Wielokrotnego wyboru')
    Poll.section.createOption(select, 'leading', 'Pytanie wiodące')
    $(select).addClass('typeSelect');
    $(select).addClass('options');
    return select;
}

Poll.section.makeStandardView = function(parent, element, question_type)
{
    var div = document.createElement('div')
    $(div).addClass('section-show').addClass('poll-section-field')

    var id          = $(parent).children('input[name="poll[question][order][]"]').val();
    var title       = $(element).children('table') .children('tbody') .children('tr') .children('td').children( 'input[name$="[title]"]').val();
    var description = $(element).children('table') .children('tbody') .children('tr') .children('td').children('input[name$="[description]"]').val();
    var choice_limit = parseInt( $(element).find('input[name$="[choiceLimit]"]').val() )
    var type        = $(question_type).val();

    Poll.section.createElement(div, 'h2', title);
    Poll.section.createElement(div, 'small', description);
    $(div).append( document.createElement('br') )
	if( type == 'multi')
    {
    	if( choice_limit > 0)
    	{
    		var html = $(div).html()
    		$(div).html( html + '<span class="poll-section-description">Możesz podać maksymalnie '+ choice_limit +' odpowiedzi</span>')
    	}
    		
    }
    if (type == 'open')
    {
        var textarea = document.createElement('textarea');
        $(textarea).attr({
        	'cols': 40,
        	'rows': 5
        });
        $(div).append(textarea);
    }
    else
    {
    	
        var option = $(element).children('.answerset').children('li');
        var ul     = document.createElement('ul');
        $(ul).addClass('poll-section-answer-list');
        
        $.each(option, function(index, v)
        {
            var li    = document.createElement('li');
            $(li).addClass('poll-section-answer-item');
            
            var label = document.createElement('label');
            var txt   = $(v).children().val();
            $(label).text( txt );
            $(label).attr('for', 'poll[question][' + id + ']');
            var input = document.createElement('input');
            if( type == 'single' )
            {
                input.type = 'radio'
                $(input).addClass('poll-section-radio');
            }
            else
            {
                input.type = 'checkbox'
                $(input).addClass('poll-section-choice');
            }
            input.name = 'poll[question][' + id + ']';
            $(input).attr({'id': input.name })
            $(li).append(input);
            $(li).append(label);

            $(ul).append(li)
        });
        if( type == 'multi')
        {
        	var other = $(element).children('.optionset').find('input[name$="[hasOther]"]')
        	if ($(other).attr('checked'))
        	{
        		var input = document.createElement('input');
            	var li    = document.createElement('li');
            	var label = document.createElement('label');
            	
            	$(label).text('Inne')
				input.type = 'checkbox'
				$(input).addClass('poll-section-choice');
	            $(li).append(input);
	            $(li).append(label);

	            $(ul).append(li)        		 
        	}
        }
        $(div).append(ul);
        
    }

    
    var button   = Poll.section.createButton('Edytuj', 'section-button-edit');
    $(button).hide();
    $(button).click(function(){ $(element).show(); $(div).remove(); });
    $(div).append(button);
    $(div).mouseenter(function(){ $(button).show() });
    $(div).mouseleave(function(){ $(button).hide() });
    $(parent).append(div);
    $(element).hide();
}

Poll.section.createButton = function(value, class)
{
    var button   = document.createElement('input');
    button.value = value;
    button.type  = 'button';
    button.class = ''
    return button;
}

Poll.section.createElement = function(parent, type, text)
{
    var element = document.createElement(type)
    $(element).html(text)
    $(parent).append(element)
}


Poll.section.createQuestionPosition = function(elem)
{
    var hidden   = document.createElement('input')
    hidden.type  = 'hidden'
    hidden.name  = 'poll[question][order][]'
    hidden.value = Poll.section.questions;
    $(elem).append(hidden)
}

Poll.section.createOption = function(select, value, text)
{
    var option = document.createElement('option')
    option.value = value
    $(option).text(text)
    $(select).append(option)
    return option
}

Poll.section.createInput = function(varname, text)
{
    var input = Poll.section.createBaseElement('text', Poll.section.questions, varname, text)
    $(input).addClass('section-option');
    return input;
}

Poll.section.createIdInput = function(id, varname, text)
{
    return Poll.section.createBaseElement('text', id, varname, text)
}

Poll.section.createIdRadiobox = function(id,  varname, text)
{
    return Poll.section.createBaseElement('radio', id, varname, text)
}

Poll.section.createIdCheckbox = function(id,  varname, text)
{
    return Poll.section.createBaseElement('checkbox', id, varname, text)
}

Poll.section.createCheckbox = function(varname, text)
{
    return Poll.section.createBaseElement('checkbox', Poll.section.questions, varname, text)
}

Poll.section.createBaseElement = function(type, id, varname, text)
{
    var checkbox  = document.createElement('input')
    checkbox.type = type
    checkbox.id   = 'poll[question][' + id + '][' + varname +']'
    checkbox.name = 'poll[question][' + id + '][' + varname +']'

    return checkbox
}

Poll.section.createOptionSet = function(question)
{
    var ul = document.createElement('ul');
	ul.id = 'Question' + Poll.section.questions;
	ul.className = 'poll-question-answers';

    $(question).append(ul);
    
    Poll.section.createOption(ul);
    Poll.section.createAddOptionButton(question, ul)
}

Poll.section.createAddOptionButton = function(elem, set, id, type)
{
    var button = document.createElement('input')
    button.type = 'button';
    button.name = 'addQuestion';
    $(button).val('Dodaj odpowiedź');
    $(button).click(function()
    {
        Poll.section.createAnswer(set, id, 'odpowiedź', type);
    });
    $(set).after(button);
}

Poll.section.createAnswer = function(ul, id, value, type)
{
	var li     = document.createElement('li');
    var check  = document.createElement('input');
	var answer = document.createElement('input');
    var label  = document.createElement('label');

    li.className = 'poll-question-answer';
    answer.name =  'poll[question][' + id + '][answers][]';
    answer.type = 'text'

    check.type = 'checkbox'
    check.name =   'poll[question][' + id + '][hideOn][]';

    $(check).attr('id', check.name);
    $(check).val( $(ul).children().size() + 1 )
    $(check).addClass('hideOnCheckbox');
    $(check).css('display', 'inline');

    $(label).attr(
    {
        for: check.name,
    });    

    $(label).text('Ukryj sekcję');
    $(label).css('display', 'inline');

    if( $(type).val() != 'leading')
    {
        $(label).hide();
        $(check).hide();  
    }

    $(answer).val(value);
    $(answer).addClass('autocomplete')
    $(answer).autocomplete(
    	{
    	 source:'http://localhost:8000/grade/poll/autocomplete',
         delay:10
     }
	);
    var sectionRemoveButton = document.createElement('img');
    sectionRemoveButton.alt = 'usuń';
    sectionRemoveButton.className = 'remove';
    sectionRemoveButton.src = '/site_media/images/remove-ico.png';

    $(sectionRemoveButton).click(function()
    {
        Poll.section.removeQuestion( li );
    });
	$(li).append( answer );
    $(li).append( check );
    $(li).append( label );
    $(li).append( sectionRemoveButton )
	$(ul).append( li );
}


Poll.section.removeQuestion = function( element )
{
    $(element).remove();
}

Poll.section.remove = function ( element )
{
    $(element).remove();
}

$(Poll.section.init);


