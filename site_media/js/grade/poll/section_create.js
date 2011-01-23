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
    var optionset       = document.createElement('ul');
    $(answerset).addClass('answerset');

    option_fieldset.class = 'options';

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
    var isLeading   = Poll.section.createSectionOption('isLeading', 'checkbox', 'Pytanie wiodące')
    var isScale     = Poll.section.createSectionOption('isScale', 'checkbox', 'Odpowiedź w formie skali')
    var choiceLimit = Poll.section.createSectionOption('choiceLimit', 'text', 'Limit odpowiedzi')
    var hasOther    = Poll.section.createSectionOption('hasOther', 'checkbox', 'Odpowiedź inne')


    $(optionset).append(isLeading)
    $(optionset).append(isScale)
    $(optionset).append(choiceLimit)
    $(optionset).append(hasOther)

    $(isLeading).hide();
    $(isScale).hide();
    $(choiceLimit).hide();
    $(hasOther).hide();

    $(li).append(table);
    $(li).append(answerset);
    $(li).append(optionset);
    $(Poll.section.questionContainer).append(li);


    $(isLeading).change(function() {   $(answerset).children().children('.hideOnCheckbox').toggle() } );
    $(li).mouseover(function(){ $(li).addClass('section-mouseover'); });
    $(type).change(function(){Poll.section.changeType(li, type, answerset, isLeading, isScale, choiceLimit, hasOther)});
    
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

Poll.section.changeType = function(parent, type, answerset, isLeading, isScale, choiceLimit, hasOther)
{
    var id = $(parent).children('input[name="poll[question][order][]"]').val();
    if ($(type).val() != 'open')
    {
        if ( $(answerset).children().size() == 0 )
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
            Poll.section.createAddOptionButton(parent, answerset, id);
        }
    }
    else
    {
        $(parent).children('input[name$="addQuestion"]').remove();        
        $(answerset).children().remove();
    }

    if ($(type).val() == 'single')
    {
        $(isLeading).parent().children('label').show();
        $(isLeading).show();
        $(isScale).show();
        $(choiceLimit).hide();
        $(hasOther).show();


    }
    else if ($(type).val() == 'multi')
    {
        $(isLeading).hide();
        $(isLeading).parent().children('label').hide();
        $(answerset).children().children('.hideOnCheckbox').hide()
        $(isScale).hide();
        $(choiceLimit).show();
        $(hasOther).show();

    }
    else
    {
        $(isLeading).hide();
        $(isLeading).parent().children('label').hide();
        $(answerset).children().children('.hideOnCheckbox').hide()
        $(isScale).hide();
        $(choiceLimit).hide();
        $(hasOther).hide();
    }

}

/*
Poll.section.changeType = function(parent, div, type, answerset)
{

    var optionset = $(div).children('fieldset');
    var oldType   = $(div).children('input[name$="[type]"]').val();
    var newType   = $(type).val();
    var id        = 2//$(div).children('input[name="poll[question][order][]"]').val();

    $(div).children('input[name$="[type]"]').val(newType);
    alert(newType);
    if ( newType == 'open')
    {
/        Poll.section.removeElement(optionset, 'hasOther');
        Poll.section.removeElement(optionset, 'choiceLimit');
        Poll.section.removeElement(optionset, 'isScale');
        $(div).children('input[name$="addQuestion"]').remove();        
/
        $(answerset).children().remove();
        // 
    }
    else if ( newType == 'multi')
    {
        Poll.section.removeElement(optionset, 'isScale');
        if ( oldType != 'multi' )
        {  
        }

        if (oldType == 'open')
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
            Poll.section.createAddOptionButton($(answerset).parent(), answerset, id);

        }
    }
    else
    {
//        if ( oldType != 'single' )
  //      {
    //
      //  }
        //Poll.section.removeElement(optionset, 'hasOther');
        ///Poll.section.removeElement(optionset, 'choiceLimit');
        if (oldType == 'open')
        {
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
            Poll.section.createAddOptionButton($(answerset).parent(), answerset, id);
            Poll.section.createAnswer(answerset, id, 'odpowiedź');
        }
    }
}
*/
Poll.section.removeElement = function(element, name)
{
    var el  =  $(element).children('input[name$="['+ name +']"]');
    $(element).children('label[for="'+ $(el).attr('id') +'"]').remove()
    $(el).remove()
}

Poll.section.createTextArea = function(name)
{
    var area = document.createElement('textarea');
    $(area).attr(
    {
        name: 'poll[question]['+ Poll.section.questions  +'][description]',
        id: 'poll[question]['+ Poll.section.questions  +'][description]'
    });
    return area;
}

Poll.section.createTypeSelect = function()
{
    var select = document.createElement('select')
    $(select).attr('name', 'poll[question][' + Poll.section.questions + '][type]');
    Poll.section.createOption(select, 'open', 'Otwarte')
    Poll.section.createOption(select, 'single', 'Jednokrotnego wyboru')
    Poll.section.createOption(select, 'multi', 'Wielokrotnego wyboru')
    $(select).addClass('typeSelect');
    $(select).addClass('options');
    return select;
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

Poll.section.createInput = function(varname, text)
{
    return Poll.section.createBaseElement('text', Poll.section.questions, varname, text)
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
	var li     = document.createElement('li');
    var check  = document.createElement('input');
	var answer = document.createElement('input');

    li.className = 'poll-question-answer';
    answer.name =  'poll[question][' + id + '][answers][]';
    answer.type = 'text'

    check.type = 'checkbox'
    check.name =   'poll[question][' + id + '][hideOn][]';
    $(check).val( $(ul).children().size() + 1 )
    $(check).addClass('hideOnCheckbox');
    $(check).hide();  
    
    $(answer).val(value);
    
	$(li).append(answer);
    $(li).append(check);
	$(ul).append(li);
}



$(Poll.section.init);


