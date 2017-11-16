// Load course info using AJAX

import * as $ from "jquery";
// import { scrollUpToElementIfWindowBelow } from "common/utils";

let isLoadingCourse: boolean = false;
type CourseInfo = {
	courseName: string,
	courseEditLink: string,
	courseHtml: string,
};

function installClickHandlers(): void {
	const links = document.querySelectorAll(".course-link");
	links.forEach(function(linkElem) {
		linkElem.addEventListener("click", onCourseLinkClicked);
	});
}

function onCourseLinkClicked(event: MouseEvent): void {
	event.preventDefault();
	if (isLoadingCourse) {
		return;
	}
	const clickedLink = event.target as HTMLHRElement;
	const courseUrl = clickedLink.getAttribute("href");
	loadCourseInfo(courseUrl);
}

function loadCourseInfo(courseUrl: string): void {
	isLoadingCourse = true;
	const container = document.getElementById("main-content");
	setElementLoadingUi(container);
	// scrollUpToElementIfWindowBelow("#main-menu-list");
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
		complete: function() {
			isLoadingCourse = false;
		}
	});
}

function setElementLoadingUi(elem: HTMLElement): void {
	const coveringLoadElem = document.createElement("div");
	coveringLoadElem.innerHTML = "&nbsp";
	coveringLoadElem.classList.add("content-loading");
	elem.appendChild(coveringLoadElem);
}

function removeElementLoadingUi(elem: HTMLElement): void {
	const elemChildren = Array.from(elem.children);
	elemChildren.forEach(function(child: Element) {
		const childClasses = Array.from(child.classList);
		if (childClasses.indexOf("content-loading") !== -1) {
			elem.removeChild(child);
		}
	});
}

function fillCourseHtml(courseHtml: string) {
	const mainContainer = document.getElementById("main-content");
	mainContainer.innerHTML = "";

	const courseContainer = document.createElement("div");
	courseContainer.setAttribute("id", "enr-course-view");
	courseContainer.innerHTML = courseHtml;
	mainContainer.appendChild(courseContainer);
}

function setPageTitleAndUrl(courseName: string, url: string) {
	document.title = `${courseName} - System Zapisów`;
	history.pushState({}, "", url);
}

function updateCourseNameAndEditLink(courseInfo: CourseInfo) {
	// The little arrow before the course name above the filters
	const arrowElem = document.getElementById("enr-course-arrow");
	arrowElem.classList.remove("hidden");

	const courseNameElem = document.getElementById("enr-course-name");
	courseNameElem.innerText = courseInfo.courseName;
	courseNameElem.classList.remove("hidden");

	const courseEditLink = document.getElementById("enr-course-edit-link");
	// It might not exist, only admins see that link
	if (courseEditLink) {
		courseEditLink.setAttribute("href", courseInfo.courseEditLink);
		courseEditLink.classList.remove("hidden");
	}
}

function onCourseResponseReceived(resp, courseUrl) {
	const courseInfo: CourseInfo = JSON.parse(resp);
	fillCourseHtml(courseInfo.courseHtml);
	setPageTitleAndUrl(courseInfo.courseName, courseUrl);
	updateCourseNameAndEditLink(courseInfo);
}

console.log("LOL");
document.addEventListener("CoursesListChanged", installClickHandlers);
