function ajaxSuccessCallBack(data) {
		    
   $("#subject-list").text("");  
   $("#subject-list").append("<h2>Semestr: " + data.semester_name + "</h2>");    
   
   var str = "";
   var size = 0;
   
   $.each(data.subjects, function(i,item){
       str += "<li><a class=\"subject-link\" id=\"subject-9"+ item.id +"\" link=\"/subjects/"+ item.slug +"\">" + item.entity__name + "</a></li>";
	   size += 1;
   });
   
   $("#subject-list").append("<ul>" + str + "</ul>");
   
   	$('.subject-link').click(function(){
      loadSubjectDetails($(this).attr('link'), $(this));
   })
   
    $("#subject-list").append("<i>Przedmiotow: " + size);

}

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
$(function(){
	try {
		//var url = sessionStorage.getItem('loaded-subject-detail-url');
		var url = jaaulde.utils.cookies.get('loaded-subject-detail-url');
		if (url != null) {
			loadSubjectDetails(url, null);
		}
	} catch(ex) {}
});
