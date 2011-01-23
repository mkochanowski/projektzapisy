if (typeof Poll == 'undefined')
    Poll = new Object();﻿

Poll.section = Object();

Poll.section.init = function()
{
	Poll.section.questions         = 0;
    Poll.section.questionContainer = $("#poll-form");

	$("#add-question").click(Poll.section.addQuestion)
    $(Poll.section.questionContainer).sortable({handle : 'div'});
}

Poll.section.addQuestion = function()
{
	Poll.section.questions++;
    
    var type = 'open'
	var div  = document.createElement('div');
    var li   = document.createElement('li');
    var option_fieldset = document.createElement('fieldset');
    var answerset       = document.createElement('ul');
    $(answerset).addClass('answerset');

    option_fieldset.class = 'options';

	li.className = "poll-question";

    Poll.section.createQuestionPosition(div);
    Poll.section.createInput     (div, 'title', 'Podaj treść pytania');
    Poll.section.createCheckbox  (option_fieldset, 'required', 'Pytanie wymagane');
    Poll.section.breakLine(option_fieldset);

    var typeButton = Poll.section.createTypeSelect(option_fieldset);
    $(typeButton).click(function(){Poll.section.changeType(li, div)});

    $(div).append(option_fieldset);
    Poll.section.createTextArea  (div, 'description', 'Opis');
    $(div).append(answerset);
    Poll.section.createType(div, type);
    var save = Poll.section.createButton(div, 'Zapisz');
    var del = Poll.section.createButton(div, 'Usuń');
    $(save).click(function(){Poll.section.makeStandardView(li, div)});
    $(del).click(function(){ $(li).remove()});
    $(li).append(div);
   // Poll.section.makeStandardView(li, div);
    $(Poll.section.questionContainer).append(li);
    
    return li; 
}

Poll.section.changeType = function(parent, div)
{

    var answerset = $(div).children('.answerset');
    var optionset = $(div).children('fieldset');
    var oldType   = $(div).children('input[name$="[type]"]').val();
    var newType   = $(div).children('fieldset').children('.options').val();
    var id        = $(div).children('input[name="poll[question][order][]"]').val();

    $(div).children('input[name$="[type]"]').val(newType);
    if ( newType == 'open')
    {
        Poll.section.removeElement(optionset, 'hasOther');
        Poll.section.removeElement(optionset, 'choiceLimit');
        Poll.section.removeElement(optionset, 'isScale');
        $(div).children('button[name$="addQuestion"]').remove();        
        $(answerset).children().remove();
        // Poll.section.createCheckbox  (optionset, 'required', 'Pytanie wymagane');
    }
    else if ( newType == 'multi')
    {
        Poll.section.removeElement(optionset, 'isScale');
        if ( oldType != 'multi' )
        {  
            Poll.section.createIdCheckbox  (optionset, id, 'hasOther', 'Opcja inne');
            Poll.section.createIdInput     (optionset, id, 'choiceLimit', 'Liczba odpowiedzi');
        }

        if (oldType == 'open')
        {

            Poll.section.createAddOptionButton($(answerset).parent(), answerset, id);
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
        }
    }
    else
    {
        if ( oldType != 'single' )
        {
            Poll.section.createIdCheckbox  (optionset, id, 'isScale', 'Skala');
        }
        Poll.section.removeElement(optionset, 'hasOther');
        Poll.section.removeElement(optionset, 'choiceLimit');
        if (oldType == 'open')
        {
            Poll.section.createAddOptionButton($(answerset).parent(), answerset, id);
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
        }
    }
}

Poll.section.removeElement = function(element, name)
{
    var el  =  $(element).children('input[name$="['+ name +']"]');
    $(element).children('label[for="'+ $(el).attr('id') +'"]').remove()
    $(el).remove()
}

Poll.section.createTextArea = function(element, name, text)
{
    var area = document.createElement('textarea');
    area.name = 'poll[question]['+ Poll.section.questions  +'][description]';
    area.id   = area.name;
    var label = document.createElement('label');
    label.for = area.id
    $(label).text(text)
    $(element).append(label);
    $(element).append(area);
}

Poll.section.createTypeSelect = function(element)
{
    var select = document.createElement('select')
    select.class = 'typeSelect';
    Poll.section.createOption(select, 'open', 'Otwarte')
    Poll.section.createOption(select, 'single', 'Jednokrotnego wyboru')
    Poll.section.createOption(select, 'multi', 'Wielokrotnego wyboru')
    $(select).addClass('options');
    $(element).append(select);
    return Poll.section.createButton(element, 'Zmień');
}

Poll.section.breakLine = function(parent)
{
    var br = document.createElement('br');
    $(parent).append(br);
}

Poll.section.makeStandardView = function(parent, element)
{
    var div = document.createElement('div')
    div.class = 'aa'
    div.id    = 'aa'

    var id          = $(element).children('input[name="poll[question][order][]"]').val();
    var title       = $(element).children('input[name$="[title]"]').val();
    
    var description = $(element).children('textarea[name$="[description]"]').val();
    var required    = $(element).children('fieldset').children('input[name$="[required]"]').val();
    var type        = $(element).children('fieldset').children('input[name$="[type]"]').val();

    if ( required == 'on' )
    {
        title = title + ' <em>*</em>';
    }
    Poll.section.createElement(div, 'small', description);
    Poll.section.createElement(div, 'h2', title);
    if (type == 'open')
    {
        var textarea = document.createElement('textarea');
        $(div).append(textarea);
    }
    else
    {
        var option = $(element).children('.answerset').children('li');
        var ul     = document.createElement('ul');
        $.each(option, function(index, v)
        {
            var li    = document.createElement('li');
            var label = document.createElement('label');
            var txt   = $(v).children().val();
            $(label).text( txt );
            $(label).attr('for', 'poll[question][' + id + ']');
            var input = document.createElement('input');
            if( type == 'single' )
            {
                input.type = 'radiobox'
            }
            else
            {
                input.type = 'checkbox'
            }
            input.name = 'poll[question][' + id + ']';
            $(li).append(label);
            $(li).append(input);
            $(ul).append(li)
        });
        $(div).append(ul);
    }

    
    var button   = Poll.section.createButton(div, 'Edytuj');
    $(button).hide();
    $(button).click(function(){ $(element).show(); $(div).remove(); });
    $(div).append(button);
    $(div).mouseenter(function(){ $(button).show() });
    $(div).mouseleave(function(){ $(button).hide() });
    $(parent).append(div);
    $(element).hide();
}

Poll.section.createButton = function(parent, value)
{
    var button   = document.createElement('input');
    button.value = value;
    button.type  = 'button';
    $(parent).append(button);
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

Poll.section.createInput = function(question, varname, text)
{
    Poll.section.createBaseElement('text', Poll.section.questions, question, varname, text)
}

Poll.section.createIdInput = function(question, id, varname, text)
{
    Poll.section.createBaseElement('text', id, question, varname, text)
}

Poll.section.createIdRadiobox = function(question, id,  varname, text)
{
    Poll.section.createBaseElement('radio', id, question, varname, text)
}

Poll.section.createIdCheckbox = function(question, id,  varname, text)
{
    Poll.section.createBaseElement('checkbox', id, question, varname, text)
}

Poll.section.createCheckbox = function(question, varname, text)
{
    Poll.section.createBaseElement('checkbox', Poll.section.questions, question, varname, text)
}

Poll.section.createBaseElement = function(type, id, question, varname, text)
{
    var label = document.createElement('label')
    $(label).attr('for', 'poll[question][' + id + '][' + varname +']');
    $(label).text(text)

    $(question).append(label)

    var checkbox  = document.createElement('input')
    checkbox.type = type
    checkbox.id   = 'poll[question][' + id + '][' + varname +']'
    checkbox.name = 'poll[question][' + id + '][' + varname +']'

    $(question).append(checkbox)
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

Poll.section.createAddOptionButton = function(elem, set, id)
{
    var button = document.createElement('input')
    button.type = 'button';
    button.name = 'addQuestion';
    $(button).val('Dodaj odpowiedź');
    $(button).click(function()
    {
        Poll.section.createAnswer(set, id, 'odpowiedź');
    });
    $(elem).append(button);
}

Poll.section.createAnswer = function(ul, id, value)
{
	var li = document.createElement('li');
    li.className = 'poll-question-answer';
	var answer = document.createElement('input');
    answer.name =  'poll[question][' + id + '][answers][]';
    answer.type = 'text'
    $(answer).val(value);

	$(li).append(answer);
	$(ul).append(li);
}


Poll.section.createType = function(question, type_name)
{	
	var type = document.createElement('input');
    type.type = 'hidden'
    $(type).val(type_name);
    type.name = 'poll[question][' + Poll.section.questions + '][type]';

    $(question).append(type);
}


$(Poll.section.init);


