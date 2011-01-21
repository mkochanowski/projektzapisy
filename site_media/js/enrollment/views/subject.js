/**
 * Kod widoku przedmiotu, tzn konkretnego przedmiotu w danym semestrze, na który
 * się można zapisać (oczywiście pod warunkiem otwartych zapisów).
 */

SubjectView = new Object();

/**
 * Inicjuje widok przedmiotu.
 */
SubjectView.init = function()
{
	SubjectView._detailsContainer = $('#enr-subject-view .details').assertOne();

	// wysokość panelu szczegółów (w stanie "widoczny")
	SubjectView._detailsCurrentHeight = SubjectView._detailsContainer.height();

	// czy panel szczegółów jest wyświetlony
	SubjectView.detailsVisible = null;

	SubjectView._initDetailsToggleSwitch();
	SubjectView._initExpandableDescription();
};

$(SubjectView.init);

/**
 * Inicjuje zwijanie długich opisów przedmiotów.
 */
SubjectView._initExpandableDescription = function()
{
	var descriptionContainer = SubjectView._detailsContainer.children('.description').
		assertOne();
	var propertiesContainer = SubjectView._detailsContainer.children('ul').assertOne();

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
	SubjectView._descriptionExpanded = false;

	// akcja rozwijania opisu
	moreDescriptionButton.disableDragging().click(function()
	{
		if (SubjectView._descriptionExpanded)
			return;
		SubjectView._descriptionExpanded = true;

		moreDescriptionButton.remove();
		SubjectView._detailsContainer.stop().animate({
			height: fullHeight + 'px'
		}, 150);

		SubjectView._detailsCurrentHeight = fullHeight;
	});

	// zwijanie/rozwijanie opisu, w zależności od potrzeby (rozmiaru opisu
	// i dostępnego miejsca)
	var initMoreDescriptionSwitch = function()
	{
		descriptionHeight = descriptionContainer.outerHeight();
		fullHeight = Math.max(descriptionHeight, propertiesHeight);

		if (descriptionHeight > propertiesHeight + 15 &&
			!SubjectView._descriptionExpanded)
		{
			SubjectView._detailsCurrentHeight = propertiesHeight;
			
			moreDescriptionButton.css({
				display: 'block',
				left: (descriptionContainer.innerWidth() -
					moreDescriptionButton.outerWidth()) + 'px'
			});
		}
		else
		{
			SubjectView._detailsCurrentHeight = fullHeight;
			
			moreDescriptionButton.css('display', 'none');
		}
		if (SubjectView.detailsVisible)
			SubjectView._detailsContainer.css('height', SubjectView._detailsCurrentHeight + 'px');
	};
	initMoreDescriptionSwitch();
	var moreDescriptionObserver = { update: initMoreDescriptionSwitch };
	Sidebar.addObserver(moreDescriptionObserver);
};

/**
 * Inicjuje ukrywanie panelu szczegółów przedmiotu.
 */
SubjectView._initDetailsToggleSwitch = function()
{
	// wysokość marginesu będzie potrzebna, bo chcemy zwijać panel razem z nim
	SubjectView._detailsContainerMargin =
		SubjectView._detailsContainer.css('margin-bottom');

	// ustawienie widoczności panelu na podstawie cookie
	SubjectView.detailsVisible = !$.cookies.get('SubjectView-details-hidden');
	if (!SubjectView.detailsVisible)
		SubjectView._detailsContainer.css({
			height: 0,
			marginBottom: 0
		});

	// wygenerowanie przycisku chowania panelu
	var detailsVisibleToggle = $.create('a', { className: 'details-toggle' }).
		prependTo($('#enr-subject-view').assertOne()).text('blabla');

	// aktualizacja napisu na przycisku chowania
	var detailsVisibleToggleUpdateText = function()
	{
		detailsVisibleToggle.text(SubjectView.detailsVisible ?
			'ukryj szczegóły' : 'pokaż szczegóły');
	};
	detailsVisibleToggleUpdateText();

	// akcja chowania/pokazywania panelu szczegółów
	detailsVisibleToggle.disableDragging().click(function()
	{
		var visible = SubjectView.detailsVisible = !SubjectView.detailsVisible;
		$.cookies.set('SubjectView-details-hidden', !visible);

		SubjectView._detailsContainer.stop().animate({
			height: visible ? SubjectView._detailsCurrentHeight : 0,
			marginBottom: visible ? SubjectView._detailsContainerMargin : 0
		}, 150);

		detailsVisibleToggleUpdateText();
	});
};
