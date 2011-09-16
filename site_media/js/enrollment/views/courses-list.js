/**
 * Kod odpowiedzialny za listę przedmiotów w systemie zapisów.
 */

CoursesList = new Object();

/**
 * Inicjuje widok listy przedmiotów.
 */
CoursesList.init = function()
{
	CoursesList.initCourseLists();
	CoursesList.initFilter();
};

$(CoursesList.init);

/**
 * Inicjuje listy przedmiotów i semestrów (model).
 */
CoursesList.initCourseLists = function()
{
	CoursesList.courses = new Object();
	CoursesList.semesters = new Object();

	$('#course-list').assertOne().children('div.semester').
		each(function(i, semesterContainer)
	{
		semesterContainer = $(semesterContainer);

		var semester = new CoursesList.Semester();
		semester.id = semesterContainer.children('input[name=semester-id]').
			assertOne().attr('value').castToInt();
		semester.name = semesterContainer.children('h2').assertOne().
			children('span').assertOne().text();
		semester.container = semesterContainer;
		CoursesList.semesters[semester.id] = semester;

		semesterContainer.children('ul').assertOne().children('li').
			each(function(i, courseContainer)
		{
			courseContainer = $(courseContainer);
			var link = courseContainer.children('a').assertOne();

			var course = new CoursesList.Course();
			course.id = link.attr('id').removePrefix('course-').castToInt();
			course.name = link.text().trim();
			course.type = courseContainer.children('input[name=type]').
				assertOne().attr('value').castToInt();
			course.container = courseContainer;
			course.wasEnrolled = courseContainer.children('input[name=wasEnrolled]').
				assertOne().attr('value').castToBool();
			course.english = courseContainer.children('input[name=english]').
				assertOne().attr('value').castToBool();
			course.exam = courseContainer.children('input[name=exam]').
				assertOne().attr('value').castToBool();
			course.suggested_for_first_year = courseContainer.children('input[name=suggested_for_first_year]').
				assertOne().attr('value').castToBool();
			semester.addCourse(course);
			CoursesList.courses[course.id] = course;
		});
	});
};

/**
 * Inicjuje filtrowanie.
 */
CoursesList.initFilter = function()
{
	var courseFilterForm = $('#enr-coursesList-top-bar').assertOne();

	courseFilterForm.css('display', 'block');

	courseFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		courseFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	CoursesList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden przedmiot.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#course-list').assertOne());
	CoursesList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	CoursesList.courseFilter = new ListFilter('coursesList-courses', courseFilterForm.getDOM());
	
	CoursesList.courseFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (CoursesList.emptyFilterWarningVisible == visible)
			return;
		CoursesList.emptyFilterWarningVisible = visible;
		CoursesList.emptyFilterWarning.css('display', visible?'':'none');
	};

	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var course = element.data;
		if (!course.name)
			$.log(course);
		return (course.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'semester', '#enr-courseFilter-semester', function(element, option)
	{
		if (!option || option == 0)
			return true;
		var course = element.data;
		return (course.semester.id == option);
	}));

	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		if (!value)
			return true;
		var course = element.data;
		return !course.wasEnrolled;
	}));
	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showEnglish', '#enr-courseFilter-english', function(element, value)
	{
		if(value)
			return true;
		var course = element.data;
		return !course.english;
	}));
	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showExam', '#enr-courseFilter-exam', function(element, value)
	{
		if(value)
			return true;
		var course = element.data;
		return !course.exam;
	}));
	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showSyggestedForFirstYear', '#enr-courseFilter-suggestedForFirstYear', function(element, value)
	{
		if(!value)
			return true;
		var course = element.data;
		return course.suggested_for_first_year;
	}));

	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		var course = element.data;
		return (course.type == courseType);
	}));

	for (var course in CoursesList.courses)
	{
		course = CoursesList.courses[course];
		CoursesList.courseFilter.addElement(new ListFilter.Element(course, function(visible)
		{
			var course = this.data;
			course.setVisible(visible);
		}));
	};

	CoursesList.courseFilter.runThread();
	$('#enr-coursesList-top-bar').find('label').disableDragging();
};


/*******************************************************************************
 * Klasa semestru.
 ******************************************************************************/

/**
 * Konstruktor modelu semestru.
 */
CoursesList.Semester = function()
{
	this.id = null;
	this.name = null;
	this.type = null;
	this.courses = new Object();
	this.container = null;
	this.visibleCourses = 0;
	this.visible = true;
};

/**
 * Dodaje przedmiot do listy przedmiotów w danym semestrze.
 */
CoursesList.Semester.prototype.addCourse = function(course)
{
	if (!course.id)
		throw new Error('Nie ustawiono ID przedmiotu');

	course.semester = this;
	this.courses[course.id] = course;
	this.visibleCourses++;
};

/**
 * Odświeża widoczność semestru na podstawie widoczności jego przedmiotów.
 * Semestr jest wyświetlany wtedy i tylko wtedy, gdy zawiera przynajmniej jeden
 * wyświetlany przedmiot.
 */
CoursesList.Semester.prototype.updateVisibility = function()
{
	if (this.visibleCourses < 0)
		throw new Error('Nieprawidłowy stan licznika widocznych przedmiotów');
	var visible = (this.visibleCourses > 0);

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
CoursesList.Course = function()
{
	this.id = null;
	this.name = null;
	this.semester = null;
	this.container = null;
	this.visible = true;
	this.type = null;
	this.wasEnrolled = null; // czy aktualny student był zapisany
	this.english = null;
	this.exam = null;
	this.suggested_for_first_year = null;
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
CoursesList.Course.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	if (visible)
		this.semester.visibleCourses++;
	else
		this.semester.visibleCourses--;
	this.semester.updateVisibility();

	this.container.css('display', visible?'':'none');
};
