function loadSubjectDetails(detailsUrl, obj){
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
                loadSubjectDetails($(this).attr('link'), $(this));
            });
			try {
				//sessionStorage.setItem('loaded-subject-detail-url', detailsUrl);
        if (obj == null || !obj.hasClass("forget")) {
          jaaulde.utils.cookies.set('loaded-subject-detail-url', detailsUrl);
        }
			} catch(ex) {}
			$('.subject-details-table tbody tr:even').addClass('even');
        },
        complete: function(){
            //$detailsDiv.removeClass('subject-details-loading');
            $loadingDiv.remove();
        }
    });
}
