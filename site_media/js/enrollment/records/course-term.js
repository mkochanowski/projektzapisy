/**
 * Model terminu przedmiotu, do operacji na danych.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.CourseTerm = function()
{
	this.id = null;
	this.type = null;

	this.isEnrolled = null; // czy student jest zapisany
	this.isQueued = null; // czy jest "w kolejce"
	this.isPinned = null; // czy przypiął do planu
	this.queuePriority = null; // jeżeli jest w kolejce, to jaki ma priorytet

	// w przypadku studentów nie zamawianych - zamawiana część grupy jest
	// "niedostępna"
	this.limit = null;
	this.unavailableLimit = null;
	this.enrolledCount = null;
	this.unavailableEnrolledCount = null;
	this.queuedCount = null;

	this.updateListeners = [];

	if (!Fereol.Enrollment.CourseTerm._setEnrolledURL)
		Fereol.Enrollment.CourseTerm._setEnrolledURL =
			$('input[name=ajax-set-enrolled-url]').assertOne().attr('value');
	if (!Fereol.Enrollment.CourseTerm._setQueuePriorityURL)
		Fereol.Enrollment.CourseTerm._setQueuePriorityURL =
			$('input[name=ajax-set-queue-priority-url]').assertOne().
				attr('value');
	if (!Fereol.Enrollment.CourseTerm._priorityLimit)
		Fereol.Enrollment.CourseTerm._priorityLimit =
			$('input[name=priority-limit]').assertOne().attr('value').
				castToInt();
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

Fereol.Enrollment.CourseTerm._byID = {};

Fereol.Enrollment.CourseTerm.prototype._register = function()
{
	Fereol.Enrollment.CourseTerm._byID[this.id] = this;
};

Fereol.Enrollment.CourseTerm.prototype._notifyUpdateListeners = function()
{
	this.updateListeners.forEach(function(listener)
	{
		listener();
	});
};

Fereol.Enrollment.CourseTerm.fromJSON = function(json)
{
	var raw = $.parseJSON(json);

	var ct = new Fereol.Enrollment.CourseTerm();

	ct.id = raw['id'].castToInt();
	ct.type = raw['type'].castToInt();
	ct.updateFromJSON(json);

	ct._register();
	return ct;
};

Fereol.Enrollment.CourseTerm.prototype.updateFromJSON = function(json)
{
	var raw = $.parseJSON(json);

	this.isEnrolled = !!raw['is_enrolled'];
	this.isQueued = !!raw['is_queued'];
	this.isPinned = !!raw['is_pinned'];

	this.limit = raw['limit'].castToInt();
	this.unavailableLimit = raw['unavailable_limit'].castToInt();
	this.enrolledCount = raw['enrolled_count'].castToInt();
	this.unavailableEnrolledCount = raw['unavailable_enrolled_count'].castToInt();
	this.queuedCount = raw['queued_count'].castToInt();
	if (this.isQueued)
		this.queuePriority = raw['queue_priority'].castToInt();
};

Fereol.Enrollment.CourseTerm.prototype.availableLimit = function()
{
	if (this.limit === null ||
		this.unavailableLimit === null)
		throw new Error('NullPointerException');
	return this.limit - this.unavailableLimit;
};

Fereol.Enrollment.CourseTerm.prototype.availableEnrolledCount = function()
{
	if (this.enrolledCount === null ||
		this.unavailableEnrolledCount === null)
		throw new Error('NullPointerException');
	return this.enrolledCount - this.unavailableEnrolledCount;
};

/**
 * @return true, jeżeli grupa jest pełna
 */
Fereol.Enrollment.CourseTerm.prototype.isFull = function()
{
	return this.availableLimit() <= this.availableEnrolledCount();
};

/******************************************************************************/

/**
 * Zapisuje lub wypisuje użytkownika do/z grupy lub kolejki (w zależności od
 * wolnych miejsc.
 *
 * @param enroll true, jeżeli zapisać; false aby wypisać
 */
Fereol.Enrollment.CourseTerm.prototype.setEnrolled = function(enroll)
{
	if (!Fereol.Enrollment.CourseTerm._setLoading(true))
		return;
	$.dataInvalidate();

	var self = this;
	enroll = !!enroll;

	$.post(Fereol.Enrollment.CourseTerm._setEnrolledURL, {
		group: this.id,
		enroll: enroll
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);

		if (result.isSuccess())
		{
			// do nothing special
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
			result.displayMessageBox();
		else
			result.displayMessageBox();

		if (result.data)
		{
			for (var gid in result.data)
				Fereol.Enrollment.CourseTerm._byID[gid].
					updateFromJSON(result.data[gid]);
			for (var gid in result.data)
				Fereol.Enrollment.CourseTerm._byID[gid]._notifyUpdateListeners();
		}
		
		Fereol.Enrollment.CourseTerm._setLoading(false);
	}, 'json');
};

/**
 * Zmienia priorytet grupy.
 *
 * @param newPriority nowy priorytet (1-10)
 */
Fereol.Enrollment.CourseTerm.prototype.changePriority = function(newPriority)
{
	if (!Fereol.Enrollment.CourseTerm._setLoading(true))
		return;

	var self = this;
	if (newPriority < 1 ||
		newPriority > Fereol.Enrollment.CourseTerm._priorityLimit)
		throw new Error('Nieprawidłowy priorytet do ustawienia');

	$.dataInvalidate();

	$.post(Fereol.Enrollment.CourseTerm._setQueuePriorityURL, {
			id: this.id,
			priority: newPriority
		}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		if (result.isSuccess())
		{
			Fereol.Enrollment.CourseTerm._setLoading(false);
			this._notifyUpdateListeners();
		}
		else
			result.displayMessageBox();
	}, 'json');
};

/******************************************************************************/

Fereol.Enrollment.CourseTerm.prototype.toString = function()
{
	return 'CourseTerm#' + this.id;
}

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
	Fereol.Enrollment.CourseTerm.loadingListeners.forEach(function(e)
	{
		e(loading);
	});
	return true;
};

Fereol.Enrollment.CourseTerm.loadingListeners = [];
