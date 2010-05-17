function loadSubjectDetails(detailsUrl){
    var $detailsDiv = $('#subject-details'),
    $loadingDiv = $('<div>&nbsp;</div>').addClass('subject-details-loading');
    $detailsDiv.append($loadingDiv);
    //$detailsDiv.addClass('subject-details-loading');
    $.ajax({
        type: "POST",
        dataType: "html",
        url: detailsUrl,
        success: function(resp){
            $detailsDiv.empty();
            $detailsDiv.append($(resp));
            $('.subject-details-link').click(function(){
                loadSubjectDetails($(this).attr('link'));
            });
        },
        complete: function(){
            //$detailsDiv.removeClass('subject-details-loading');
            $loadingDiv.remove();
        }
    });
}
$(function(){
	$('.subject-link').click(function(){
		loadSubjectDetails($(this).attr('link'));
	});
});
