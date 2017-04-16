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
    
    $("#enr-courseFilter-semester").change(CoursesList.onNewSemesterChosen);
    
    // TODO: turn this on when we migrate to jquery > 1.6
   // $("#enr-courseFilter-effects").mousedown(CoursesList.onMultiselectClicked);
   // $("#enr-courseFilter-tags").mousedown(CoursesList.onMultiselectClicked);
};

$(CoursesList.init);


CoursesList.onMultiselectClicked = function(e)
{
    e.preventDefault();
    $(this).attr("selected", !$(this).attr("selected"));
    return false;
};

CoursesList.setDownloadingDataUi = function()
{
    $("#mainCoursesContainer").addClass("hidden");
    $("#fetchingListMessage").removeClass("hidden");
};

CoursesList.setCoursesViewUi = function()
{
    $("#mainCoursesContainer").removeClass("hidden");
    $("#fetchingListMessage").addClass("hidden");
};

CoursesList.onNewSemesterChosen = function()
{
    var newId = parseInt($("#enr-courseFilter-semester").find(":selected").val());
    CoursesList.userChosenSemester = newId;
    
    CoursesList.setDownloadingDataUi();
    
    $.get(
        "/courses/get_semester_info/" + newId,
        CoursesList.onSemesterInfoReceived)
        .fail(CoursesList.onSemesterInfoReceiveFailed);
};

CoursesList.onSemesterInfoReceiveFailed = function()
{
    CoursesList.setCoursesViewUi();
    
    $("#enr-courseFilter-semester").val(CoursesList.currentSemester.id);
    CoursesList.userChosenSemester = CoursesList.currentSemester.id;
    
    alert("Nie udało się pobrać listy przedmiotów dla tego semestru.");
};

CoursesList.onSemesterInfoReceived = function(data, status)
{
    CoursesList.courses = data.courseList;
    CoursesList.currentSemester = data.semesterInfo;
    
    CoursesList.updateUiFromData();
    CoursesList.setCoursesViewUi();
}

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
    CoursesList.userChosenSemester = coursesListObject.semesterInfo.id;
    
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
    
    CoursesList.initFilter();
};

CoursesList.setCourseVisible = function(course, visible)
{
    course.visible = visible;
    if (visible)
        course.htmlNode.removeClass("hidden");
    else
        course.htmlNode.addClass("hidden");
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
	CoursesList.emptyFilterWarning = $("#noResultsMessage");
	CoursesList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	CoursesList.courseFilter = new ListFilter('coursesList-courses', courseFilterForm.getDOM());
	
	CoursesList.courseFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (CoursesList.emptyFilterWarningVisible == visible)
			return;
		CoursesList.emptyFilterWarningVisible = visible;
        
        if (visible)
            CoursesList.emptyFilterWarning.removeClass("hidden");
        else
            CoursesList.emptyFilterWarning.addClass("hidden");
	};

	CoursesList.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var course = element.data;
		return (course.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
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
