function loadSubjectDetails(detailsUrl){
	$.ajax({
		type: "POST",
		dataType: "html",
		url: detailsUrl,
		success: function(resp){
			$('#subject-details').html(resp);
		}
	});
}

$(function(){
	$('.subject-link').click(function(){
		loadSubjectDetails($(this).attr('link'));
	})
});