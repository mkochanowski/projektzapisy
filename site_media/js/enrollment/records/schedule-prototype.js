
function addSubject(id) {
	$('.'+id).each(function(){
		var content = $(this).html(), 
			day = $(this).attr('day'), 
			from = $(this).attr('from'), 
			minutes = $(this).attr('minutes'), 
			subjectID = $(this).attr('subjectID'), 
			groupID = $(this).attr('groupID');
			termID = $(this).attr('termID');

		$('#schedule-wrapper').schedule('addTerm', content, day, from, minutes, subjectID, groupID, termID );
	});
}

function removeSubject(subjectid) {
	$('#schedule-wrapper').schedule('deleteSubjectTerms', subjectid );
}
	
$(function(){
	$('#schedule-wrapper').schedule({
		hourColumnWidth: 40,
		dayColumnWidth: Math.floor(($('#schedule-wrapper').width() - 100)/5),
		messageBoxId: 'schedule-message'
	});
	
	$('.schedule-prototype-subject').click(function(){
		
		if($(this).hasClass('schedule-prototype-subject-hide')){
			$(this).removeClass('schedule-prototype-subject-hide')
			removeSubject($(this).attr('subjectid'));
		}
		else {
			$(this).addClass('schedule-prototype-subject-hide');
			addSubject($(this).attr('id'));
		}
		
	});
	
	$('#btnAssignToAll').click(function(){
		$('#schedule-wrapper').schedule('tryAssignToPinned');
	});

});