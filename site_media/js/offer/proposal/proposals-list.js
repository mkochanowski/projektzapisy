/**
 * Kod odpowiedzialny za listę przedmiotów w systemie zapisów.
 */

ProposalsList = new Object();

/**
 * Inicjuje widok listy proposzycji.
 */
ProposalsList.init = function()
{
	ProposalsList.initProposalLists();
	ProposalsList.initFilter();
};

$(ProposalsList.init);

/**
 * Inicjuje listy przedmiotów
 */
ProposalsList.initProposalLists = function()
{
	ProposalsList.proposals = new Object();

	$('#proposal-list').assertOne().children('ul').assertOne().children('li').
			each(function(i, proposalContainer)
		{
			proposalContainer = $(proposalContainer);
			var link = proposalContainer.children('a').assertOne();

			var proposal = new ProposalsList.Proposal();
			proposal.id = link.attr('id').removePrefix('proposal-').castToInt();
			proposal.name = link.text().trim();
			proposal.container = proposalContainer;
            proposal.student = proposalContainer.children('input[name=student]').
                assertOne().attr('value').castToBool()
			ProposalsList.proposals[proposal.id] = proposal;
		});
};

/**
 * Inicjuje filtrowanie.
 */
ProposalsList.initFilter = function()
{
	var proposalFilterForm = $('#enr-proposalsList-top-bar').assertOne();

	proposalFilterForm.css('display', 'block');

	proposalFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		proposalFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	ProposalsList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żadna propozycja.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#proposal-list').assertOne());
	ProposalsList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	ProposalsList.proposalFilter = new ListFilter('proposalsList-proposals', proposalFilterForm.getDOM());
	
	ProposalsList.proposalFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (ProposalsList.emptyFilterWarningVisible == visible)
			return;
		ProposalsList.emptyFilterWarningVisible = visible;
		ProposalsList.emptyFilterWarning.css('display', visible?'':'none');
	};

	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var proposal = element.data;
		if (!proposal.name)
			$.log(proposal);
		return (proposal.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'studentProp', '#students_proposals', function(element, value)
	{
		if (value)
			return true;
		var proposal = element.data;
		return proposal.student == false;
	}));



	for (var proposal in ProposalsList.proposals)
	{
		proposal = ProposalsList.proposals[proposal];
		ProposalsList.proposalFilter.addElement(new ListFilter.Element(proposal, function(visible)
		{
			var proposal = this.data;
			proposal.setVisible(visible);
		}));
	};

	ProposalsList.proposalFilter.runThread();
	$('#enr-proposalsList-top-bar').find('label').disableDragging();
};



/*******************************************************************************
 * Klasa przedmiotu.
 ******************************************************************************/

/**
 * Konstruktor modelu przedmiotu.
 */
ProposalsList.Proposal = function()
{
	this.id = null;
	this.name = null;
	this.container = null;
	this.visible = true;
    this.student = false;
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
ProposalsList.Proposal.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	this.container.css('display', visible?'':'none');
};
