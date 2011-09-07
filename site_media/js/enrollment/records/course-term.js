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

	if (!Fereol.Enrollment.CourseTerm._setEnrolledURL)
		Fereol.Enrollment.CourseTerm._setEnrolledURL =
			$('input[name=ajax-set-enrolled-url]').assertOne().attr('value');
	if (!Fereol.Enrollment.CourseTerm._setQueuePriorityURL)
		Fereol.Enrollment.CourseTerm._setQueuePriorityURL =
			$('input[name=ajax-set-queue-priority-url]').assertOne().
				attr('value');
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

Fereol.Enrollment.CourseTerm.fromJSON = function(json)
{
	var raw = $.parseJSON(json);

	var ct = new Fereol.Enrollment.CourseTerm();

	ct.id = raw['id'].castToInt();
	ct.type = raw['type'].castToInt();
	ct.updateFromJSON(json);

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

Fereol.Enrollment.CourseTerm.prototype.toString = function()
{
	return 'CourseTerm#' + this.id;
}
