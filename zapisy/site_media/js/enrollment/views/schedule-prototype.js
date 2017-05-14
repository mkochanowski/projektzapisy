/**
 * Kod odpowiedzialny za prototyp planu.
 */

SchedulePrototype = new Object();

/**
 * Inicjuje widok prototypu planu.
 */
SchedulePrototype.init = function()
{
	var scheduleContainer = $('#enr-schedulePrototype-scheduleContainer').assertOne();


	SchedulePrototype.initGroups();

	SchedulePrototype.schedule = new Schedule(scheduleContainer);

	/* //testowe
	SchedulePrototype.schedule.addTerm(new Schedule.Term(0,
		new Schedule.Time(13, 20), new Schedule.Time(16, 20), $.create('div').text('a')));
	SchedulePrototype.schedule.addTerm(new Schedule.Term(0,
		new Schedule.Time(16, 10), new Schedule.Time(17, 10), $.create('div').text('b')));
	SchedulePrototype.schedule.addTerm(new Schedule.Term(0,
		new Schedule.Time(12, 30), new Schedule.Time(13, 50), $.create('div').text('c')));
	SchedulePrototype.schedule.addTerm(new Schedule.Term(0,
		new Schedule.Time(15, 00), new Schedule.Time(19, 10), $.create('div').text('d')));
	SchedulePrototype.schedule.addTerm(new Schedule.Term(0,
		new Schedule.Time(18, 20), new Schedule.Time(19, 10), $.create('div').text('e')));
	*/

	SchedulePrototype.initCourseList();
	SchedulePrototype.initFilter();
    if( user_is_student ){
	    SchedulePrototype.initRecordsLocking();
    }

	$.dataInvalidate(); // zawsze chcemy świeżych danych
};

SchedulePrototype.urls = {};

$(SchedulePrototype.init);

/**
 * Inicjuje filtrowanie.
 */
SchedulePrototype.initFilter = function()
{
	var courseFilterForm = $('#enr-schedulePrototype-top-bar').assertOne();

	courseFilterForm.css('display', 'block');

	courseFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		courseFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	SchedulePrototype.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden przedmiot.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#enr-schedulePrototype-course-list').assertOne());
	SchedulePrototype.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	SchedulePrototype.courseFilter = new ListFilter('SchedulePrototype-courses', courseFilterForm.getDOM());

	SchedulePrototype.courseFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (SchedulePrototype.emptyFilterWarningVisible == visible)
			return;
		SchedulePrototype.emptyFilterWarningVisible = visible;
		SchedulePrototype.emptyFilterWarning.css('display', visible?'':'none');
		SchedulePrototype.uncheckAllButton.css('display', visible?'none':'');
	};

	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var course = element.data;
		return (course.model.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		if (!value)
			return true;
		var course = element.data;
		return !course.wasEnrolled;
	}));
	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showEnglish', '#enr-courseFilter-english', function(element, value)
	{
		if(value)
			return true;
		var course = element.data;
		return !course.english;
	}));
	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showExam', '#enr-courseFilter-exam', function(element, value)
	{
		if(value)
			return true;
		var course = element.data;
		return !course.exam;
	}));
	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showSyggestedForFirstYear', '#enr-courseFilter-suggestedForFirstYear', function(element, value)
	{
		if(!value)
			return true;
		var course = element.data;
		return course.suggested_for_first_year;
	}));

	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		var course = element.data;
		return (course.model.type == courseType);
	}));

	SchedulePrototype.courseList.forEach(function(course)
	{
		SchedulePrototype.courseFilter.addElement(new ListFilter.Element(course, function(visible)
		{
			var course = this.data;
			course.setVisible(visible);
		}));
	});

	SchedulePrototype.courseFilter.runThread(true);
	$('#enr-schedulePrototype-top-bar').find('label').disableDragging();
};

/**
 * Inicjuje przycisk blokowania planu.
 */
SchedulePrototype.initRecordsLocking = function()
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

SchedulePrototype.initGroups = function()
{
	var coursesRAW = $.parseJSON($(
		'#enr-schedulePrototype-scheduleContainer input[name=courses]').val());
	coursesRAW.forEach(function(courseRAW)
	{
		Fereol.Enrollment.Course.fromJSON(courseRAW);
	});

	var groupsRAW = $.parseJSON(
		$('#enr-schedulePrototype-scheduleContainer input[name=groups]').val());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};

SchedulePrototype.courseList = [];

SchedulePrototype.initCourseList = function()
{
	var courseList = $('#enr-schedulePrototype-course-list');

	courseList.children('li').each(function(idx, elem)
	{
		elem = $(elem);

		var course = new SchedulePrototype.PrototypeCourse();
		SchedulePrototype.courseList.push(course);

		course.model = Fereol.Enrollment.Course.getByID(
			elem.children('input[name=id]').attr('value').castToInt());

		course.wasEnrolled = elem.children('input[name=wasEnrolled]').attr('value').castToBool();
		course.english = elem.children('input[name=english]').attr('value').castToBool();
		course.exam = elem.children('input[name=exam]').attr('value').castToBool();
		course.suggested_for_first_year = elem.children('input[name=suggested_for_first_year]').attr('value').castToBool();
		course._listElementContainer = elem;
		course._prototypedCheckbox = elem.find('input[type=checkbox]').assertOne();

		elem.children('input[name=term]').each(function(idx, elem)
		{
			elem = $(elem);

			var sterm = Fereol.Enrollment.ScheduleCourseTerm.fromJSON(
				elem.attr('value'));
			sterm.displayStyle =
				Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE;

			sterm.assignSchedule(SchedulePrototype.schedule);

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

	SchedulePrototype.uncheckAllButton = $.create('a').attr('id',
		'enr-schedulePrototype-uncheckAll').insertBefore($(courseList).parent().find('hr')).
		text('odznacz wszystkie').disableDragging().click(function()
	{
		SchedulePrototype.courseList.forEach(function(course)
		{
			course.setPrototyped(false);
		});
	});
};

/*******************************************************************************
 * Klasa przedmiotu używanego w prototypie planu, tzn posiadającego kolekcję
 * terminów.
 ******************************************************************************/

SchedulePrototype.PrototypeCourse = function()
{
	this.model = null; // model danych

	this.wasEnrolled = null;
	this.english = null;
	this.exam = null;
	this.suggested_for_first_year = null;
	this.terms = [];
	this.isPrototyped = false;
	this._listElementContainer = null;
	this._prototypedCheckbox = null;
};

SchedulePrototype.PrototypeCourse.prototype.setPrototyped = function(prototyped)
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

SchedulePrototype.PrototypeCourse.prototype.setVisible = function(visible)
{
	this._listElementContainer.css('display', (visible ? '' : 'none'));
	if (!visible)
		this.setPrototyped(false);
};

SchedulePrototype.PrototypeCourse.prototype.toString = function()
{
	return 'PrototypeCourse@' + this.model.toString();
};
