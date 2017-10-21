// Load course info using AJAX

function installClickHandlers() {
    const links = document.querySelectorAll(".course-link");
    links.forEach(function(linkElem) {
        linkElem.addEventListener("click", onCourseLinkClicked);
    });
}

function onCourseLinkClicked(event) {
    event.preventDefault();
    const courseUrl = event.target.getAttribute("href");
    loadCourseInfo(courseUrl);
}

function loadCourseInfo(courseUrl) {
    $.ajax({
        type: "GET",
        dataType: "html",
        url: courseUrl,
        success: function(resp){
            onCourseResponseReceived(resp);
        },
        error: function() {
            alert("Nie udało się pobrać strony tego przedmiotu.");
        }
    });
}

function onCourseResponseReceived(resp) {
    const courseInfo = JSON.parse(resp);
    const mainContainer = document.getElementById("main-content");
    mainContainer.innerHTML = "";

    const courseContainer = document.createElement("div");
    courseContainer.setAttribute("id", "enr-course-view");
    courseContainer.innerHTML = courseInfo.courseHtml;
    mainContainer.appendChild(courseContainer);
}

// document.addEventListener("DOMContentLoaded", installClickHandlers);
document.addEventListener("CoursesListChanged", installClickHandlers);
