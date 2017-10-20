// Load course info using AJAX

function init() {
    alert("AjaxCourseLoad::init");
    $(".course-link").click(function(event){
        event.preventDefault();
        loadCourseInfo($(this).attr('href'));
    });
}

function loadCourseInfo(courseUrl) {
    //alert("Loading course " + courseUrl);
    $.ajax({
        type: "GET",
        dataType: "html",
        url: courseUrl,
        success: function(resp){
            alert("Response for " + courseUrl + ": " + resp);
            //$mainDiv.empty();
            //$mainDiv.append($(resp));
        },
    });
}

$(document).ready(init);
