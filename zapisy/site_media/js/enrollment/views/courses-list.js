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
    CoursesList.currentSemester = new Object();
    
    var jsonString = $("#courses_list_json").assertOne().val();
    var coursesListObject = JSON.parse(jsonString);
    
    CoursesList.courses = coursesListObject.courseList;
    CoursesList.currentSemester = coursesListObject.semesterInfo;
    
    CoursesList.updateUiFromData();
};

CoursesList.updateUiFromData = function()
{
    $("#current_semester_year").text(CoursesList.currentSemester.year);
    $("#current_semester_type").text(CoursesList.currentSemester.type);
    
    $("#courses-list").empty();
    CoursesList.courses.forEach(function(course)
    {
        var courseLink = $("<a/>", {
                "href" : course.url,
                "text" : course.name
            });
        course["htmlNode"] = $("<li/>");
        courseLink.appendTo(course["htmlNode"]);
        course["htmlNode"].appendTo($("#courses-list"));
    });
};

CoursesList.setCourseVisible = function(course, visible)
{
    course.visible = visible;
    course.htmlNode.css("display", visible ? "" : "none");
}

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
    
    CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'effects', '#enr-courseFilter-effects', function(element, option)
	{
        if (!option || !$("#effectsSearchEnabled").is(':checked'))
        {
            return true;
        }
        
        var course = element.data;
        var courseEffectsArray =  [].concat(course.effects);
        var selectedEffectsArray = [].concat(option).map(function(num) { return parseInt(num); });
        
        // if no filters in place, match all courses
        // (this happens if the checkbox is checked but the user hasn't selected
        // anything yet)
        if (!selectedEffectsArray.length)
        {
            return true;
        }
        
        // TODO: which should it be? true or false?
        if (!courseEffectsArray.length)
        {
            //return true;
            return false;
        }
        
        return findOne(courseEffectsArray, selectedEffectsArray);
	}));
    
    CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'tags', '#enr-courseFilter-tags', function(element, option)
	{
        if (!option || !$("#tagsSearchEnabled").is(':checked'))
        {
            return true;
        }
        
        var course = element.data;
        var courseTagsArray = [].concat(course.tags);
        var selectedTagsArray = [].concat(option).map(function(num) { return parseInt(num); });
        
        if (!selectedTagsArray.length)
        {
            return true;
        }
        
        // see above
        if (!courseTagsArray.length)
        {
            //return true;
            return false;
        }
        
        return findOne(courseTagsArray, selectedTagsArray);
	}));

	CoursesList.courses.forEach(function(course)
	{
		CoursesList.courseFilter.addElement(new ListFilter.Element(course, function(visible)
		{
			var courseToSet = this.data;
			CoursesList.setCourseVisible(courseToSet, visible);
		}));
	});

	CoursesList.courseFilter.runThread();
	$('#enr-coursesList-top-bar').find('label').disableDragging();
};
