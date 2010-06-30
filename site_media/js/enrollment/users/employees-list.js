$(document).ready(function(){ 
	$('.employee-profile-link').click(function(){
	      loadEmployeeProfile($(this).attr('link'));
     })
});

function loadEmployeeProfile(profileUrl){
    var $profileDiv = $('#employee-profile'),
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