/**
 * Model terminu przedmiotu, do wyświetlenia w widoku przedmiotu.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.CourseTerm = function()
{
	this.id = null;

	this.isEnrolled = false; // czy student jest zapisany
	this.isQueued = false; // czy jest "w kolejce"
	this.queuePriority = null; // jeżeli jest w kolejce, to jaki ma priorytet

	this.groupLimit = null;
	this.enrolledCount = null;
	this.queuedCount = null;
	this.course = null; // SchedulePrototype.PrototypeCourse

	this._queuePrioritySetURL = null;
};

Fereol.Enrollment.CourseTerm.fromHTML = function(container)
{
	container.assertOne();

	var sterm = new Fereol.Enrollment.CourseTerm();
	sterm._container = container;

	sterm.id = container.find('input[name=group-id]').assertOne().attr('value').
		castToInt();
	sterm.type = container.parent().parent().parent().
		children('input[name=tutorial-type]').assertOne().attr('value').castToInt();

	sterm._groupLimitCell = container.find('td.termLimit').assertOne();
	sterm._enrolledCountCell = container.find('td.termEnrolledCount').
		assertOne();
	sterm._queuedCountCell = container.find('td.termQueuedCount').assertOne();

	sterm.groupLimit = sterm._groupLimitCell.text().castToInt();
	sterm.enrolledCount = sterm._enrolledCountCell.text().castToInt();
	sterm.queuedCount = sterm._queuedCountCell.text().castToInt();
	sterm.isEnrolled = container.find('input[name=is-signed-in]').assertOne().
		attr('value').castToBool();

	if (!Fereol.Enrollment.CourseTerm._setEnrolledURL)
		Fereol.Enrollment.CourseTerm._setEnrolledURL =
			$('input[name=ajax-set-enrolled-url]').assertOne().attr('value');

	var priorityCell = container.find('td.priority').assertOne();
	sterm._queuePrioritySetURL = priorityCell.
		children('input[name=ajax-priority-url]').assertOne().attr('value');
	if (priorityCell.children('form').length > 0)
	{
		sterm.isQueued = true;
		sterm.queuePriority = priorityCell.children('span').assertOne().text().
			castToInt();
	}

	return sterm;
};

/**
 * Zamienia zwykłe kontrolki (np. przyciski zapisywania) w ajax-owe.
 */
Fereol.Enrollment.CourseTerm.prototype.convertControlsToAJAX = function()
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
	for (var i = 1; i <= priority_limit; i++)
	{
		var priorityOption = $.create('option', {value: i}).text(i);
		if (i === this.queuePriority)
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
Fereol.Enrollment.CourseTerm.prototype.refreshView = function()
{
	this._prioritySelector.toggle(this.isQueued);
	this._container.toggleClass('signed', this.isEnrolled);

	this._setEnrolledAction = null;
	var newEnrolledButtonLabel = null;
	if (this.isEnrolled)
	{
		this._setEnrolledAction = false;
		newEnrolledButtonLabel = 'wypisz';
	}
	else if (!this.isFull())
	{
		this._setEnrolledAction = true;
		newEnrolledButtonLabel = 'zapisz'; //TODO: przenieś
	}
	else if (this.isQueued)
	{
		this._setEnrolledAction = false;
		newEnrolledButtonLabel = 'wypisz z kolejki';
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

	this._enrolledCountCell.text(this.enrolledCount);
	this._queuedCountCell.text(this.queuedCount);
};

/**
 * @return true, jeżeli grupa jest pełna
 */
Fereol.Enrollment.CourseTerm.prototype.isFull = function()
{
	if (this.groupLimit === null ||
		this.enrolledCount === null)
		throw new Error('NullPointerException');
	return this.groupLimit <= this.enrolledCount;
};

/**
 * Zmienia priorytet grupy.
 *
 * @param newPriority nowy priorytet (1-10)
 */
Fereol.Enrollment.CourseTerm.prototype.changePriority = function(newPriority)
{
	var self = this;
	this._prioritySelector.attr('disabled', true);
	if (newPriority < 1 || newPriority > priority_limit)
		throw new Error('Nieprawidłowy priorytet do ustawienia');
	
	$.post(this._queuePrioritySetURL, {
			csrfmiddlewaretoken: $.cookie('csrftoken'),
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
Fereol.Enrollment.CourseTerm.prototype.setEnrolled = function(enroll)
{
	if (!Fereol.Enrollment.CourseTerm._setLoading(true))
		return;

	var self = this;
	enroll = !!enroll;

	$.post(Fereol.Enrollment.CourseTerm._setEnrolledURL, {
		csrfmiddlewaretoken: $.cookie('csrftoken'),
		group: this.id,
		enroll: enroll
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		self._isLoading = false;
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
		if (result.isSuccess())
		{
			if (enroll)
			{
				self.isEnrolled = true;
				self.enrolledCount++;

				// zaznaczanie innych grup tego samego typu jako "nie zapisane"
				CourseView._termsList.forEach(function(e)
				{
					if (e.id == self.id || e.type != self.type)
						return;
					if (e.isEnrolled)
					{
						e.isEnrolled = false;
						e.enrolledCount--;
					}
					e.refreshView();
				});

				// zaznaczanie powiązanych jako "zapisane"
				result.data.forEach(function(alsoEnrolledID)
				{
					if (alsoEnrolledID == self.id)
						return;
					var alsoEnrolled = CourseView._termsMap[alsoEnrolledID];
					if (!alsoEnrolled.isEnrolled)
					{
						alsoEnrolled.isEnrolled = true;
						alsoEnrolled.enrolledCount++;
					}
					alsoEnrolled.refreshView();
				})
			}
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
		{
			self.isQueued = true;
			self.queuedCount++;
			if (self.enrolledCount < self.groupLimit)
				self.enrolledCount = self.groupLimit;
			result.displayMessageBox();
		}
		else
			result.displayMessageBox();
		self.refreshView();
		Fereol.Enrollment.CourseTerm._setLoading(false);
	}, 'json');
};

/**
 * Włącza lub wyłącza tryb komunikacji z serwerem. W tym trybie może być tylko
 * jeden "wątek".
 *
 * @param loading true, jeżeli włączyć
 * @return true, jeżeli zakończono powodzeniem
 */
Fereol.Enrollment.CourseTerm._setLoading = function(loading)
{
	loading = !!loading;
	if (loading && Fereol.Enrollment.CourseTerm._isLoading)
		return false;
	Fereol.Enrollment.CourseTerm._isLoading = loading;
	$('input.setEnrolledButton').attr('disabled', loading);
	return true;
};

Fereol.Enrollment.CourseTerm.prototype.toString = function()
{
	return 'CourseTerm';
}
