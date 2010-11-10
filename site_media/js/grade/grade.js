

FormGenerator = Object();

FormGenerator.init = function()
{
	FormGenerator.questions = 0;
        FormGenerator.form      = $("#pool-form");
	$("#add-question").click ( function(){
		FormGenerator.addQuestion(); }
	)
}

FormGenerator.addQuestion = function()
{
	FormGenerator.questions++;

	var question_type = $("#add-question-type").val();
	var type = document.createElement('input');
	    type.type = 'hidden'
	    type.value = question_type;
	    type.name = 'pool[' + FormGenerator.questions + '][type]';


	// jezeli typ to pytanie otwarte:


	// jezeli nie:

	var div = document.createElement('div');
	    div.id = 'Question' + FormGenerator.questions;
	
	var title = document.createElement('input');
	    title.type = 'text';
            title.name = 'pool[' + FormGenerator.questions + '][title]';
	    title.value = 'Wpisz pytanie';
	if (question_type != 'Otwarte')
	{	
		divAnswer = document.createElement('div');
		divAnswer.className = 'Answers';

		var answer = document.createElement('input');
		    title.type = 'text';
		    answer.name =  'pool[' + FormGenerator.questions + '][answers][]';
		    answer.value = 'odpowiedź';

		$(divAnswer).append (answer);
	}
	var ok =  document.createElement('button');
	    ok.value = 'dodaj';
	  $(ok).click(function(){FormGenerator.addOption ( FormGenerator.questions )}); 
	// dodac event

	$(div).append (type);
	$(div).append (title);
	if (question_type != 'Otwarte') { $(div).append (divAnswer); }
	$(div).append (ok);
	FormGenerator.form.append (div);
	
}

FormGenerator.addOption = function( question )
{
	var answer = document.createElement('input');
	    answer.name =  'pool[' + question + '][answers][]';
	    answer.value = 'odpowiedź';

	$('#Question' + question + ' .Answers').append(answer);
	
	// bierzemy pytanie
	// dodajemy pole
}

$(FormGenerator.init);


