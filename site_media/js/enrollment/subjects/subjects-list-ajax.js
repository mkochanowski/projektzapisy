$(document).ready(function(){  // add listeners to events and invoke ajax function after first loading 

    $.each([$('#semester'), $('.type-list')], function(index, element) { 
       element.click(function() { getSearchedSubjects(ajaxUrl); })
    });

    $('#keyword').keydown(function(){
       getSearchedSubjects(ajaxUrl);
    })

    getSearchedSubjects(ajaxUrl);  
});

function getSearchedSubjects(url_) {

var SubjTypes = "";

$('input:checkbox[class:type-list]:checked').each(function() { SubjTypes += "&type=" + this.value; }); 
var sem_id = $('#semester').val() || 0;

$.ajax({
      url: url_,
      type: "POST",
	  dataType: "json",
      data: "semester=" + sem_id + "&keyword=" + $('input:text[name:keyword]').val() + SubjTypes,
      success: function(data) {
	    
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
		      loadSubjectDetails($(this).attr('link'));
	       })
		   
		    $("#subject-list").append("<i>Przedmiotow: " + size);
  
	  },
	  error: function (XMLHttpRequest, textStatus, errorThrown) {
        alert("XMLHttpRequest="+XMLHttpRequest.responseText+"\ntextStatus="+textStatus+"\nerrorThrown="+errorThrown);
    }

   });
 
}