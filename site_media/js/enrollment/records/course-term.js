/**
 * Model terminu przedmiotu, tzn zakresu godzinowego dla określonej grupy
 * z określonego przedmiotu, do wyświetlenia w terminarzu.
 *
 * TODO: przetestować dla niespójnych id grup i terminów (w danych przykładowych
 * wszystkie id terminów pokrywają się z id grup).
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.CourseTerm = function()
{
	this.id = null;
	this.groupID = null;
	this.scheduleTerm = null; // Schedule.Term
	this.container = $.create('div');

	this._containerReady = false;
	this._controlsReady = false;

	this.isPinned = false; // czy jest "przypięty"
	this.isEnrolled = false; // czy student jest zapisany
	this.isPrototyped = false; // czy jest tymczasowo wyświetlony w prototypie
	this.isQueued = false; // czy jest "w kolejce"

	this._isLoading = false; // czy w tej chwili trwa komunikacja z serwerem
	this._isVisible = false;

	this.schedule = null;
	this.course = null; // SchedulePrototype.PrototypeCourse

	this.classroom = null;
	this.teacher = null;
	this.type = null;
};

Fereol.Enrollment.CourseTerm.groupTypes =
{
	1: ['wykład', 'wyk'],
	2: ['ćwiczenia', 'ćw'],
	3: ['pracownia', 'prac'],
	4: ['ćwiczenia (zaaw)', 'ćw-z'],
	5: ['ćwiczenia + prac.', 'ćw+prac'],
	6: ['seminarium', 'sem'],
	7: ['lektorat', 'lek'],
	8: ['wf', 'wf'],
    9: ['repetytorium', 'rep'],
   10: ['projekt', 'proj']
};

Fereol.Enrollment.CourseTerm.byGroups = {};

Fereol.Enrollment.CourseTerm.prototype.isEnrolledOrQueued = function()
{
	return this.isEnrolled || this.isQueued;
}

Fereol.Enrollment.CourseTerm.fromJSON = function(json)
{
	var sterm = new Fereol.Enrollment.CourseTerm();
	var raw = $.parseJSON(json)

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

	if (!Fereol.Enrollment.CourseTerm.byGroups[sterm.groupID])
		Fereol.Enrollment.CourseTerm.byGroups[sterm.groupID] = [];
	Fereol.Enrollment.CourseTerm.byGroups[sterm.groupID].push(sterm);

	return sterm;
};

Fereol.Enrollment.CourseTerm.prototype.assignSchedule = function(schedule)
{
	this.schedule = schedule;
	this._updateVisibility();
};

Fereol.Enrollment.CourseTerm.prototype._updateVisibility = function()
{
	var self = this;

	if (!this._containerReady)
	{
		this._containerReady = true;

		$.create('span', {className: 'name'}).text(this.course.shortName).
			attr('title', this.course.name).appendTo(this.container);
		this._teacherLabel = $.create('span', {className: 'teacher'}).text(this.teacher).
			appendTo(this.container);
		this._typeLabel = $.create('span', {className: 'type'}).
			appendTo(this.container).attr('title',
			Fereol.Enrollment.CourseTerm.groupTypes[this.type][0]);

		this._classroomLabel = $.create('span', {className: 'classroom'}).
			appendTo(this.container);
		if (this.classroom)
			this._classroomLabel.text('s. ' + this.classroom);

		this._controlsBox = $.create('div', {className: 'controls'}).
			appendTo(this.container).css('display', 'none');

		this._pinUnpinButton = $.create('span', { className: 'pinUnpin'}).
			appendTo(this._controlsBox);
		this._signInOutButton = $.create('span', { className: 'signInOut'}).
			appendTo(this._controlsBox);
		this._loadingIndicator = $.create('div', { className: 'loadingIndicator'}).
			appendTo(this._controlsBox).css('display', 'none');

		this.container.mouseenter(function()
		{
			if (!self._controlsEmpty)
				self._controlsBox.css('display', 'block');
		}).mouseleave(function()
		{
			self._controlsBox.css('display', 'none');
		});
	}
	this._updateControls();

	if (this.isEnrolled)
		this.container.addClass('enrolled');
	else
		this.container.removeClass('enrolled');
	if (this.isQueued)
		this.container.addClass('queued');
	else
		this.container.removeClass('queued');

	var shouldBeVisible = (this.isPinned || this.isEnrolled ||
		this.isPrototyped || this.isQueued);
	if (shouldBeVisible == this._isVisible)
		return;
	this._isVisible = shouldBeVisible;
	if (shouldBeVisible)
		SchedulePrototype.schedule.addTerm(this.scheduleTerm);
	else
	{
		SchedulePrototype.schedule.removeTerm(this.scheduleTerm);
		this._controlsBox.css('display', 'none');
	}
};

Fereol.Enrollment.CourseTerm.prototype._updateControls = function()
{
	var self = this;
	
	if (!this._controlsReady)
	{
		this._controlsReady = true;

		this._signInOutButton.click(function()
		{
			MessageBox.clear();
			self.setEnrolled(!self.isEnrolledOrQueued());
		});

		this._pinUnpinButton.click(function()
		{
			MessageBox.clear();
			self.setPinned(!self.isPinned);
		});
	}
	this._controlsEmpty = false;

	if (this._isLoading)
	{
		self._loadingIndicator.css('display', 'block');
		self._controlsBox.children('span').css('display', 'none');
		return;
	}
	self._loadingIndicator.css('display', 'none');

	this._pinUnpinButton.css({
		backgroundPosition: this.isPinned ? '-12px -12px' : '0 -12px',
		display: this.isEnrolledOrQueued() ? 'none' : ''
	}).attr('title', this.isPinned ? 'odepnij od planu' : 'przypnij do planu');
	this._signInOutButton.css({
		backgroundPosition: this.isEnrolledOrQueued() ? '-12px 0' : '0 0',
		display: this.course.isRecordingOpen ? '' : 'none'
	}).attr('title', this.isEnrolledOrQueued() ? 'wypisz się' +
		(this.isQueued ? ' z kolejki' : '') : 'zapisz się');
	this._controlsEmpty = this.isEnrolledOrQueued() &&
		!this.course.isRecordingOpen;
};

Fereol.Enrollment.CourseTerm.prototype._onResize = function(isFullSize)
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

	this._typeLabel.text(Fereol.Enrollment.CourseTerm.
		groupTypes[this.type][isFullSize?0:1]).css({
		top: (this._typeLabel.parent().innerHeight() -
			this._typeLabel.height() -
			CLASSROOM_PADDING) + 'px'
	});

	this._teacherLabel.css({
		display: isFullSize ? 'block' : 'none'
	});
};

Fereol.Enrollment.CourseTerm.prototype.setPrototyped = function(prototyped)
{
	this.isPrototyped = prototyped;
	this._updateVisibility();
};

Fereol.Enrollment.CourseTerm.prototype.setPinned = function(pinned)
{
	if (this._isLoading)
		return;
	this._isLoading = true;

	var self = this;
	this._updateControls();

	pinned = !!pinned;
	if (this.isPinned == pinned)
		return;

	$.post(SchedulePrototype.urls['set-pinned'], {
		csrfmiddlewaretoken: $.cookie('csrftoken'), // TODO: nowe jquery tego podobno nie wymaga
		group: this.groupID,
		pin: pinned
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		self._isLoading = false;
		if (result.isSuccess())
			self.isPinned = pinned;
		else
			result.displayMessageBox();
		self._updateVisibility();
	}, 'json');
};

Fereol.Enrollment.CourseTerm.prototype.setEnrolled = function(enrolled)
{
	if (this._isLoading)
		return;
	this._isLoading = true;

	var self = this;
	this._updateControls();

	if (!this.course.isRecordingOpen)
		throw new Error('Zapisy na ten przedmiot są zamknięte');

	enrolled = !!enrolled;
	if (this.isEnrolledOrQueued() == enrolled)
		return;

	$.post(SchedulePrototype.urls['set-enrolled'], {
		csrfmiddlewaretoken: $.cookie('csrftoken'), // TODO: nowe jquery tego podobno nie wymaga
		group: this.groupID,
		enroll: enrolled
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		self._isLoading = false;
		if (result.isSuccess())
		{
			self.isEnrolled = enrolled;
			self.isPinned = false;
			self.isQueued = false;
			if (enrolled)
			{
				// zaznaczanie innych grup tego samego typu jako "nie zapisane"
				self.course.terms.forEach(function(e)
				{
					if (e.groupID == self.groupID || e.type != self.type)
						return;
					e.isEnrolled = false;
					e._updateVisibility();
				});

				// zaznaczanie powiązanych jako "zapisane"
				result.data.forEach(function(e)
				{
					if (e == self.groupID)
						return;
					Fereol.Enrollment.CourseTerm.byGroups[e].forEach(function(alsoEnrolledTo)
					{
						alsoEnrolledTo.isEnrolled = true;
						alsoEnrolledTo.isPinned = false;
						alsoEnrolledTo._updateVisibility();
					});
				})
			}
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			self.isQueued = true;
			self.isPinned = false;
			result.displayMessageBox();
		}
		else
			result.displayMessageBox();
		self._updateVisibility();
	}, 'json');
};

Fereol.Enrollment.CourseTerm.prototype.toString = function()
{
	return this.scheduleTerm.toString();
};
