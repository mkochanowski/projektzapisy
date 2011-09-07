/**
 * Model terminu przedmiotu, do wyświetlenia w widoku przedmiotu.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.EPanelCourseTerm = function()
{
	this.courseTerm = null; // model danych
};

Fereol.Enrollment.EPanelCourseTerm.fromHTML = function(container)
{
	container.assertOne();

	var sterm = new Fereol.Enrollment.EPanelCourseTerm();
	sterm._container = container;

	sterm.courseTerm = Fereol.Enrollment.CourseTerm.fromJSON(container.
		find('input[name=group-json]').assertOne().attr('value'));
	sterm.courseTerm.updateListeners.push(function() { sterm.refreshView(); });

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
		self.courseTerm.setEnrolled(self._setEnrolledAction);
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
		self.courseTerm.changePriority(self._prioritySelector.attr('value').
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

Fereol.Enrollment.EPanelCourseTerm.prototype.toString = function()
{
	return 'EPanelCourseTerm';
};

Fereol.Enrollment.CourseTerm.loadingListeners.push(function(isLoading)
{
	$('input.setEnrolledButton').attr('disabled', isLoading);
	$('td.priority select').attr('disabled', isLoading);
});
