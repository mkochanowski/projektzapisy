/*
 * Offer/proposal courses list.
*/

"use strict";

function OfferCoursesList()
{
    this.courseList = [];
    
    FilteredCoursesList.call(this);
};

OfferCoursesList.prototype = Object.create(FilteredCoursesList.prototype);

OfferCoursesList.prototype.init = function()
{
    FilteredCoursesList.prototype.init.call(this);
    this.initCourses();
};

OfferCoursesList.prototype.initCourses = function()
{
    const jsonString = $("#courses_list_json").assertOne().val();
    let coursesObj = JSON.parse(jsonString);
    this.courses = coursesObj;
    
    let self = this;
    this.courses.forEach(function(course)
    {
        self.processCourse(course);
    });
    
    this.initFilters(); 
};

OfferCoursesList.prototype.processCourse = function(courseProposal)
{
    // Assign the HTML node that corresponds to this course
    // Needed so that we can show-hide it depending on the state
    // of the filters.
    courseProposal["htmlNode"] = $("#listItem-proposal-" + courseProposal.id);
};

OfferCoursesList.prototype.addCustomFilters = function()
{
    // Two custom filters - they allow users to filter by teacher
    // and filter by vote status.
    this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
        'teacher', '#enr-teacher', function(element, value)
    {
        if (!value || value == -1)
          			return true;
        var course = element.data;
        return (course.teacher == value);
    }));
    
    this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
   		'vote', '#enr-proposalFilter-vote', function(element, value)
   	{
        var course = element.data;
        if (!value)
        {
            // We want to hide the courses students can vote for
            return course.status == 2;
        }
   		return true;
   	}));
};

$(document).ready(function()
{
    new OfferCoursesList();
});
