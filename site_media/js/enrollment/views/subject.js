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
	SubjectView.initDetails();
};

$(SubjectView.init);

/**
 * Inicjuje panel szczegółów (tabelka z właściwościami i opis).
 */
SubjectView.initDetails = function()
{
	var detailsContainer = $('#enr-subject-view .details').assertOne();
	var descriptionContainer = detailsContainer.children('.description').
		assertOne();
	var propertiesContainer = detailsContainer.children('ul').assertOne();

	var prefferedHeight = propertiesContainer.outerHeight();
	var descriptionHeight = descriptionContainer.outerHeight();

	// rozmiary panelu szczegółów przed modyfikacjami
	var originalHeight = detailsContainer.height() + 'px';
	var originalMarginBottom = detailsContainer.css('margin-bottom');

	// aktualne rozmiary panelu w stanie "widoczny"
	var currentHeight = originalHeight;
	var currentMarginBottom = originalMarginBottom;

	if (descriptionHeight > prefferedHeight + 10)
	{
		currentHeight = prefferedHeight + 'px'
		currentMarginBottom = (parseInt(originalMarginBottom) +
			parseInt(propertiesContainer.css('margin-bottom'))) + 'px';

		detailsContainer.css({
			height: currentHeight,
			marginBottom: currentMarginBottom
		});

		var moreDescriptionButton = $.create('a', { className: 'more' }).
			text('pokaż więcej...').appendTo(descriptionContainer);
		moreDescriptionButton.css('top',
			(prefferedHeight - moreDescriptionButton.outerHeight()) + 'px');
		moreDescriptionButton.css('left',
			(descriptionContainer.innerWidth() -
				moreDescriptionButton.outerWidth()) + 'px');

		var moreDescriptionButtonClicked = false;
		moreDescriptionButton.disableDragging().click(function()
		{
			if (moreDescriptionButtonClicked)
				return;
			moreDescriptionButtonClicked = true;

			moreDescriptionButton.remove();
			detailsContainer.stop().animate({
				height: originalHeight,
				marginBottom: originalMarginBottom
			}, 150);

			currentHeight = originalHeight;
			currentMarginBottom = originalMarginBottom;
		});
	}

	// ukrywanie panelu szczegółów

	SubjectView.detailsVisible = !$.cookies.get('SubjectView-details-hidden');
	if (!SubjectView.detailsVisible)
		detailsContainer.css({
			height: 0,
			marginBottom: 0
		});

	var detailsVisibleToggle = $.create('a', { className: 'details-toggle' }).
		prependTo($('#enr-subject-view').assertOne()).text('blabla');

	var detailsVisibleToggleUpdateText = function()
	{
		detailsVisibleToggle.text(SubjectView.detailsVisible ?
			'ukryj szczegóły' : 'pokaż szczegóły');
	};
	detailsVisibleToggleUpdateText();

	detailsVisibleToggle.disableDragging().click(function()
	{
		var visible = SubjectView.detailsVisible = !SubjectView.detailsVisible;
		$.cookies.set('SubjectView-details-hidden', !visible);

		detailsContainer.stop().animate({
			height: visible ? currentHeight : 0,
			marginBottom: visible? currentMarginBottom : 0
		}, 150);

		detailsVisibleToggleUpdateText();
	});
};
