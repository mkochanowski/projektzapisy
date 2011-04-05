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
	this.scheduleTerm = null; //Schedule.Term
	this.container = $.create('div');

	this.isPinned = false; // czy jest "przypięty"
	this.isEnrolled = false; // czy student jest zapisany
	this.isPrototyped = false; // czy jest tymczasowo wyświetlony w prototypie

	this._isVisible = false;

	this.schedule = null;
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
		SchedulePrototype.schedule.addTerm(this.scheduleTerm);
	else
		SchedulePrototype.schedule.removeTerm(this.scheduleTerm);
};
