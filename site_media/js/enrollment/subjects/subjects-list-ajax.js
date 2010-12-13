$(document).ready(function(){  // add listeners to events and invoke ajax function after first loading 
	var ajaxUrl = $('#ajaxUrl').val();

    $.each([$('input:checkbox[class:type-list]')], function(index, element) { 
       element.click(function() { getSearchedSubjects(ajaxUrl, ajaxSuccessCallBack); })
    });

    $('#semester').change(function(){
       getSearchedSubjects(ajaxUrl, ajaxSuccessCallBack);
    })

    $('#keyword').keydown(function(){
       getSearchedSubjects(ajaxUrl, ajaxSuccessCallBack);
    })

    getSearchedSubjects(ajaxUrl, ajaxSuccessCallBack);  
});

function getSearchedSubjects(url_, successCallback) {

	var SubjTypes = "";
	
	$('input:checkbox[class:type-list]:checked').each(function() { SubjTypes += "&type=" + this.value; }); 
	var sem_id = $('#semester').val() || 0;
	
	$.ajax({
	      url: url_,
	      type: "POST",
		  dataType: "json",
	      data: "semester=" + sem_id + "&keyword=" + $('input:text[name:keyword]').val() + SubjTypes,
	      success: successCallback,
		  error: function (XMLHttpRequest, textStatus, errorThrown) {
	        alert("XMLHttpRequest="+XMLHttpRequest.responseText+"\ntextStatus="+textStatus+"\nerrorThrown="+errorThrown);
	    }
	
	   });
 
}