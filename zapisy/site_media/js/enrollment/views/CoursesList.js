/*
 * Client-side implementation of the course list,
 * using the FilteredCoursesList base class.
*/

"use strict";

function CoursesList()
{
    FilteredCoursesList.call(this);
};

CoursesList.prototype = Object.create(FilteredCoursesList.prototype);

CoursesList.prototype.init = function()
{
    FilteredCoursesList.prototype.init.call(this);
    
    let self = this;
    // The semester selector
    $("#enr-courseFilter-semester").change(function()
    {
        self.onNewSemesterChosen();
    });
    
    this.initCourseLists();
};

CoursesList.prototype.initCourseLists = function()
{
    const jsonString = $("#courses_list_json").assertOne().val();
    let coursesListObject = JSON.parse(jsonString);
    
    this.courses = coursesListObject.courseList;
    this.currentSemester = coursesListObject.semesterInfo;
    
    this.setCoursesFromData();
};

CoursesList.prototype.setCoursesFromData = function()
{
    let self = this;
    this.courses.forEach(function(course)
    {
        self.addNewCourse(course);
    });
    
    $("#current_semester_year").text(this.currentSemester.year);
    $("#current_semester_type").text(this.currentSemester.type);
    
    this.initFilters();
};

CoursesList.prototype.onNewSemesterChosen = function()
{
    var newId = parseInt($("#enr-courseFilter-semester").find(":selected").val());
    this.userChosenSemester = newId;
    
    this.setDownloadingDataUi();
    
    let self = this;
    $.get(
        "/courses/get_semester_info/" + newId,
        function(d, s) { self.onSemesterInfoReceived(d, s); })
        .fail(function() { self.onSemesterInfoReceiveFailed(); });
};

CoursesList.prototype.onSemesterInfoReceiveFailed = function()
{
    this.setCoursesViewUi();
    
    $("#enr-courseFilter-semester").val(this.currentSemester.id);
    this.userChosenSemester = this.currentSemester.id;
    
    alert("Nie udało się pobrać listy przedmiotów dla tego semestru.");
};

CoursesList.prototype.onSemesterInfoReceived = function(data, status)
{
    this.courses = data.courseList;
    this.currentSemester = data.semesterInfo;
    
    $("#courses-list").empty();
    this.setCoursesFromData();
    this.setCoursesViewUi();
};

CoursesList.prototype.setDownloadingDataUi = function()
{
    $("#mainCoursesContainer").addClass("hidden");
    $("#fetchingListMessage").removeClass("hidden");
};

CoursesList.prototype.setCoursesViewUi = function()
{
    $("#mainCoursesContainer").removeClass("hidden");
    $("#fetchingListMessage").addClass("hidden");
};

CoursesList.prototype.addNewCourse = function(course)
{
    let courseLink = $("<a/>", {
             "href" : course.url,
             "text" : course.name
        });
    course["htmlNode"] = $("<li/>");
    courseLink.appendTo(course["htmlNode"]);
    course["htmlNode"].appendTo($("#courses-list"));
};


$(document).ready(function()
{
    new CoursesList();
});
