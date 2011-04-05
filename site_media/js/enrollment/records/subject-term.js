/**
 * Model terminu przedmiotu, tzn zakresu godzinowego dla określonej grupy
 * z określonego przedmiotu, do wyświetlenia w terminarzu.
 *
 * TODO: przetestować dla niespójnych id grup i terminów (w danych przykładowych
 * wszystkie id terminów pokrywają się z id grup).
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.SubjectTerm = function()
{
	this.id = null;
	this.groupID = null;
	this.scheduleTerm = null; // Schedule.Term
	this.container = $.create('div');
	this._containerReady = false;

	this.isPinned = false; // czy jest "przypięty"
	this.isEnrolled = false; // czy student jest zapisany
	this.isPrototyped = false; // czy jest tymczasowo wyświetlony w prototypie

	this._isVisible = false;

	this.schedule = null;
	this.subject = null; // SchedulePrototype.PrototypeSubject

	this.classroom = null;
	this.teacher = null;
};

Fereol.Enrollment.SubjectTerm.groupTypes =
{
	1: ['wykład', 'wyk'],
	2: ['ćwiczenia', 'ćw'],
	3: ['pracownia', 'prac'],
	4: ['ćwiczenia (zaaw)', 'ćw-z'],
	5: ['ćwiczenia + prac.', 'ćw+prac'],
	6: ['seminarium', 'sem'],
	7: ['lektorat', 'lek'],
	8: ['wf', 'wf']
};

Fereol.Enrollment.SubjectTerm.fromJSON = function(json)
{
	var sterm = new Fereol.Enrollment.SubjectTerm();
	var raw = $.parseDjangoJSON(json)

	sterm.id = raw.id.castToInt();
	sterm.groupID = raw.group.castToInt();
	sterm.scheduleTerm = new Schedule.Term(
		raw.day.castToInt() - 1,
		new Schedule.Time(raw.start_time[0].castToInt(), raw.start_time[1].castToInt()),
		new Schedule.Time(raw.end_time[0].castToInt(), raw.end_time[1].castToInt()),
		sterm.container
	);
	sterm.scheduleTerm.onResize = function(isFullSize)
	{
		sterm._onResize(isFullSize);
	};

	sterm.classroom = raw.classroom.castToInt();
	sterm.teacher = raw.teacher;
	sterm.type = raw.group_type.castToInt();

	return sterm;
};

Fereol.Enrollment.SubjectTerm.prototype.assignSchedule = function(schedule)
{
	this.schedule = schedule;
	this._updateVisibility();
};

Fereol.Enrollment.SubjectTerm.prototype._updateVisibility = function()
{
	var shouldBeVisible = (this.isPinned || this.isEnrolled || this.isPrototyped);
	if (shouldBeVisible == this._isVisible)
		return;
	this._isVisible = shouldBeVisible;
	if (shouldBeVisible)
	{
		if (!this._containerReady)
		{
			this._containerReady = true;

			$.create('span', {className: 'name'}).text(this.subject.shortName).
				attr('title', this.subject.name).appendTo(this.container);
			this._teacherLabel = $.create('span', {className: 'teacher'}).text(this.teacher).
				appendTo(this.container);
			this._typeLabel = $.create('span', {className: 'type'}).
				appendTo(this.container);
			this._classroomLabel = $.create('span', {className: 'classroom'}).
				appendTo(this.container);
			if (this.classroom)
				this._classroomLabel.text('s. ' + this.classroom);
		}
		SchedulePrototype.schedule.addTerm(this.scheduleTerm);
		if (this.isEnrolled)
			this.container.addClass('enrolled');
		else
			this.container.removeClass('enrolled');
	}
	else
		SchedulePrototype.schedule.removeTerm(this.scheduleTerm);
};

Fereol.Enrollment.SubjectTerm.prototype._onResize = function(isFullSize)
{
	var CLASSROOM_PADDING = 2;

	this._classroomLabel.css({
		left: (this._classroomLabel.parent().innerWidth() -
			CLASSROOM_PADDING * 2 -
			this._classroomLabel.width()) + 'px',
		top: (this._classroomLabel.parent().innerHeight() -
			this._classroomLabel.height() -
			CLASSROOM_PADDING) + 'px'
	});

	this._typeLabel.text(Fereol.Enrollment.SubjectTerm.
		groupTypes[this.type][isFullSize?0:1]).css({
		top: (this._typeLabel.parent().innerHeight() -
			this._typeLabel.height() -
			CLASSROOM_PADDING) + 'px'
	});

	this._teacherLabel.css({
		display: isFullSize ? 'block' : 'none'
	});
};

Fereol.Enrollment.SubjectTerm.prototype.setPrototyped = function(prototyped)
{
	this.isPrototyped = prototyped;
	this._updateVisibility();
};

Fereol.Enrollment.SubjectTerm.prototype.toString = function()
{
	return this.scheduleTerm.toString();
};
