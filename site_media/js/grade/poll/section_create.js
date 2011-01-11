if (typeof Poll == 'undefined')
    Poll = new Object();﻿

Poll.section = Object();

Poll.section.init = function()
{
	Poll.section.questions         = 0;
    Poll.section.questionContainer = $("#poll-form");

	$("#add-question").click(function()
    {
		Poll.section.addQuestion();
    })
}

Poll.section.addQuestion = function()
{
	Poll.section.questions++;
    var type = $("#add-question-type").val();	
    switch(type)
    {
        case 'open':
            Poll.section.createOpenQuestion();
        break;

        case 'single':
            Poll.section.createSingleQuestion();
        break;

        case 'multi':
            Poll.section.createMultiQuestion()
        break;
    }	
}

Poll.section.createQuestion = function()
{
    
	var li = document.createElement('li');
	li.className = "poll-question";

    Poll.section.createQuestionPosition(li);
    Poll.section.createInput(li, 'title', 'Podaj treść pytania');
    Poll.section.createType(li);
    $(Poll.section.questionContainer).append(li);
    return li;    
}


Poll.section.createOpenQuestion = function()
{
    var question = Poll.section.createQuestion()
}

Poll.section.createSingleQuestion = function()
{
    var question = Poll.section.createQuestion()
    Poll.section.createCheckbox(question, 'isScale', 'Odpowiedź w skali')
    Poll.section.createCheckbox(question, 'isLeading', 'Pytanie wiodące')
    Poll.section.createOptionSet(question);
}

Poll.section.createMultiQuestion = function()
{
    var question = Poll.section.createQuestion();
    Poll.section.createCheckbox(question, 'hasOther', 'Opcja inne');
    Poll.section.createInput(question, 'choice_limit', 'Maksymalnie odpowiedzi');
    Poll.section.createOptionSet(question);
}

Poll.section.createQuestionPosition = function(elem)
{
    var hidden   = document.createElement('input')
    hidden.type  = 'hidden'
    hidden.name  = 'poll[question][order][]'
    hidden.value = Poll.section.questions;
    $(elem).append(hidden)
}

Poll.section.createInput = function(question, varname, text)
{
    Poll.section.createElement('input', question, varname, text)
}

Poll.section.createCheckbox = function(question, varname, text)
{
    Poll.section.createElement('checkbox', question, varname, text)
}

Poll.section.createElement = function(type, question, varname, text)
{
    var label = document.createElement('label')
    label.for  = 'poll[question][' + Poll.section.questions + '][' + varname +']'
    $(label).text(text)

    $(question).append(label)

    var checkbox = document.createElement('input')
    checkbox.type = type
    checkbox.name = 'poll[question][' + Poll.section.questions + '][' + varname +']'

    $(question).append(checkbox)
}

Poll.section.createOptionSet = function(question)
{
    var ul = document.createElement('ul');
	ul.id = 'Question' + Poll.section.questions;
	ul.className = 'poll-question-answers';

    $(question).append(ul);
    
    Poll.section.createOption(ul);

    $(question).append(ul);

    Poll.section.createAddOptionButton(question, ul)
}

Poll.section.createAddOptionButton = function(elem, set)
{
    var button = document.createElement('button')
    button.type = 'button';
    $(button).text('Dodaj odpowiedź');
    $(button).click(function()
    {
        Poll.section.createOption(set);
    });
    $(elem).append(button);
}

Poll.section.createOption = function(ul)
{
	var li = document.createElement('li');
    li.className = 'poll-question-answer';
	var answer = document.createElement('input');
    answer.name =  'poll[question][' + Poll.section.questions + '][answers][]';
    answer.value = 'odpowiedź';

	$(li).append(answer);
	$(ul).append(li);
}


Poll.section.createType = function(question)
{
	var question_type = $("#add-question-type").val();	
	var type = document.createElement('input');
	    type.type = 'hidden'
	    type.value = question_type;
	    type.name = 'poll[question][' + Poll.section.questions + '][type]';
    $(question).append(type);
}


$(Poll.section.init);


