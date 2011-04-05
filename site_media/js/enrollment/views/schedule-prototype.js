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
	var pinnedGroupIDs = $.parseDjangoJSON(scheduleContainer.
		children('input[name=pinned]').assertOne().attr('value'));
	var enrolledGroupIDs = $.parseDjangoJSON(scheduleContainer.
		children('input[name=enrolled]').assertOne().attr('value'));

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

	$('#enr-schedulePrototype-subject-list').
		children('li').children('input[name=term]').
		each(function(idx, elem)
	{
		var sterm = Fereol.Enrollment.SubjectTerm.fromJSON(elem.value);
		sterm.isPinned = (pinnedGroupIDs.indexOf(sterm.groupID) >= 0);
		sterm.isEnrolled = (enrolledGroupIDs.indexOf(sterm.groupID) >= 0);
		sterm.isPrototyped = false;
		
		sterm.assignSchedule(SchedulePrototype.schedule);
	});

	//SchedulePrototype.initFilter();
};

$(SchedulePrototype.init);

/**
 * Inicjuje filtrowanie.
 */
SchedulePrototype.initFilter = function()
{
	var subjectFilterForm = $('#enr-schedulePrototype-top-bar').assertOne();

	subjectFilterForm.css('display', 'block');

	subjectFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		subjectFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	SchedulePrototype.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden przedmiot.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#enr-schedulePrototype-subject-list').assertOne());
	SchedulePrototype.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	SchedulePrototype.subjectFilter = new ListFilter('SchedulePrototype-subjects', subjectFilterForm.getDOM());

	SchedulePrototype.subjectFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (SchedulePrototype.emptyFilterWarningVisible == visible)
			return;
		SchedulePrototype.emptyFilterWarningVisible = visible;
		SchedulePrototype.emptyFilterWarning.css('display', visible?'':'none');
	};

	SchedulePrototype.subjectFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		return true;
		var subject = element.data;
		if (!subject.name)
			$.log(subject);
		return (subject.name.toLowerCase().indexOf(value) >= 0);
	}));

	SchedulePrototype.subjectFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		return true;
		if (!value)
			return true;
		var subject = element.data;
		return !subject.wasEnrolled;
	}));

	SchedulePrototype.subjectFilter.addFilter(ListFilter.CustomFilters.createSubjectTypeFilter(
		function(element, subjectType)
	{
		return true;
		var subject = element.data;
		return (subject.type == subjectType);
	}));
/*
	for (var subject in SchedulePrototype.subjects)
	{
		subject = SchedulePrototype.subjects[subject];
		SchedulePrototype.subjectFilter.addElement(new ListFilter.Element(subject, function(visible)
		{
			var subject = this.data;
			subject.setVisible(visible);
		}));
	};
*/
	SchedulePrototype.subjectFilter.runThread();
};
