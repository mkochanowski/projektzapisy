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
	CourseView._detailsContainer = $('#enr-course-view .details').assertOne();

	// wysokość panelu szczegółów (w stanie "widoczny")
	CourseView._detailsCurrentHeight = CourseView._detailsContainer.height();

	// czy panel szczegółów jest wyświetlony
	CourseView.detailsVisible = null;

	CourseView.isEnrollmentOpen = ($('.setEnrolledButton').size() > 0);

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
		var term = Fereol.Enrollment.CourseTerm.fromHTML($(elem));
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
	var propertiesContainer = CourseView._detailsContainer.children('ul').assertOne();

	var propertiesHeight = propertiesContainer.outerHeight();
	var descriptionHeight = descriptionContainer.outerHeight();

	// rozmiary panelu szczegółów w stanie "rozwinięty opis"
	var fullHeight = Math.max(descriptionHeight, propertiesHeight);

	// generowanie przycisku "pokaż więcej..." dla opisu
	var moreDescriptionButton = $.create('a', { className: 'more' }).
		text('pokaż więcej...').appendTo(descriptionContainer);
	moreDescriptionButton.css('top',
		(propertiesHeight - moreDescriptionButton.outerHeight()) + 'px');

	// czy opis został już rozwinięty
	CourseView._descriptionExpanded = false;

	// akcja rozwijania opisu
	moreDescriptionButton.disableDragging().click(function()
	{
		if (CourseView._descriptionExpanded)
			return;
		CourseView._descriptionExpanded = true;

		moreDescriptionButton.remove();
		CourseView._detailsContainer.stop().animate({
			height: fullHeight + 'px'
		}, 150);

		CourseView._detailsCurrentHeight = fullHeight;
	});

	// zwijanie/rozwijanie opisu, w zależności od potrzeby (rozmiaru opisu
	// i dostępnego miejsca)
	var initMoreDescriptionSwitch = function()
	{
		descriptionHeight = descriptionContainer.outerHeight();
		fullHeight = Math.max(descriptionHeight, propertiesHeight);

		if (descriptionHeight > propertiesHeight + 15 &&
			!CourseView._descriptionExpanded)
		{
			CourseView._detailsCurrentHeight = propertiesHeight;
			
			moreDescriptionButton.css({
				display: 'block',
				left: (descriptionContainer.innerWidth() -
					moreDescriptionButton.outerWidth()) + 'px'
			});
		}
		else
		{
			CourseView._detailsCurrentHeight = fullHeight;
			
			moreDescriptionButton.css('display', 'none');
		}
		if (CourseView.detailsVisible)
			CourseView._detailsContainer.css('height', CourseView._detailsCurrentHeight + 'px');
	};
	initMoreDescriptionSwitch();
	var moreDescriptionObserver = { update: initMoreDescriptionSwitch };
	Sidebar.addObserver(moreDescriptionObserver);
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
	if (!CourseView.detailsVisible)
		CourseView._detailsContainer.css({
			height: 0,
			marginBottom: 0
		});

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

		CourseView._detailsContainer.stop().animate({
			height: visible ? CourseView._detailsCurrentHeight : 0,
			marginBottom: visible ? CourseView._detailsContainerMargin : 0
		}, 150);

		detailsVisibleToggleUpdateText();
	});
};
