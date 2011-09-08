/**
 * Kod odpowiedzialny za plan zajęć.
 */

ScheduleView = new Object();

/**
 * Inicjuje widok planu.
 */

ScheduleView.init = function()
{
	ScheduleView.initGroups();

	var scheduleContainer = $('#enr-schedule-scheduleContainer').assertOne();

	ScheduleView.schedule = new Schedule(scheduleContainer, {
		dayColumnWidth: 170
	});

	ScheduleView.initCourseList();
};
$(ScheduleView.init);

ScheduleView.courseList = [];

ScheduleView.initGroups = function()
{
	var coursesRAW = $.parseJSON($(
		'#enr-schedule-scheduleContainer input[name=courses]').val());
	coursesRAW.forEach(function(courseRAW)
	{
		Fereol.Enrollment.Course.fromJSON(courseRAW);
	});

	var groupsRAW = $.parseJSON(
		$('#enr-schedule-scheduleContainer input[name=groups]').val());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};

ScheduleView.initCourseList = function()
{
	var courseList = $('#enr-schedule-listByCourse');

	courseList.find('tr.courseDetails > td').each(function(idx, elem)
	{
		elem = $(elem);

		var course = new ScheduleView.Course();
		ScheduleView.courseList.push(course);

		course.id = elem.children('input[name=id]').attr('value').castToInt();
		course.name = elem.children('input[name=name]').attr('value').trim();
		course.shortName = elem.children('input[name=short]').attr('value').trim();
		course.url = elem.children('input[name=url]').attr('value').trim();
		course.type = elem.children('input[name=type]').attr('value').castToInt();
		course._listElementContainer = elem;

		elem.find('input[name=term]').each(function(idx, elem)
		{
			elem = $(elem);

			var sterm = Fereol.Enrollment.ScheduleCourseTerm.fromJSON(elem.attr('value'));
			sterm.displayStyle =
				Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE;
			sterm.isEnrolled = true;
			sterm.course = course;

			sterm.assignSchedule(ScheduleView.schedule);

			course.terms.push(sterm);
		});
	});
};

/*******************************************************************************
 * Klasa przedmiotu używanego w planie, tzn posiadającego kolekcję terminów.
 ******************************************************************************/

ScheduleView.Course = function()
{
	this.id = null;
	this.name = null;
	this.shortName = null;
	this.url = null;
	this.type = null;
	this.terms = [];
	this._listElementContainer = null;
	this._prototypedCheckbox = null;
};

ScheduleView.Course.prototype.toString = function()
{
	if (this.shortName)
		return this.shortName;
	else if (this.name)
		return this.name;
	else
		return 'ScheduleView.Course';
};
