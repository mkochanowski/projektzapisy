var question_edit = "<li class='poll-question'>                         " +
"	<input type='hidden' name='poll[question][order][]' value='${id}'>  " +
"	<div class='section-edit section-mouseover'>                        " +
"	<table>         " +
"		<tbody>     " +
"			<tr>    " +
"				<td>Podaj treść pytania: </td>" +
"				<td><input type='text' id='poll[question][${id}][title]' name='poll[question][${id}][title]' class='section-option'></td>" +
"			</tr>" +
"			<tr> " +
"				<td>Opis pytania: </td>" +
"				<td><input type='text' id='poll[question][${id}][description]' name='poll[question][${id}][description]' class='section-option'></td>" +
"			</tr>" +
"			<tr  class='typeSelect'>" +
"				<td>Typ pytania: </td>" +
"				<td>" +
"                   <input type='hidden' name='poll[question][${id}][type]' value='open'>" +
"                   <select name='poll[question][${id}][faketype]' class='typeSelect options'>" +
"				    </select>" +
"				</td>" +
"			</tr>" +
"		</tbody>" +
"	</table>" +
"	<ul class='answerset ui-sortable' style=''></ul>" +
"	<ul class='optionset'>" +
"		<li class='isScale optionss' style='display: none;'>" +
"			<input type='checkbox' id='poll[question][${id}][isScale]' class='scale' name='poll[question][${id}][isScale]'>" +
"			<label for='poll[question][${id}][isScale]'>Odpowiedź w formie skali</label>" +
"		</li>" +
"		<li class='choiceLimit optionss' style='display: none;'>" +
"			<input type='text' id='poll[question][${id}][choiceLimit]' name='poll[question][${id}][choiceLimit]'>" +
"			<label for='poll[question][${id}][choiceLimit]'>Limit odpowiedzi</label>" +
"		</li>" +
"		<li class='hasOther optionss' style='display: none;'>" +
"			<input type='checkbox' id='poll[question][${id}][hasOther]' name='poll[question][${id}][hasOther]'>" +
"			<label for='poll[question][${id}][hasOther]'>Odpowiedź inne</label>" +
"		</li>" +
"	</ul>" +
"	<input class='ready' type='button' value='Gotowe'><input class='delete' type='button' value='Usuń'>" +
"	</div>" +
"</li>"

$.template( "question_edit", question_edit );