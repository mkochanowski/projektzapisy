function ajaxSuccessCallBack(data) {
	var list = $("#schedule-prototype-subject-list").text('');

	$.each(data.subjects, function(i,item){
       	var $sub = $('<li></li>')
		   	.addClass('schedule-prototype-subject')
			.attr({'id':'subject'+ item.id, 'subjectid' : item.id })
			.append($('<span>'+item.entity__name+'</span>'))
			.append($('<span class="hide">&nbsp;Schowaj</span>'))
			.appendTo(list);
   	});
	
	var sub = $('#schedule-wrapper').schedule('subjectsOnSchedule');
	for(var i = 0; i<sub.length; i++)
	{
		$('#schedule-prototype-subject-list li[subjectid='+sub[i]+']').each(function(){
			$(this).css({'color':'gray'});
		});
	}
	
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
	
	var sem_id = $('#semester').val() || 0;
	$('#schedule-wrapper').schedule('showOnlyOneSemestr', sem_id);
}


function addSubject(id) {
	$('.'+id).each(function(){
		var content = $(this).html(), 
			day = $(this).attr('day'), 
			from = $(this).attr('from'), 
			minutes = $(this).attr('minutes'), 
			subjectID = $(this).attr('subjectID'), 
			semestrID = $(this).attr('semestrID'), 
			groupID = $(this).attr('groupID'),
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
		messageBoxId: 'schedule-message',
		showMenu: true
	});
	
	
	$('#btnAssignToAll').click(function(){
		$('#schedule-wrapper').schedule('tryAssignToPinned');
	});

	$('#filter-wrapper').filter({elemsToFilterSelector:".schedule-prototype-subject"});
});