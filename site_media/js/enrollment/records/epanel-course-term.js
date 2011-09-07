/**
 * Model terminu przedmiotu, do wyświetlenia w widoku przedmiotu.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.EPanelCourseTerm = function()
{
	this.courseTerm = null; // model danych
	this.course = null; // SchedulePrototype.PrototypeCourse
};

Fereol.Enrollment.EPanelCourseTerm.fromHTML = function(container)
{
	container.assertOne();

	var sterm = new Fereol.Enrollment.EPanelCourseTerm();
	sterm._container = container;

	sterm.courseTerm = Fereol.Enrollment.CourseTerm.fromJSON(container.
		find('input[name=group-json]').assertOne().attr('value'));

	sterm._groupLimitCell = container.find('td.termLimit').assertOne();
	sterm._enrolledCountCell = container.find('td.termEnrolledCount').
		assertOne();
	sterm._queuedCountCell = container.find('td.termQueuedCount').assertOne();

	return sterm;
};

/**
 * Zamienia zwykłe kontrolki (np. przyciski zapisywania) w ajax-owe.
 */
Fereol.Enrollment.EPanelCourseTerm.prototype.convertControlsToAJAX = function()
{
	var self = this;

	var setEnrolledForm = this._container.find('.setEnrolled').assertOne();

	// Opera nie potrafi łamać wierszy w input[type=button]
	if ($.browser.opera)
	{
		this._setEnrolledButton = $.create('button', {
			className: 'setEnrolledButton'
		}).insertAfter(setEnrolledForm);
		this._setEnrolledButtonAlternative = true;
	}
	else
	{
		this._setEnrolledButton = $.create('input', {
			type: 'button',
			className: 'setEnrolledButton'
		}).insertAfter(setEnrolledForm);
		this._setEnrolledButtonAlternative = false;
	}

	setEnrolledForm.remove();
	this._setEnrolledButton.click(function()
	{
		MessageBox.clear();
		self.setEnrolled(self._setEnrolledAction);
	});

	var priorityCell = this._container.find('td.priority').assertOne();
	priorityCell.empty();
	this._prioritySelector = $.create('select').appendTo(priorityCell);
	for (var i = 1; i <= CourseView.priorityLimit; i++)
	{
		var priorityOption = $.create('option', {value: i}).text(i);
		if (i == 1)
			priorityOption.text('1 (w ostateczności)');
		if (i == CourseView.priorityLimit)
			priorityOption.text(CourseView.priorityLimit + ' (bardzo chcę)');
		if (i === this.courseTerm.queuePriority)
			priorityOption.attr('selected', 'selected');
		this._prioritySelector.append(priorityOption);
	}
	this._prioritySelector.change(function()
	{
		MessageBox.clear();
		self.changePriority(self._prioritySelector.attr('value').
			castToInt());
	});

	this.refreshView();
};

/**
 * Odświeża wiersz terminu na podstawie danych z modelu javascriptowego.
 */
Fereol.Enrollment.EPanelCourseTerm.prototype.refreshView = function()
{
	this._prioritySelector.toggle(this.courseTerm.isQueued);
	this._container.toggleClass('signed', this.courseTerm.isEnrolled);

	this._setEnrolledAction = null;
	var newEnrolledButtonLabel = null;
	if (this.courseTerm.isEnrolled)
	{
		this._setEnrolledAction = false;
		newEnrolledButtonLabel = 'wypisz';
	}
	else if (!this.courseTerm.isFull())
	{
		this._setEnrolledAction = true;
		newEnrolledButtonLabel = 'zapisz'; //TODO: przenieś
	}
	else if (this.courseTerm.isQueued)
	{
		this._setEnrolledAction = false;
		newEnrolledButtonLabel = 'wypisz z kolejki';
		this._prioritySelector.children('option').attr('selected', false);
		this._prioritySelector.children('option[value=' + this.courseTerm.queuePriority +
			']').attr('selected', 'selected');
	}
	else
	{
		this._setEnrolledAction = true;
		newEnrolledButtonLabel = 'zapisz do kolejki';
	}

	if (this._setEnrolledButtonAlternative)
		this._setEnrolledButton.text(newEnrolledButtonLabel);
	else
		this._setEnrolledButton.attr('value', newEnrolledButtonLabel);

	this._groupLimitCell.text(
		this.courseTerm.unavailableLimit ?
			(this.courseTerm.availableLimit() + ' + ' +
				this.courseTerm.unavailableLimit) :
			this.courseTerm.limit
	);
	this._enrolledCountCell.text(
		this.courseTerm.unavailableLimit ?
			(this.courseTerm.availableEnrolledCount() + ' + ' +
				this.courseTerm.unavailableEnrolledCount) :
			this.courseTerm.enrolledCount
	);
	this._queuedCountCell.text(this.courseTerm.queuedCount);
};

/**
 * Zmienia priorytet grupy.
 *
 * @param newPriority nowy priorytet (1-10)
 */
Fereol.Enrollment.EPanelCourseTerm.prototype.changePriority = function(newPriority)
{
	var self = this;
	this._prioritySelector.attr('disabled', true);
	if (newPriority < 1 || newPriority > CourseView.priorityLimit)
		throw new Error('Nieprawidłowy priorytet do ustawienia');

	$.dataInvalidate();
	
	$.post(Fereol.Enrollment.CourseTerm._setQueuePriorityURL, {
			id: this.courseTerm.id,
			priority: newPriority
		}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		if (result.isSuccess())
			self._prioritySelector.attr('disabled', false);
		else
			result.displayMessageBox();
	}, 'json');
};

/**
 * Zapisuje lub wypisuje użytkownika do/z grupy lub kolejki (w zależności od
 * wolnych miejsc.
 *
 * Założenie: zmiany limitów grup odbywają się rzadko. Zmiana taka może
 * spowodować operowanie na nieświeżych danych, np. użytkownik może obserwować
 * nieprawidłowe liczniki grup. Na przykład, jeżeli przy próbie zapisania się
 * do grupy (w której było 10 zajętych miejsc na 20 w sumie) zostaną
 * zmniejszone w niej limity (do równo 10), użytkownik zamiast stanu 10/10
 * ujrzy 20/20 (i siebie w kolejce). Po odświeżeniu zobaczy prawidłowy stan.
 *
 * Zawsze jedak akcja "zapisania" zapisze go do grupy lub kolejki, akcja
 * "wypisania" analogicznie wypisze. Akcja "zapisania", jeżeli zapisze go do
 * kolejki, NIE wypisze z grupy, niezależnie od etykiety przycisku (która może
 * brzmieć "przepisz do innej grupy").
 *
 * @param enroll true, jeżeli zapisać; false aby wypisać
 */
Fereol.Enrollment.EPanelCourseTerm.prototype.setEnrolled = function(enroll)
{
	if (!Fereol.Enrollment.EPanelCourseTerm._setLoading(true))
		return;
	$.dataInvalidate();

	var self = this;
	enroll = !!enroll;

	$.post(Fereol.Enrollment.CourseTerm._setEnrolledURL, {
		group: this.courseTerm.id,
		enroll: enroll
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		self._isLoading = false;
		if (result.isSuccess() ||
			result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			if (self.courseTerm.isEnrolled)
			{
				self.courseTerm.isEnrolled = false;
				self.courseTerm.enrolledCount--;
			}
			if (self.courseTerm.isQueued)
			{
				self.courseTerm.isQueued = false;
				self.courseTerm.queuedCount--;
			}
		}
		if (result.isSuccess())
		{
			if (enroll)
			{
				self.courseTerm.isEnrolled = true;
				self.courseTerm.enrolledCount++;

				// zaznaczanie innych grup tego samego typu jako "nie zapisane"
				CourseView._termsList.forEach(function(e)
				{
					if (e.id == self.courseTerm.id || e.type != self.courseTerm.type)
						return;
					if (e.courseTerm.isEnrolled)
					{
						e.courseTerm.isEnrolled = false;
						e.courseTerm.enrolledCount--;
					}
					e.refreshView();
				});

				// zaznaczanie powiązanych jako "zapisane"
				result.data['connected_group_ids'].forEach(
					function(alsoEnrolledID)
				{
					if (alsoEnrolledID == self.courseTerm.id)
						return;
					var alsoEnrolled = CourseView._termsMap[alsoEnrolledID];
					if (!alsoEnrolled.courseTerm.isEnrolled)
					{
						alsoEnrolled.courseTerm.isEnrolled = true;
						alsoEnrolled.courseTerm.enrolledCount++;
					}
					alsoEnrolled.refreshView();
				})
			}
			else if (self.courseTerm.type == 1) // wykład
			{
				// zaznaczenie innych grup z tego przedmiotu jako "nie zapisane"
				// (wypisanie z wykładu skutkuje wypisaniem z całego przedmiotu)
				CourseView._termsList.forEach(function(e)
				{
					if (e.id == self.courseTerm.id)
						return;
					if (e.courseTerm.isEnrolled)
					{
						e.courseTerm.isEnrolled = false;
						e.courseTerm.enrolledCount--;
					}
					e.refreshView();
				});
			}
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			self.courseTerm.isQueued = true;
			self.courseTerm.queuedCount++;
			if (self.courseTerm.enrolledCount < self.courseTerm.limit)
				self.courseTerm.enrolledCount = self.courseTerm.limit;
			self.queuePriority = 1;
			result.displayMessageBox();
		}
		else
			result.displayMessageBox();
		self.refreshView();
		Fereol.Enrollment.EPanelCourseTerm._setLoading(false);
	}, 'json');
};

/**
 * Włącza lub wyłącza tryb komunikacji z serwerem. W tym trybie może być tylko
 * jeden "wątek".
 *
 * @param loading true, jeżeli włączyć
 * @return true, jeżeli zakończono powodzeniem
 */
Fereol.Enrollment.EPanelCourseTerm._setLoading = function(loading)
{
	loading = !!loading;
	if (loading && Fereol.Enrollment.EPanelCourseTerm._isLoading)
		return false;
	Fereol.Enrollment.EPanelCourseTerm._isLoading = loading;
	$('input.setEnrolledButton').attr('disabled', loading);
	return true;
};

Fereol.Enrollment.EPanelCourseTerm.prototype.toString = function()
{
	return 'EPanelCourseTerm';
};
