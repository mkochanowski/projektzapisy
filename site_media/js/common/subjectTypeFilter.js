/**
 * Model filtra po typach przedmiotów.
 */

function SubjectTypeFilter()
{
    this.enabledTypes = new Object();
    this.metaMode = true;
};

/// GETTERY I SETTERY //////////////////////////////////////////////////////////

/**
 * Dodaje typ przedmiotu do listy filtra.
 *
 * @param type identyfikator typu przedmiotu
 */
SubjectTypeFilter.prototype.enableType = function(type)
{
    this.enabledTypes[$.trim(type)] = true;
};

/**
 * Usuwa typ przedmiotu z listy filtra.
 *
 * @param type identyfikator typu przedmiotu
 */
SubjectTypeFilter.prototype.disableType = function(type)
{
    delete this.enabledTypes[$.trim(type)];
};

/**
 * Sprawdza, czy dany typ przedmiotu jest wybrany.
 *
 * @param type identyfikator typu przedmiotu
 * @return podany typ przedmiotu jest wybrany
 */
SubjectTypeFilter.prototype.isEnabled = function(type)
{
    return !!this.enabledTypes[$.trim(type + '')];
}

/**
 * Sprawdza, czy którykolwiek z podanych typów przedmiotów jest wybrany.
 *
 * @param types tablica identyfikatorów typów przedmiotów
 * @return jeden z podanych typów przedmiotów jest wybrany
 */
SubjectTypeFilter.prototype.isAnyEnabled = function(types)
{
    for (var i = 0; i < types.length; i++)
        if (this.isEnabled(types[i]))
            return true;
    return false;
}

SubjectTypeFilter.prototype.setMetaMode = function(enabled)
{
    this.metaMode = !!enabled;
};

/// GETTERY I SETTERY - koniec /////////////////////////////////////////////////

/// SERIALIZACJA ///////////////////////////////////////////////////////////////

/**
 * Deserializacja filtra, np. z cookie.
 *
 * @param serializedFilter filtr w postaci surowej
 * @return SubjectTypeFilter obiekt filtra
 */
SubjectTypeFilter.deserialize = function(serializedFilter)
{
    if (!serializedFilter)
        return null;

    var deserializedFilter = new SubjectTypeFilter();
    deserializedFilter.setMetaMode(serializedFilter.metaMode);

    for (var subjectType in serializedFilter.enabledTypes)
        if (serializedFilter.enabledTypes[subjectType])
            deserializedFilter.enableType(subjectType);

    return deserializedFilter;
};

/// SERIALIZACJA - koniec //////////////////////////////////////////////////////

/**
 * Porównuje filtr z innym.
 *
 * @param filter filtr do porównania
 * @return boolean filtry są równe
 */
SubjectTypeFilter.prototype.isEqual = function(filter)
{
    if (filter.metaMode != this.metaMode)
        return false;
    for (var subjectType1 in this.enabledTypes)
        if (!filter.enabledTypes[subjectType1])
            return false;
    for (var subjectType2 in filter.enabledTypes)
        if (!this.enabledTypes[subjectType2])
            return false;
    return true;
};

/**
 * Sprawdza, czy element ma klasę (css) któregoś ze znajdujących się w filtrze
 * typów przedmiotu.
 */
SubjectTypeFilter.prototype.haveEnabledTypeClass = function(element)
{
    for (var visibleType in this.enabledTypes)
        if ($(element).hasClass('subject-type-' + visibleType))
            return true;
    return false;
};



/******************************************************************************/



/**
 * Model formularza z filtrem po typach przedmiotów
 */

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
    this.container.appendChild(otherSpanBox);
    otherSpanBox.className = 'checkbox';
    var otherCheck = document.createElement('input');
    otherSpanBox.appendChild(otherCheck);
    otherCheck.type = 'checkbox';
    otherCheck.value = '0';
    otherCheck.id = 'filter-subject-type-0';
    otherCheck.className = 'filter-subject-type-meta';
    var otherGroup = document.createElement('input');
    otherSpanBox.appendChild(otherGroup);
    otherGroup.type = 'hidden';
    otherGroup.className = 'group-id';
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
 * @return SubjectTypeFilter odczytany filtr
 */
SubjectTypeFilterForm.prototype.readFilter = function()
{
    var deserializedFilter = new SubjectTypeFilter();

    var subjectTypes = $(this.container).find('input[type=checkbox]');
    for (var i = 0; i < subjectTypes.length; i++)
    {
        if ($(subjectTypes[i]).hasClass('filter-subject-type-meta'))
            continue;

        var subKey = subjectTypes[i].id;
        if (subKey.substr(0, 20) != 'filter-subject-type-')
            throw new Error('SubjectTypeFilter.readFilterFromForm: Nieprawidłowy id pola');
        subKey = subKey.substr(20);
        if (subjectTypes[i].checked)
            deserializedFilter.enableType(subKey);
        else
            deserializedFilter.disableType(subKey);
    }

    deserializedFilter.setMetaMode(this.metaMode);

    return deserializedFilter;
};

/**
 * Ustawia formularz zgodnie z podanym filtrem.
 *
 * @param filter filtr, do ustawienia w formularzu
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
        subjectTypes[i].checked = filter.isEnabled(subKey);
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
