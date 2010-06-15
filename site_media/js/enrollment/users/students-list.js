$(document).ready(function(){ 
	$('.student-profile-link').click(function(){
	      loadStudentProfile($(this).attr('link'));
     })
});

function loadStudentProfile(profileUrl){
    var $profileDiv = $('#student-profile'),
    $loadingDiv = $('<div>&nbsp;</div>').addClass('profile-loading');
    $profileDiv.append($loadingDiv);
    
    $.ajax({
        type: "POST",
        dataType: "html",
        url: profileUrl,
        success: function(resp){
            $profileDiv.empty();
            $profileDiv.append($(resp));
            
        },
        complete: function(){
    
            $loadingDiv.remove();
        }
    });
}