/**
 * Model terminu przedmiotu, tzn zakresu godzinowego dla określonej grupy
 * z określonego przedmiotu, do wyświetlenia w prototypie planu lub terminarzu.
 *
 * TODO: przetestować dla niespójnych id grup i terminów (w danych przykładowych
 * wszystkie id terminów pokrywają się z id grup).
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.ScheduleCourseTerm = function()
{
	this.group = null; // model danych

	this.id = null;
	this.groupID = null;
	this.groupURL = null;
	this.scheduleTerm = null; // Schedule.Term
	this.container = $.create('div');
	this.popupContents = $.create('div');

	this.displayStyle =
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE;

	this.limit = null; // limit osób w grupie
	this.enrolledCount = null; // ilość osób zapisanych do grupy
	this.queuedCount = null; // ilość osób w kolejce

	this._containerReady = false;
	this._controlsReady = false;

	this.isPinned = false; // czy jest "przypięty"
	this.isEnrolled = false; // czy student jest zapisany
	this.isPrototyped = false; // czy jest tymczasowo wyświetlony w prototypie
	this.isQueued = false; // czy jest "w kolejce"

	this._isLoading = false; // czy w tej chwili trwa komunikacja z serwerem
	this._isVisible = false;

	this.schedule = null;
	this.course = null; // SchedulePrototype.PrototypeCourse lub Schedule.PrototypeCourse

	this.classroom = null;
	this.teacher = null;
	this.teacherURL = null;
	this.type = null;
};

Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle = {
	SCHEDULE: 1,
	PROTOTYPE: 2
};

Fereol.Enrollment.ScheduleCourseTerm.byGroups = {};

Fereol.Enrollment.ScheduleCourseTerm.prototype.isEnrolledOrQueued = function()
{
	return this.isEnrolled || this.isQueued;
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.isFull = function()
{
	return this.limit <= this.enrolledCount;
};

Fereol.Enrollment.ScheduleCourseTerm.fromJSON = function(json, readOnly)
{
	var sterm = new Fereol.Enrollment.ScheduleCourseTerm();
	var raw = $.parseJSON(json)

	sterm.id = raw.id.castToInt();
	sterm.groupID = raw.group.castToInt();
	sterm.groupURL = raw.group_url;
	sterm.scheduleTerm = new Schedule.Term(
		raw.day.castToInt() - 1,
		new Schedule.Time(raw.start_time[0].castToInt(), raw.start_time[1].castToInt()),
		new Schedule.Time(raw.end_time[0].castToInt(), raw.end_time[1].castToInt()),
		sterm.container,
		sterm.popupContents
	);
	sterm.scheduleTerm.onResize = function(isFullSize)
	{
		sterm._onResize(isFullSize);
	};

	sterm.limit = raw.limit.castToInt();
	sterm.enrolledCount = (raw.enrolled_count === undefined ? null :
		raw.enrolled_count.castToInt());
	sterm.queuedCount = (raw.queued_count === undefined ? null :
		raw.queued_count.castToInt());

	sterm.classroom = raw.classroom.castToInt();
	sterm.teacher = raw.teacher;
	sterm.teacherURL = raw.teacher_url;
	sterm.type = raw.group_type.castToInt();

	if (!Fereol.Enrollment.ScheduleCourseTerm.byGroups[sterm.groupID])
		Fereol.Enrollment.ScheduleCourseTerm.byGroups[sterm.groupID] = [];
	Fereol.Enrollment.ScheduleCourseTerm.byGroups[sterm.groupID].push(sterm);

	return sterm;
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.assignSchedule = function(schedule)
{
	this.schedule = schedule;
	this._updateVisibility();
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._updateVisibility = function()
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
			Fereol.Enrollment.CourseGroup.groupTypes[this.type][0]);

		this._classroomLabel = $.create('span', {className: 'classroom'}).
			appendTo(this.container);
		if (this.classroom)
			this._classroomLabel.text('s. ' + this.classroom);

		this._controlsBox = null;
		if (this.displayStyle ==
			Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE)
		{
			this._controlsBox = $.create('div', {className: 'controls'}).
				appendTo(this.container).css('display', 'none');

			this._pinUnpinButton = $.create('span', { className: 'pinUnpin'}).
				appendTo(this._controlsBox);
			this._signInOutButton = $.create('span', { className: 'signInOut'}).
				appendTo(this._controlsBox);
			this._loadingIndicator =
				$.create('div', { className: 'loadingIndicator'}).
				appendTo(this._controlsBox).css('display', 'none');

			this.container.mouseenter(function()
			{
				if (!self._controlsEmpty)
					self._controlsBox.css('display', 'block');
			}).mouseleave(function()
			{
				self._controlsBox.css('display', 'none');
			});
			this._controlsBox.click(function(ev)
			{
				ev.stopPropagation();
			});
		}

		this.container.click(function()
		{
			self._generatePopup();
			self.scheduleTerm.setPopupVisible(true);
		});
		this.popupContents.mouseleave(function()
		{
			self.scheduleTerm.setPopupVisible(false);
		});
	}
	this._updateControls();

	this.container.toggleClass('enrolled', this.isEnrolled);
	this.container.toggleClass('queued', this.isQueued);
	this.container.toggleClass('full', this.isFull() && !this.isEnrolled && !this.isQueued);

	var shouldBeVisible = (this.isPinned || this.isEnrolled ||
		this.isPrototyped || this.isQueued);
	if (shouldBeVisible == this._isVisible)
		return;
	this._isVisible = shouldBeVisible;
	if (shouldBeVisible)
		this.schedule.addTerm(this.scheduleTerm);
	else
	{
		this.schedule.removeTerm(this.scheduleTerm);
		if (this._controlsBox)
			this._controlsBox.css('display', 'none');
	}
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._generatePopup = function()
{
	this.popupContents.empty();
	
	$.create('h2', {className: 'name'}).appendTo(this.popupContents).append(
		$.create('a').text(this.course.name).attr('href', this.course.url));
	$.create('p', {className: 'typeAndTerm'}).text(
		Fereol.Enrollment.CourseGroup.groupTypes[this.type][0].
			capitalize() +
		' (' + Schedule.dayNames[this.scheduleTerm.day].toLowerCase() + ' ' +
		this.scheduleTerm.timeFrom.toString() + '-' +
		this.scheduleTerm.timeTo.toString() + ')'
	).appendTo(this.popupContents);
    if(this.teacherURL==''){
        $.create('p', {className: 'teacher'}).text('Prowadzący: ').        
            appendTo(this.popupContents).append($.create('span').text(this.teacher));
    }
    else {
        $.create('p', {className: 'teacher'}).text('Prowadzący: ').
            appendTo(this.popupContents).append($.create('a').text(this.teacher).        
            attr('href', this.teacherURL));
    }
	$.create('p', {className: 'classroom'}).text(
		'Sala: ' + this.classroom
	).appendTo(this.popupContents);

	if (this.displayStyle ==
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE)
	{
		var enrolled = $.create('p', {className: 'enrolledCount'}).
			text('Zapisanych: ').appendTo(this.popupContents);
		$.create('a', {
			href: this.groupURL,
			title: 'zapisanych osób: ' + this.enrolledCount +
				', limit miejsc w grupie: ' + this.limit
		}).appendTo(enrolled).
			text(this.enrolledCount + '/' + this.limit);
		if (this.enrolledCount >= this.limit && !this.isEnrolled &&
			!this.isQueued)
			$.create('img', {
				src: '/site_media/images/warning.png',
				alt: '(brak wolnych miejsc)',
				title: 'nie ma wolnych miejsc w tej grupie, możesz zapisać ' +
					'się do kolejki'
			}).appendTo(enrolled.appendSpace());
		if (this.queuedCount > 0)
			$.create('span').text('(w kolejce: ' + this.queuedCount + ')').
				appendTo(enrolled.appendSpace());

		if (this.isEnrolledOrQueued())
		{
			var einfo = $.create('p', { className: 'enrolledInfo'}).
				appendTo(this.popupContents);
			if (this.isEnrolled)
				einfo.text('Jesteś zapisany do tej grupy.');
			if (this.isQueued)
				einfo.text('Jesteś w kolejce do tej grupy.');
		}
	}
	else if (this.displayStyle ==
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE)
	{
		$.create('p', {className: 'groupListLink'}).appendTo(
			this.popupContents).append($.create('a', {
			href: this.groupURL
		}).text('lista osób zapisanych do grupy'));
	}
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._updateControls = function()
{
	var self = this;
	if (!this._controlsBox)
		return;
	
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
		if (self._controlsBox)
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

Fereol.Enrollment.ScheduleCourseTerm.prototype._onResize = function(isFullSize)
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

	this._typeLabel.text(Fereol.Enrollment.CourseGroup.
		groupTypes[this.type][isFullSize?0:1]).css({
		top: (this._typeLabel.parent().innerHeight() -
			this._typeLabel.height() -
			CLASSROOM_PADDING) + 'px'
	});

	this._teacherLabel.css({
		display: isFullSize ? 'block' : 'none'
	});
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.setPrototyped = function(prototyped)
{
	this.isPrototyped = prototyped;
	this._updateVisibility();
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.setPinned = function(pinned)
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

Fereol.Enrollment.ScheduleCourseTerm.prototype.setEnrolled = function(enrolled)
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
		group: this.groupID,
		enroll: enrolled
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		self._isLoading = false;
		if (result.isSuccess() ||
			result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			if (self.isEnrolled)
			{
				self.isEnrolled = false;
				self.enrolledCount--;
			}
			if (self.isQueued)
			{
				self.isQueued = false;
				self.queuedCount--;
			}
		}
		if (result.isSuccess())
		{
			self.isPinned = false;
			if (enrolled)
			{
				self.isEnrolled = true;
				self.enrolledCount++;

				// zaznaczanie innych grup tego samego typu jako "nie zapisane"
				self.course.terms.forEach(function(e)
				{
					if (e.groupID == self.groupID || e.type != self.type)
						return;
					if (e.isEnrolled)
					{
						e.isEnrolled = false;
						e.enrolledCount--;
					}
					e._updateVisibility();
				});

				$.log(result.data);
				//TODO

				// zaznaczanie powiązanych jako "zapisane"
				result.data['connected_group_ids'].forEach(function(e)
				{
					if (e == self.groupID)
						return;
					Fereol.Enrollment.ScheduleCourseTerm.byGroups[e].forEach(function(alsoEnrolledTo)
					{
						if (!alsoEnrolledTo.isEnrolled)
						{
							alsoEnrolledTo.isEnrolled = true;
							alsoEnrolledTo.enrolledCount++;
							alsoEnrolledTo.isPinned = false;
						}
						alsoEnrolledTo._updateVisibility();
					});
				})
			}
			else if (self.type == 1) // wykład
			{
				// zaznaczenie innych grup z tego przedmiotu jako "nie zapisane"
				// (wypisanie z wykładu skutkuje wypisaniem z całego przedmiotu)
				self.course.terms.forEach(function(e)
				{
					if (e.groupID == self.groupID)
						return;
					if (e.isEnrolled)
					{
						e.isEnrolled = false;
						e.enrolledCount--;
					}
					e._updateVisibility();
				});
			}
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			self.isQueued = true;
			self.queuedCount++;
			self.isPinned = false;
			if (self.enrolledCount < self.limit)
				self.enrolledCount = self.limit;
			result.displayMessageBox();
		}
		else
			result.displayMessageBox();
		self._updateVisibility();
	}, 'json');
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.toString = function()
{
	return this.course.toString() + ' - ' + this.scheduleTerm.toString();
};
