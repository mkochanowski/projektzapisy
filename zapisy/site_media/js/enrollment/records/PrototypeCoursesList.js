/*
 * Schedule prototype courses list.
*/

"use strict";

function PrototypeCoursesList()
{
    this.courseList = [];
    
    FilteredCoursesList.call(this);
};

PrototypeCoursesList.prototype = Object.create(FilteredCoursesList.prototype);

PrototypeCoursesList.prototype.init = function()
{
    FilteredCoursesList.prototype.init.call(this);
	
    var scheduleContainer = $('#enr-schedulePrototype-scheduleContainer').assertOne();
    this.schedule = new Schedule(scheduleContainer);
    
    if( user_is_student )
    {
        // TODO: this didn't work anyway (tried to use an undefined)
        // variable, and besides, what is the point of this feature?
	//    this.initRecordsLocking();
    }
    
    this.initCourses();
    this.initGroups();
    this.processGroupsAndTerms();
    
    this.uncheckAllButton = $("#enr-schedulePrototype-uncheckAll");
    this.uncheckAllButton.disableDragging();
    let self = this;
    this.uncheckAllButton.click(function()
	{
		self.courseList.forEach(function(course)
		{
			course.setPrototyped(false);
		});
	});
};

PrototypeCoursesList.prototype.initCourses = function()
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

PrototypeCoursesList.prototype.processCourse = function(courseRawObj)
{
    Fereol.Enrollment.Course.fromJSON(courseRawObj);
    
    let course = new PrototypeCourse();
    Object.keys(courseRawObj).forEach(function(key) {
        course[key] = courseRawObj[key];
    });

    let courseCheckbox = $("#checkbox-course-" + course.id);    
    let containingListItem = $("#listItem-course-" + course.id);
    
    courseRawObj.htmlNode = containingListItem;
    course._prototypedCheckbox = courseCheckbox;
        
    this.courseList.push(course);
};

PrototypeCoursesList.prototype.processGroupsAndTerms = function()
{
    let self = this;
    this.courseList.forEach(function(course)
    {
        let termsObjects = course.terms;
        course.terms = [];
        termsObjects.forEach(function(termObj)
        {
            let sterm = Fereol.Enrollment.ScheduleCourseTerm.fromObject(termObj);
            sterm.displayStyle =
                Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE;

            sterm.assignSchedule(self.schedule);
            course.terms.push(sterm);
        });
        (function()
		{
			course._prototypedCheckbox.click(function()
			{
				course.setPrototyped(course._prototypedCheckbox.attr('checked'));
			});
		})();
        course.setPrototyped(course._prototypedCheckbox.attr('checked'));
    });
};

/**
 * Inicjuje przycisk blokowania planu.
 */
PrototypeCoursesList.prototype.initRecordsLocking = function()
{
	var lockForm = $('#enr-schedulePrototype-setLocked').assertOne();
	var lockURL = lockForm.find('input[name=ajax-url]').assertOne().
		attr('value').trim();
	var isLocked = (lockForm.find('input[name=lock]').assertOne().
		attr('value') != 'true');
	var isLocking = false;

	var lockButton = $.create('a').insertAfter(lockForm);
	lockForm.remove();
	lockButton.attr('id', 'enr-schedulePrototype-setLocked');

	var updateLockButton = function()
	{
		var label = (isLocked ? 'Odblokuj' : 'Zablokuj') + ' plan';
		lockButton.text(label).attr('title', label).
			toggleClass('locked', isLocked).
			toggleClass('unlocked', !isLocked);
	};
	updateLockButton();

	lockButton.click(function()
	{
		if (isLocking)
			return;
		isLocking = true;
		lockButton.css('opacity', '0.5');

		isLocked = !isLocked;
		updateLockButton();
		if( user_is_student ){
		$.post(lockURL, {
			lock: isLocked
		}, function(data)
		{
			var result = AjaxMessage.fromJSON(data);
			self._isLoading = false;
			if (result.isSuccess())
			{
				isLocking = false;
				lockButton.css('opacity', '1');
			}
			else
				result.displayMessageBox();
			self._updateVisibility();
		}, 'json');
        }
	});

	lockButton.hover(function()
	{
		if (isLocking)
			return;
		lockButton.
			toggleClass('locked', !isLocked).
			toggleClass('unlocked', isLocked);
	}, function()
	{
		if (isLocking)
			return;
		lockButton.
			toggleClass('locked', isLocked).
			toggleClass('unlocked', !isLocked);
	})
};

PrototypeCoursesList.prototype.initGroups = function()
{
	var groupsRAW = $.parseJSON($('#courses_groups').val());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};


$(document).ready(function()
{
    new PrototypeCoursesList();
});


/*******************************************************************************
 * Klasa przedmiotu używanego w prototypie planu, tzn posiadającego kolekcję
 * terminów.
 ******************************************************************************/

function PrototypeCourse()
{
	this.model = null; // model danych

	this.wasEnrolled = null;
	this.english = null;
	this.exam = null;
	this.suggested_for_first_year = null;
	this.terms = [];
	this.isPrototyped = false;
	this._prototypedCheckbox = null;
};

PrototypeCourse.prototype.setPrototyped = function(prototyped)
{
	prototyped = !!prototyped;
	if (this.isPrototyped == prototyped)
		return;
	this.isPrototyped = prototyped;
	this._prototypedCheckbox.attr('checked', prototyped);

	this.terms.forEach(function(term)
	{
		term.setPrototyped(prototyped);
	});
};
