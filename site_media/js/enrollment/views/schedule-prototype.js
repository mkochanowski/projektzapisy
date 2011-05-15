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
	var pinnedGroupIDs = $.parseJSON(scheduleContainer.
		children('input[name=pinned]').assertOne().attr('value'));
	var enrolledGroupIDs = $.parseJSON(scheduleContainer.
		children('input[name=enrolled]').assertOne().attr('value'));
	var queuedGroupIDs = $.parseJSON(scheduleContainer.
		children('input[name=queued]').assertOne().attr('value'));

	SchedulePrototype.urls['set-pinned'] = scheduleContainer.
		children('input[name=setPinnedUrl]').assertOne().attr('value').trim();
	SchedulePrototype.urls['set-enrolled'] = scheduleContainer.
		children('input[name=setEnrolledUrl]').assertOne().attr('value').trim();

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

	
	SchedulePrototype.initCourseList(enrolledGroupIDs, pinnedGroupIDs, queuedGroupIDs);
	SchedulePrototype.initFilter();
	SchedulePrototype.initRecordsLocking();
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
		return (course.name.toLowerCase().indexOf(value) >= 0);
	}));

	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		if (!value)
			return true;
		var course = element.data;
		return !course.wasEnrolled;
	}));

	SchedulePrototype.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		var course = element.data;
		return (course.type == courseType);
	}));

	SchedulePrototype.courseList.forEach(function(course)
	{
		SchedulePrototype.courseFilter.addElement(new ListFilter.Element(course, function(visible)
		{
			var course = this.data;
			course.setVisible(visible);
		}));
	});

	SchedulePrototype.courseFilter.runThread();
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
		
		$.post(lockURL, {
			csrfmiddlewaretoken: $.cookie('csrftoken'), // TODO: nowe jquery tego podobno nie wymaga
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

SchedulePrototype.courseList = [];

SchedulePrototype.initCourseList = function(enrolled, pinned, queued)
{
	var courseList = $('#enr-schedulePrototype-course-list');

	courseList.children('li').each(function(idx, elem)
	{
		elem = $(elem);

		var course = new SchedulePrototype.PrototypeCourse();
		SchedulePrototype.courseList.push(course);

		course.id = elem.children('input[name=id]').attr('value').castToInt();
		course.name = elem.children('label').disableDragging().text().trim();
		course.shortName = elem.children('input[name=short]').attr('value').trim();
		course.type = elem.children('input[name=type]').attr('value').castToInt();
		course.wasEnrolled = elem.children('input[name=wasEnrolled]').attr('value').castToBool();
		course.isRecordingOpen = elem.children('input[name=isRecordingOpen]').attr('value').castToBool();
		course._listElementContainer = elem;
		course._prototypedCheckbox = elem.find('input[type=checkbox]').assertOne();

		elem.children('input[name=term]').each(function(idx, elem)
		{
			elem = $(elem);

			var sterm = Fereol.Enrollment.CourseTerm.fromJSON(elem.attr('value'));
			sterm.isPinned = (pinned.indexOf(sterm.groupID) >= 0);
			sterm.isEnrolled = (enrolled.indexOf(sterm.groupID) >= 0);
			sterm.isQueued = (queued.indexOf(sterm.groupID) >= 0);
			sterm.isPrototyped = false;
			sterm.course = course;

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
		'enr-schedulePrototype-uncheckAll').insertAfter(courseList).
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
	this.id = null;
	this.name = null;
	this.shortName = null;
	this.type = null;
	this.wasEnrolled = null;
	this.isRecordingOpen = null;
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
	if (this.shortName)
		return this.shortName;
	else if (this.name)
		return this.name;
	else
		return 'SchedulePrototype.PrototypeCourse';
};
