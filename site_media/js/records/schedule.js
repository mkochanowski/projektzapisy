
$(function(){
	$('.schedule-table-simple tr:even').addClass('even');
	$('#schedule-wrapper').schedule({
		hourColumnWidth: 40,
		dayColumnWidth: Math.floor(($('#schedule-wrapper').width() - 140)/6),
		dayList: ['Poniedzialek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota']});
});