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
    const container = document.getElementById("main-content");
    setElementLoadingUi(container);
    scrollUpToElementIfWindowBelow("#main-menu-list");
    $.ajax({
        type: "GET",
        dataType: "html",
        url: courseUrl,
        success: function(resp) {
            onCourseResponseReceived(resp, courseUrl);
        },
        error: function() {
            removeElementLoadingUi(container);
            alert("Nie udało się pobrać strony tego przedmiotu.");
        },
    });
}

function setElementLoadingUi(elem) {
    const coveringLoadElem = document.createElement("div");
    coveringLoadElem.innerHTML = "&nbsp";
    coveringLoadElem.classList.add("content-loading");
    elem.appendChild(coveringLoadElem);
}

function removeElementLoadingUi(elem) {
    const elemChildren = Array.from(elem.children);
    elemChildren.forEach(function(child) {
        const childClasses = Array.from(child.classList);
        if (childClasses.indexOf("content-loading") !== -1) {
            elem.removeChild(child);
        }
    });
}

function fillCourseHtml(courseHtml) {
    const mainContainer = document.getElementById("main-content");
    mainContainer.innerHTML = "";

    const courseContainer = document.createElement("div");
    courseContainer.setAttribute("id", "enr-course-view");
    courseContainer.innerHTML = courseHtml;
    mainContainer.appendChild(courseContainer);
}

function setPageTitleAndUrl(courseName, url) {
    document.title = `${courseName} - System Zapisów`;
    history.pushState({}, "", url);
}

function onCourseResponseReceived(resp, courseUrl) {
    const courseInfo = JSON.parse(resp);
    fillCourseHtml(courseInfo.courseHtml);
    setPageTitleAndUrl(courseInfo.courseName, courseUrl);
}

document.addEventListener("CoursesListChanged", installClickHandlers);
