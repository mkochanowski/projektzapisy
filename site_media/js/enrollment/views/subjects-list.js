/**
 * Kod odpowiedzialny za listę przedmiotów w systemie zapisów.
 */

SubjectsList = new Object();

/**
 * Inicjuje widok listy przedmiotów.
 */
SubjectsList.init = function()
{
	SubjectsList.initSubjectLists();
	SubjectsList.initFilter();
};

$(SubjectsList.init);

/**
 * Inicjuje listy przedmiotów i semestrów (model).
 */
SubjectsList.initSubjectLists = function()
{
	SubjectsList.subjects = new Object();
	SubjectsList.semesters = new Object();

	$('#subject-list').assertOne().children('div.semester').
		each(function(i, semesterContainer)
	{
		semesterContainer = $(semesterContainer);

		var semester = new SubjectsList.Semester();
		semester.id = semesterContainer.children('input[name=semester-id]').
			assertOne().attr('value').castToInt();
		semester.name = semesterContainer.children('h2').assertOne().
			children('span').assertOne().text();
		semester.container = semesterContainer;
		SubjectsList.semesters[semester.id] = semester;

		semesterContainer.children('ul').assertOne().children('li').
			each(function(i, subjectContainer)
		{
			subjectContainer = $(subjectContainer);
			var link = subjectContainer.children('a').assertOne();

			var subject = new SubjectsList.Subject();
			subject.id = link.attr('id').removePrefix('subject-').castToInt();
			subject.name = link.text().trim();
			subject.type = subjectContainer.children('input[name=type]').
				assertOne().attr('value').castToInt();
			subject.container = subjectContainer;
			subject.wasEnrolled = subjectContainer.children('input[name=wasEnrolled]').
				assertOne().attr('value').castToBool();
			semester.addSubject(subject);
			SubjectsList.subjects[subject.id] = subject;
		});
	});
};

/**
 * Inicjuje filtrowanie.
 */
SubjectsList.initFilter = function()
{
	var subjectFilterForm = $('#enr-subjectsList-top-bar').assertOne();

	subjectFilterForm.css('display', 'block');

	subjectFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		subjectFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	SubjectsList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden przedmiot.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#subject-list').assertOne());
	SubjectsList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	SubjectsList.subjectFilter = new ListFilter('subjectsList-subjects', subjectFilterForm.getDOM());
	
	SubjectsList.subjectFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (SubjectsList.emptyFilterWarningVisible == visible)
			return;
		SubjectsList.emptyFilterWarningVisible = visible;
		SubjectsList.emptyFilterWarning.css('display', visible?'':'none');
	};

	SubjectsList.subjectFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var subject = element.data;
		if (!subject.name)
			$.log(subject);
		return (subject.name.toLowerCase().indexOf(value) >= 0);
	}));

	SubjectsList.subjectFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'semester', '#enr-subjectFilter-semester', function(element, option)
	{
		if (!option || option == 0)
			return true;
		var subject = element.data;
		return (subject.semester.id == option);
	}));

	SubjectsList.subjectFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		if (!value)
			return true;
		var subject = element.data;
		return !subject.wasEnrolled;
	}));

	SubjectsList.subjectFilter.addFilter(ListFilter.CustomFilters.createSubjectTypeFilter(
		function(element, subjectType)
	{
		var subject = element.data;
		return (subject.type == subjectType);
	}));

	for (var subject in SubjectsList.subjects)
	{
		subject = SubjectsList.subjects[subject];
		SubjectsList.subjectFilter.addElement(new ListFilter.Element(subject, function(visible)
		{
			var subject = this.data;
			subject.setVisible(visible);
		}));
	};

	SubjectsList.subjectFilter.runThread();
	$('#enr-subjectsList-top-bar').find('label').disableDragging();
};


/*******************************************************************************
 * Klasa semestru.
 ******************************************************************************/

/**
 * Konstruktor modelu semestru.
 */
SubjectsList.Semester = function()
{
	this.id = null;
	this.name = null;
	this.type = null;
	this.subjects = new Object();
	this.container = null;
	this.visibleSubjects = 0;
	this.visible = true;
};

/**
 * Dodaje przedmiot do listy przedmiotów w danym semestrze.
 */
SubjectsList.Semester.prototype.addSubject = function(subject)
{
	if (!subject.id)
		throw new Error('Nie ustawiono ID przedmiotu');

	subject.semester = this;
	this.subjects[subject.id] = subject;
	this.visibleSubjects++;
};

/**
 * Odświeża widoczność semestru na podstawie widoczności jego przedmiotów.
 * Semestr jest wyświetlany wtedy i tylko wtedy, gdy zawiera przynajmniej jeden
 * wyświetlany przedmiot.
 */
SubjectsList.Semester.prototype.updateVisibility = function()
{
	if (this.visibleSubjects < 0)
		throw new Error('Nieprawidłowy stan licznika widocznych przedmiotów');
	var visible = (this.visibleSubjects > 0);

	if (visible == this.visible)
		return;
	this.visible = visible;

	this.container.css('display', visible?'':'none');
};

/*******************************************************************************
 * Klasa przedmiotu.
 ******************************************************************************/

/**
 * Konstruktor modelu przedmiotu.
 */
SubjectsList.Subject = function()
{
	this.id = null;
	this.name = null;
	this.semester = null;
	this.container = null;
	this.visible = true;
	this.wasEnrolled = null; // czy aktualny student był zapisany
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
SubjectsList.Subject.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	if (visible)
		this.semester.visibleSubjects++;
	else
		this.semester.visibleSubjects--;
	this.semester.updateVisibility();

	this.container.css('display', visible?'':'none');
};
