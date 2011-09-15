/**
 * Kod widoku przedmiotu, tzn konkretnego przedmiotu w danym semestrze, na który
 * się można zapisać (oczywiście pod warunkiem otwartych zapisów).
 */

CourseView = new Object();

/**
 * Inicjuje widok przedmiotu.
 */
CourseView.init = function()
{
	Fereol.Enrollment.Course.fromJSON($('input[name=ajax-course-data]').val());

	CourseView._detailsContainer = $('#enr-course-view .details').assertOne();

	// wysokość panelu szczegółów (w stanie "widoczny")
	CourseView._detailsCurrentHeight = CourseView._detailsContainer.height();

	// czy panel szczegółów jest wyświetlony
	CourseView.detailsVisible = null;

	CourseView.isEnrollmentOpen = ($('.setEnrolledButton').size() > 0);
	CourseView.priorityLimit = $('input[name=priority-limit]').assertOne().
		attr('value').castToInt();

	CourseView._initDetailsToggleSwitch();
	CourseView._initExpandableDescription();
	CourseView._initTermsList();
	CourseView._initTermsTablesStyles();
};

$(CourseView.init);

/**
 * Inicjuje listy terminów.
 */
CourseView._initTermsList = function()
{
	if (!CourseView.isEnrollmentOpen)
		return;
	CourseView._termsList = new Array();
	CourseView._termsMap = new Object();
	$('#enr-course-view > .tutorial tbody tr').each(function(idx, elem)
	{
		var term = Fereol.Enrollment.EPanelCourseTerm.fromHTML($(elem));
		CourseView._termsList.push(term);
		CourseView._termsMap[term.id] = term;
		term.convertControlsToAJAX();
	});
};

/**
 * Inicjuje dynamicznie zmienane style tabel z terminami.
 */
CourseView._initTermsTablesStyles = function()
{
	Sidebar.addObserver({ update: function()
	{
		$('#enr-course-view .termEnrolledHeader').text(
			Sidebar.visible ? 'Zapis.' : 'Zapisanych');
		$('#enr-course-view .termQueuedHeader').text(
			Sidebar.visible ? 'Kolejka' : 'W kolejce');
	}});
};

/**
 * Inicjuje zwijanie długich opisów przedmiotów.
 */
CourseView._initExpandableDescription = function()
{
	var descriptionContainer = CourseView._detailsContainer.children('.description').
		assertOne();
};

/**
 * Inicjuje ukrywanie panelu szczegółów przedmiotu.
 */
CourseView._initDetailsToggleSwitch = function()
{
	// wysokość marginesu będzie potrzebna, bo chcemy zwijać panel razem z nim
	CourseView._detailsContainerMargin =
		CourseView._detailsContainer.css('margin-bottom');

	// ustawienie widoczności panelu na podstawie cookie
	CourseView.detailsVisible = !$.cookies.get('CourseView-details-hidden');
	if (!CourseView.detailsVisible){
		CourseView._detailsContainer.css({
			marginBottom: 0
		});
        $('.course-details').hide('slow');
    } else {
        $('.course-details').show('slow');
    } 
	// wygenerowanie przycisku chowania panelu
	var detailsVisibleToggle = $.create('a', { className: 'details-toggle' }).
		prependTo($('#enr-course-view').assertOne()).text('blabla');

	// aktualizacja napisu na przycisku chowania
	var detailsVisibleToggleUpdateText = function()
	{
		detailsVisibleToggle.text(CourseView.detailsVisible ?
			'ukryj szczegóły' : 'pokaż szczegóły');
	};
	detailsVisibleToggleUpdateText();

	// akcja chowania/pokazywania panelu szczegółów
	detailsVisibleToggle.disableDragging().click(function()
	{
		var visible = CourseView.detailsVisible = !CourseView.detailsVisible;
		$.cookies.set('CourseView-details-hidden', !visible);
		if(visible){
            $('.course-details').show('slow');
        } else {
            $('.course-details').hide('slow');
        }

		detailsVisibleToggleUpdateText();
	});
};
