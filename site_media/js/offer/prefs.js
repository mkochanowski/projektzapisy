/**
 * Funkcje i klasy odpowiedzialne za preferencje pracowników na temat
 * przedmiotów z oferty dydaktycznej.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

Prefs = Object();

/**
 * Zainicjowanie formularza preferencji.
 */
Prefs.init = function()
{
	var i;

	var prefsList = $('#od-prefs-list');
	Prefs.prefsList = prefsList.getDOM();

	Prefs.courses = new Array();
	var courseElements = prefsList.children('li');
	for (i = 0; i < courseElements.length; i++)
	{
		var sub = Prefs.Course.fromElement(courseElements[i]);
		sub.attachControls();
		sub.setCollapsed(true);
		Prefs.courses.push(sub);
	}

	// panel rozwiń / zwiń wszystko
	var viewmodeSelectionBar = document.createElement('p');
	viewmodeSelectionBar.id = 'od-prefs-viewmode-selection';
	$('#main-content').prepend(viewmodeSelectionBar);

	var uncollapseAll = document.createElement('a');
	uncollapseAll.appendChild(document.createTextNode('Rozwiń wszystko'));
	viewmodeSelectionBar.appendChild(uncollapseAll);
	viewmodeSelectionBar.appendChild(document.createTextNode(' '));

	var collapseAll = document.createElement('a');
	collapseAll.appendChild(document.createTextNode('Zwiń wszystko'));
	viewmodeSelectionBar.appendChild(collapseAll);

	var toggleCollapseAll = function(collapse)
	{
		for (i = 0; i < Prefs.courses.length; i++)
			Prefs.courses[i].setCollapsed(collapse);
	};
	$(collapseAll).click(function()
	{
		toggleCollapseAll(true);
	});
	$(uncollapseAll).click(function()
	{
		toggleCollapseAll(false);
	});

	// nie ustalone preferencje

	var undecidedList = $('#od-prefs-undecided');
	Prefs.undecidedList = undecidedList;

	var undecidedElements = undecidedList.children('li');
	for (i = 0; i < undecidedElements.length; i++)
	{
		var und = Prefs.Undecided.fromElement(undecidedElements[i]);
		und.attachControls();
	}

	Prefs.emptyMessage = $('#od-prefs-emptyMessage');
	if (Prefs.emptyMessage.length)
		Prefs.emptyMessage = Prefs.emptyMessage.getDOM();
	else
		Prefs.emptyMessage = null;

	// reszta ustawień

	$('#od-prefs-top-bar').find('label').disableDragging();

	Prefs.initFilter();
};

$(Prefs.init);


/*******************************************************************************
 * Model przedmiotu bez ustalonych preferencji
 ******************************************************************************/

Prefs.Undecided = function()
{
	this.initURL = null;
	this.container = null;
};

Prefs.Undecided.fromElement = function(element)
{
	var el = $(element);

	var und = new Prefs.Undecided();
	und.initURL = el.children('.initURL').val().trim();
	und.container = el[0];

	return und;
};

Prefs.Undecided.prototype.attachControls = function()
{
	var thisObj = this;

	var initBtn = document.createElement('input');
	initBtn.type = 'button';
	initBtn.value = '<';
	$(initBtn).click(function()
	{
		thisObj.init();
	});

	$(this.container).prepend(initBtn);
};

Prefs.Undecided.prototype.init = function()
{
	$(this.container).remove();
	if (Prefs.undecidedList.children('li').length == 0)
		Sidebar.detach();

	$.ajax({
		type: 'post',
		url: this.initURL,
		success: function(data)
		{
			var i;

			data = $.parseJSON(data);
			if (data.Success != 'OK')
				throw Error('Prefs.Undecided.prototype.init: błąd w komunikacji');

			// workaround dla buga w Chrome i Chromium
			if (jQuery.browser.webkit)
			{
				var prefsForm = $('#od-prefs-form');
				var prefsFormURL = prefsForm[0].action;

				$.ajax({
					type: 'post',
					url: prefsFormURL,
					data: prefsForm.serialize(),
					dataType: 'html',
					success: function()
					{
						document.location.href = prefsFormURL;
					}
				});

				return;
			}

			var sub = new Prefs.Course();
			sub.id = data.id;
			sub.types = data.types;
			sub.name = data.name;
			sub.hideURL = data.hideurl;
			sub.unhideURL = data.unhideurl;
			sub.isNew = !!data.is_new;

			sub.container = document.createElement('li');
			Prefs.prefsList.appendChild(sub.container);
			Prefs.setEmptyFilterWarningVisible(false);

			var name = document.createElement('span');
			name.className = 'name';
			name.appendChild(document.createTextNode(sub.name));
			sub.container.appendChild(name);

			sub.prefContainer = document.createElement('ul');
			sub.container.appendChild(sub.prefContainer);

			var options = new Object();
			for (i = 0; i < data.prefchoices.length; i++)
			{
				var choice = data.prefchoices[i];
				options[choice[0]] = choice[1];
			}

			var appendSelect = function(label, className)
			{
				var li = document.createElement('li');
				li.appendChild(document.createTextNode(label + ' '));

				var select = document.createElement('select');
				select.name = className + '-' + sub.id;
				select.className = className;
				li.appendChild(select);

				for (var v in options)
				{
					var option = document.createElement('option');
					option.value = v;
					if (v == 0)
						option.selected = true;
					option.appendChild(document.createTextNode(options[v]));
					select.appendChild(option);
				}

				sub.prefContainer.appendChild(li);
			};

			if (data.showlectures)
				appendSelect('Wykład:', 'lecture');
			if (data.showrepetitories)
				appendSelect('Repetytorium:', 'review-lecture');
			if (data.showexercises)
				appendSelect('Ćwiczenia:', 'tutorial');
			if (data.showlaboratories)
				appendSelect('Pracownia:', 'lab');

			Prefs.courses.push(sub);
			sub.attachControls();

			if (Prefs.emptyMessage)
			{
				$(Prefs.emptyMessage).remove();
				Prefs.emptyMessage = null;
				$('#od-prefs-form')[0].style.display = 'block';
			}
		}
	});
};


/*******************************************************************************
 * Model preferencji przedmiotu
 ******************************************************************************/

Prefs.Course = function()
{
	this.id = null;
	this.types = new Array();
	this.name = null;
	this.collapsed = false;
	this.hidden = false;
	this.container = null;
	this.prefContainer = null;
	this.hideURL = null;
	this.unhideURL = null;
	this.isNew = false;
};

Prefs.Course.fromElement = function(element)
{
	var el = $(element);

	var sub = new Prefs.Course();
	sub.id = Number(el.children('.pref-id').val());
	sub.types = el.children('.pref-type').val().trim().split(new RegExp(' +'));
	sub.name = el.children('.name').text().trim();
	sub.hideURL = el.children('.pref-hide-url').val().trim();
	sub.unhideURL = el.children('.pref-unhide-url').val().trim();
	sub.collapsed = el.hasClass('collapsed');
	sub.hidden = el.hasClass('hidden');
	sub.isNew = !!el.children('.pref-is-new').assertOne().val().castToInt();

	sub.container = el[0];
	sub.prefContainer = el.children('ul')[0];

	return sub;
};

Prefs.Course.prototype.attachControls = function()
{
	var thisObj = this;
	var label = $(this.container).children('.name');

	var collapseBtn = document.createElement('input');
	collapseBtn.type = 'button';
	collapseBtn.value = (this.collapsed?'+':'-');
	collapseBtn.className = 'od-prefs-toggleCollapse';
	this.collapseBtn = collapseBtn;
	collapseBtn = $(collapseBtn);
	collapseBtn.insertBefore(label);
	collapseBtn.click(function()
	{
		thisObj.setCollapsed(!thisObj.collapsed);
	});

	var hideBtn = document.createElement('input');
	hideBtn.type = 'button';
	hideBtn.value = (this.hidden?'Nie ukrywaj':'Ukryj');
	hideBtn.className = 'od-prefs-toggleHidden';
	this.hideBtn = hideBtn;
	hideBtn = $(hideBtn);
	hideBtn.insertAfter(label);
	hideBtn.click(function()
	{
		var hidden = !thisObj.hidden;

		$.ajax({
			type: 'post',
			url: (hidden?thisObj.hideURL:thisObj.unhideURL),
			success: function()
			{
				thisObj.hidden = hidden;
				if (hidden)
				{
					$(thisObj.container).addClass('hidden');
					thisObj.hideBtn.value = 'Nie ukrywaj';
				}
				else
				{
					$(thisObj.container).removeClass('hidden');
					thisObj.hideBtn.value = 'Ukryj';
				}
				Prefs.courseFilter.doFilter();
			}
		});

	});
};

Prefs.Course.prototype.setCollapsed = function(collapsed)
{
	collapsed = !!collapsed;
	if (collapsed == this.collapsed)
		return;
	this.collapsed = collapsed;

	var cont = $(this.container);
	if (collapsed)
	{
		cont.addClass('collapsed');
		this.collapseBtn.value = '+';
	}
	else
	{
		cont.removeClass('collapsed');
		this.collapseBtn.value = '-';
	}
};


/*******************************************************************************
 * Filtrowanie
 ******************************************************************************/

/**
 * Pokazuje lub ukrywa ostrzeżenie o pustym filtrze.
 */
Prefs.setEmptyFilterWarningVisible = function(visible)
{
	Prefs.emptyFilterWarning.style.display = visible?'block':'none';
	Prefs.prefsList.style.display = visible?'none':'block';
}

/**
 * Inicjuje filtrowanie.
 */
Prefs.initFilter = function()
{
	var courseFilterForm = $('#od-prefs-top-bar').assertOne();

	courseFilterForm.css('display', 'block');

	courseFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		courseFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	Prefs.emptyFilterWarning = document.createElement('p');
	Prefs.emptyFilterWarning.className = 'emptyFilterWarning';
	Prefs.emptyFilterWarning.style.display = 'none';
	$(Prefs.emptyFilterWarning).insertAfter(Prefs.prefsList);
	Prefs.emptyFilterWarning.appendChild(document.createTextNode(
		'Do podanego filtra nie pasuje żaden z przedmiotów.'));

	// konfiguracja filtra

	Prefs.courseFilter = new ListFilter('prefs-courses', courseFilterForm.getDOM());
	Prefs.courseFilter.afterFilter = function(matchedElementsCount)
	{
		Prefs.setEmptyFilterWarningVisible(matchedElementsCount == 0);
	};

	Prefs.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var course = element.data;
		return (course.name.toLowerCase().indexOf(value) >= 0);
	}));

	Prefs.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showHidden', '#od-prefs-hidden', function(element, value)
	{
		if (value)
			return true;
		var course = element.data;
		return !course.hidden;
	}));

	Prefs.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'onlyNew', '#od-prefs-only-new', function(element, value)
	{
		if (!value)
			return true;
		var course = element.data;
		return course.isNew;
	}));

	Prefs.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		var course = element.data;
		return (course.types.indexOf(courseType) >= 0);
	}));

	for (var i = 0; i < Prefs.courses.length; i++)
		Prefs.courseFilter.addElement(new ListFilter.Element(Prefs.courses[i], function(visible)
		{
			var course = this.data;
			$(course.container).css('display', visible?'block':'none')
		}));

	Prefs.courseFilter.runThread();
};
