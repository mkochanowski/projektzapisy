var question_view = "<div class='section-show poll-section-field' style='position:relative'>" +
"	<input class='edit-mode' type='button' value='Edytuj'>" + 
"	<h2>${title}</h2>" +
"	<small>${desc}</small><br>" +
"	{{if type === 'multi' }}" + 
"		<span class='poll-section-description'>Możesz podać maksymalnie ${optionset.choiceLimit} odpowiedzi</span>	" +
"	{{/if}} " +
"	{{if type === 'open'}}" +
"   	<textarea cols='40' rows='5' disabled='disabled'></textarea>	" +
"	{{else}}	" +
"	<ul class='poll-section-answer-list'>	" +
"	{{each(i, question) questionset}}	" +
"		<li class='poll-section-answer-item'>	" +
"			<input type={{if type === 'multi'}}'checkbox'{{else}}'radio'{{/if}} class='poll-section-choice' id='poll[question][${i}]'  disabled='disabled'>" +
"			<label for='poll[question][${i}]'>${question.title}</label>" +
"		</li>" +
"	{{/each}}" +
"	</ul>" +
"	{{/if}}" +
"</div>";

$.template( "question_view", question_view );