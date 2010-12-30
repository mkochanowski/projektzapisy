/**
 * Rozszerzenie klasy ListFilter o możliwość filtrowania po typach przedmiotów.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

/**
 * Tworzy filtr typów przedmiotów. Filtr ma przypisaną nazwę "subjectType"
 * i element ".subject-type-filter".
 *
 * Po przypisaniu do formularza przekształca element (zawierający odpowiednie
 * kontrolki typów przedmiotów), grupując typy przedmiotów.
 *
 * @param matchCallback funkcja typu function(subject, subjectType)
 *        stwierdzająca, czy przedmiot "subject" jest typu subjectType
 */
ListFilter.CustomFilters.createSubjectTypeFilter = function(matchCallback)
{
	var filter = new ListFilter.Filter('subjectType', '.subject-type-filter');
	filter.enabledTypes = new Object();
    filter.metaMode = true;
	filter.filterFormModel = null;

	var typeListIsEqual = function(typeList1, typeList2)
	{
		var type;
		for (type in typeList1)
			if (!typeList2[type])
				return false;
		for (type in typeList2)
			if (!typeList1[type])
				return false;
		return true;
	};

	filter.onAssign = function()
	{
		this.filterFormModel = new SubjectTypeFilterForm(this.formElement.getDOM());
	};

	filter.serialize = function()
	{
		var enabledTypes = new Array();
		for (var type in this.enabledTypes)
			enabledTypes.push(type);
		return {
			metaMode: this.metaMode,
			enabledTypes: enabledTypes
		};
	};

	filter.deserialize = function(serialized)
	{
		/* jeżeli w zserializowanej wersji nie ma danych, to wczytujemy
		 * z formularza. TODO: przydało by się odczytywanie z formularza
		 * wszystkich typów (nie tylko zaznaczonych) i ustawienie ich
		 * (wszystkich) jako wybrane (czyli domyślnie wszystko pokazujemy)
		 */
		if (!serialized)
			return this.loadFromForm();

		var thisObj = this;

		var oldMetaMode = this.metaMode;
		this.metaMode = !!serialized.metaMode;
		
		var oldEnabledTypes = this.enabledTypes;
		this.enabledTypes = new Object();

		serialized.enabledTypes.forEach(function(type)
		{
			thisObj.enabledTypes[type] = true;
		});

		if (oldMetaMode != this.metaMode)
			return true;
		return !typeListIsEqual(oldEnabledTypes, this.enabledTypes);
	};

	filter.saveToForm = function()
	{
		this.filterFormModel.saveFilter(this);
	};

	filter.loadFromForm = function()
	{
		var oldMetaMode = this.metaMode;
		var oldEnabledTypes = this.enabledTypes;

		this.filterFormModel.readFilter(this);

		if (oldMetaMode != this.metaMode)
			return true;
		return !typeListIsEqual(oldEnabledTypes, this.enabledTypes);
	};

	filter.match = function(element)
	{
		for (var type in filter.enabledTypes)
			if (matchCallback(element, type))
				return true;
		return false;
	};

	return filter;
};


/*******************************************************************************
 * Model formularza filtrującego typy przedmiotów.
 ******************************************************************************/

/**
 * Konstruktor modelu formularza z filtrem po typach przedmiotów.
 *
 * @param container kontener, w którym jest formularz
 */
function SubjectTypeFilterForm(container)
{
    if (!container)
        throw new Error('Kontener nie istnieje');
    var thisObj = this;
    var i;

    this.container = container;
    this.subjectTypes = {};

    // generowanie nowej grupy - inne
    var otherSpanBox = document.createElement('span');
    otherSpanBox.className = 'checkbox';
    var otherCheck = document.createElement('input');
    otherCheck.type = 'checkbox';
	this.container.appendChild(otherSpanBox);
	otherSpanBox.appendChild(otherCheck);
    otherCheck.value = '0';
    otherCheck.id = 'filter-subject-type-0';
    otherCheck.className = 'filter-subject-type-meta';
    var otherGroup = document.createElement('input');
    otherGroup.type = 'hidden';
    otherGroup.className = 'group-id';
	otherSpanBox.appendChild(otherGroup);
    var otherLabel = document.createElement('label');
    otherSpanBox.appendChild(document.createTextNode(' '));
    otherSpanBox.appendChild(otherLabel);
    otherLabel.htmlFor = 'filter-subject-type-0';
    otherLabel.appendChild(document.createTextNode('Inne'));

    // akcja kliknięcia checkboxa meta-typu
    var metaClick = function(metaType)
    {
        $(metaType.checkbox).removeClass('partialCheck');
        var id = metaType.id;
        var check = metaType.checkbox.checked;
        for (i in thisObj.subjectTypes)
        {
            var subject = thisObj.subjectTypes[i];
            if (subject.isMeta)
                continue;
            if (subject.getParent().id == id)
                subject.checkbox.checked = check;
        }
    };

    // odczytywanie grup do obiektów
    var subjectTypes = $(this.container).find('span.checkbox');
    for (i = 0; i < subjectTypes.length; i++)
    {
        var type = new SubjectTypeFilterForm.Type(subjectTypes[i]);
        this.subjectTypes[type.id] = type;
    }
    var otherType = this.subjectTypes[0];
    if (!otherType)
        throw new Error('Nie wygenerowano grupy "Inne"');
    for (i in this.subjectTypes)
    {
        var subject = this.subjectTypes[i];
        if (subject.parent == null)
        {
            if (subject.isMeta)
            {
                (function(sub) {
                    $(sub.checkbox).click(function()
                    {
                        metaClick(sub);
                    });
                })(subject);
            }
            else
                subject.parent = otherType;
        }
        else
        {
            if (subject.isMeta)
                throw new Error('Nie obsługujemy modelu wielopoziomowego');
            if (!this.subjectTypes[subject.parent])
                throw new Error('Rodzic nie istnieje');
            subject.parent = this.subjectTypes[subject.parent];
        }
    }

    // dodanie przycisku metaSwitch
    this.metaSwitch = document.createElement('a');
    this.metaSwitch.className = 'filter-subject-type-metaSwitch';
    this.metaSwitch.appendChild(document.createTextNode('więcej'));
    this.container.appendChild(this.metaSwitch);
    $(this.metaSwitch).click(function()
    {
        thisObj.setMetaMode(!thisObj.metaMode);
    });

    this.setMetaMode(true);
}

/**
 * Ustawia, lub usuwa tryb meta-typów. Jeżeli jest włączony, to zamiast
 * normalnych typów przedmiotów w filtrze są wyświetlane ich grupy. Zaznaczanie
 * grupy skutkuje zaznaczeniem wszystkich jej elementów.
 *
 * @param enabled czy włączyć tryb meta-typów
 */
SubjectTypeFilterForm.prototype.setMetaMode = function(enabled)
{
    var i;

    enabled = !!enabled;

    this.metaMode = enabled;
    $(this.metaSwitch).text(enabled?'więcej':'mniej');

    for (i in this.subjectTypes)
    {
        var type = this.subjectTypes[i];
        type.container.style.display = (this.metaMode == type.isMeta)?'':'none';
    }

    if (this.metaMode)
    {
        // najpierw zaznaczamy wszystkie meta typy
        for (i in this.subjectTypes)
        {
            var metaSubject = this.subjectTypes[i];
            if (metaSubject.isMeta)
            {
                metaSubject.checkbox.checked = true;
                $(metaSubject.checkbox).removeClass('partialCheck');
            }
        }

        // teraz odznaczamy wszystkie, w których grupie choć jeden nie jest
        // zaznaczony
        var nonmetaSubject;
        for (i in this.subjectTypes)
        {
            nonmetaSubject = this.subjectTypes[i];
            if (nonmetaSubject.isMeta)
                continue;
            if (!nonmetaSubject.checkbox.checked)
                nonmetaSubject.getParent().checkbox.checked = false;
        }

        // a teraz "lekko" zaznaczamy te, w których grupie choć jeden jest
        // zaznaczony, a były odznaczone (czyli także jakiś jeden nie jest
        // zaznaczony)
        for (i in this.subjectTypes)
        {
            nonmetaSubject = this.subjectTypes[i];
            if (nonmetaSubject.isMeta)
                continue;
            if (nonmetaSubject.checkbox.checked)
            {
                var parentCheckbox = nonmetaSubject.getParent().checkbox;
                if (!parentCheckbox.checked)
                {
                    parentCheckbox.checked = true;
                    $(parentCheckbox).addClass('partialCheck');
                }
            }
        }
    }
};

/**
 * Odczytuje filtr z formularza.
 *
 * @param filter filtr (wygenerowany przez ListFilter.CustomFilters.
 *        createSubjectTypeFilter()), który ma być ustawiony według danych
 *        z formularza
 */
SubjectTypeFilterForm.prototype.readFilter = function(filter)
{
	filter.metaMode = this.metaMode;
    filter.enabledTypes = new Object();

    var subjectTypes = $(this.container).find('input[type=checkbox]');
    for (var i = 0; i < subjectTypes.length; i++)
    {
        if ($(subjectTypes[i]).hasClass('filter-subject-type-meta'))
            continue;

        var subKey = subjectTypes[i].id;
        if (subKey.substr(0, 20) != 'filter-subject-type-')
            throw new Error('Nieprawidłowy id pola');
        subKey = subKey.substr(20);
        if (subjectTypes[i].checked)
			filter.enabledTypes[subKey] = true;
    }
};

/**
 * Ustawia formularz zgodnie z podanym filtrem.
 *
 * @param filter filter filtr (wygenerowany przez ListFilter.CustomFilters.
 *        createSubjectTypeFilter()), według którego ma zostać ustawiony
 *        formularz
 */
SubjectTypeFilterForm.prototype.saveFilter = function(filter)
{
    var subjectTypes = $(this.container).find('input[type=checkbox]');
    for (var i = 0; i < subjectTypes.length; i++)
    {
        var subKey = subjectTypes[i].id;
        if (subKey.substr(0, 20) != 'filter-subject-type-')
            throw new Error('SubjectTypeFilter.readFilterFromForm: Nieprawidłowy id pola');
        subKey = subKey.substr(20);
        subjectTypes[i].checked = !!filter.enabledTypes[subKey];
    }

    this.setMetaMode(filter.metaMode);
};

/**
 * Klasa pomocnicza pojedyńczego typu przedmiotu.
 *
 * @param container kontener, z którego jest inicjowany typ
 */
SubjectTypeFilterForm.Type = function(container)
{
    var jqContainer = $(container);
    var jqCheckbox = jqContainer.children('input[type=checkbox]');

    this.container = container;
    this.isMeta = jqCheckbox.hasClass('filter-subject-type-meta')
    this.checkbox = jqCheckbox[0];
    this.id = parseInt(this.checkbox.value);
	this.name = jqContainer.children('label').text().trim();

    var groupID = jqContainer.children('input.group-id')[0].value.trim();
    if (groupID == '')
        this.parent = null;
    else
    {
        groupID = parseInt(groupID);
        if (isNaN(groupID))
            throw new Error('SubjectTypeFilterForm.Type: Zły ID grupy');
        this.parent = groupID;
    }
};

/**
 * Zwraca rodzica (meta-typ) typu przedmiotu. Jeżeli typ jest już rodzicem,
 * wyrzuca wyjątek.
 *
 * @return SubjectTypeFilterForm.Type grupa, do której należy ten typ przedmiotów
 */
SubjectTypeFilterForm.Type.prototype.getParent = function()
{
    if (this.isMeta)
        throw new Error('Węzeł jest rodzicem');
    if (this.parent == null)
        throw new Error('Pusty rodzic (powinien być inne)');
    if (typeof this.parent != 'object')
        throw new Error('Nie załadowano rodziców');
    return this.parent;
};
