/**
 * Model filtra po typach przedmiotów.
 */

function SubjectTypeFilter()
{
    this.enabledTypes = new Object();
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

SubjectTypeFilter.prototype.isEnabled = function(type)
{
    return !!this.enabledTypes[$.trim(type)];
}

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

    for (var subjectType in serializedFilter.enabledTypes)
        if (serializedFilter.enabledTypes[subjectType])
            deserializedFilter.enableType(subjectType);

    return deserializedFilter;
};

SubjectTypeFilter.readFilterFromForm = function(container)
{
    var deserializedFilter = new SubjectTypeFilter();

    var subjectTypes = $(container).find('input[type=checkbox]');
    for (var i = 0; i < subjectTypes.length; i++)
    {
        var subKey = subjectTypes[i].id;
        if (subKey.substr(0, 20) != 'filter-subject-type-')
            throw new Error('SubjectTypeFilter.readFilterFromForm: Nieprawidłowy id pola');
        subKey = subKey.substr(20);
        if (subjectTypes[i].checked)
            deserializedFilter.enableType(subKey);
        else
            deserializedFilter.disableType(subKey);
    }

    return deserializedFilter;
};

SubjectTypeFilter.prototype.saveFilterToForm = function(container)
{
    var subjectTypes = $(container).find('input[type=checkbox]');
    for (var i = 0; i < subjectTypes.length; i++)
    {
        var subKey = subjectTypes[i].id;
        if (subKey.substr(0, 20) != 'filter-subject-type-')
            throw new Error('SubjectTypeFilter.readFilterFromForm: Nieprawidłowy id pola');
        subKey = subKey.substr(20);
        subjectTypes[i].checked = this.isEnabled(subKey);
    }
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
        if ($(element).hasClass(visibleType))
            return true;
    return false;
};
