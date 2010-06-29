/**
 * Funkcje i klasy odpowiedzialne za preferencje pracowników na temat
 * przedmiotów z oferty dydaktycznej.
 */

Prefs = Object();

/**
 * Zainicjowanie formularza preferencji.
 */
Prefs.init = function()
{
    var i;

    $('#od-prefs-top-bar')[0].style.display = 'block';

    var prefsList = $('#od-prefs-list');
    Prefs.prefsList = prefsList[0];

    Prefs.subjects = new Array();
    var subjectElements = prefsList.children('li');
    for (i = 0; i < subjectElements.length; i++)
    {
        var sub = Prefs.Subject.fromElement(subjectElements[i]);
        sub.attachControls();
        sub.setCollapsed(true);
        Prefs.subjects.push(sub);
    }

    Prefs.emptyFilterWarning = document.createElement('p');
    Prefs.emptyFilterWarning.className = 'emptyFilterWarning';
    Prefs.emptyFilterWarning.style.display = 'none';
    $(Prefs.emptyFilterWarning).insertAfter(prefsList);
    Prefs.emptyFilterWarning.appendChild(document.createTextNode(
        'Do podanego filtra nie pasuje żaden z przedmiotów.'));

    // ustawianie początkowego filtra
    var cookieFilter = Prefs.Filter.deserialize($.cookies.get('prefs-filter'));
    if (cookieFilter)
    {
        Prefs.currentFilter = cookieFilter;
        cookieFilter.saveFilterToForm();
    }
    else
        Prefs.currentFilter = Prefs.Filter.readFilterFromForm();
    Prefs.doFilter(Prefs.currentFilter);
    Prefs.filterThread();

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
        for (i = 0; i < Prefs.subjects.length; i++)
            Prefs.subjects[i].setCollapsed(collapse);
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
    if (Prefs.emptyMessage)
        Prefs.emptyMessage = Prefs.emptyMessage[0];
    else
        Prefs.emptyMessage = null;
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

            var sub = new Prefs.Subject();
            sub.id = data.id;
            sub.type = data.type;
            sub.name = data.name;
            sub.hideURL = data.hideurl;
            sub.unhideURL = data.unhideurl;

            sub.container = document.createElement('li');
            Prefs.prefsList.appendChild(sub.container);

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

            Prefs.subjects.push(sub);
            sub.attachControls();
            Prefs.doFilter(Prefs.currentFilter);

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

Prefs.Subject = function()
{
    this.id = null;
    this.type = null;
    this.name = null;
    this.collapsed = false;
    this.hidden = false;
    this.container = null;
    this.prefContainer = null;
    this.hideURL = null;
    this.unhideURL = null;
};

Prefs.Subject.fromElement = function(element)
{
    var el = $(element);

    var sub = new Prefs.Subject();
    sub.id = Number(el.children('.pref-id').val());
    sub.type = el.children('.pref-type').val();
    sub.name = el.children('.name').text().trim();
    sub.hideURL = el.children('.pref-hide-url').val().trim();
    sub.unhideURL = el.children('.pref-unhide-url').val().trim();
    sub.collapsed = el.hasClass('collapsed');
    sub.hidden = el.hasClass('hidden');

    sub.container = el[0];
    sub.prefContainer = el.children('ul')[0];

    return sub;
};

Prefs.Subject.prototype.attachControls = function()
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
                Prefs.doFilter(Prefs.currentFilter);
            }
        });

    });
};

Prefs.Subject.prototype.setCollapsed = function(collapsed)
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
 * "Wątek" sprawdza, czy formularz nie zmienił zawartości - jeżeli tak, to
 * aplikuje filtr.
 */
Prefs.filterThread = function()
{
    var newFilter = Prefs.Filter.readFilterFromForm();

    if (!Prefs.currentFilter.isEqual(newFilter))
    {
        Prefs.currentFilter = newFilter;
        $.cookies.set('prefs-filter', Prefs.currentFilter);
        Prefs.doFilter(Prefs.currentFilter);
    }

    setTimeout(Prefs.filterThread, 50);
};

/**
 * Aplikuje wybrany filtr do listy przedmiotów.
 *
 * @param filter filtr, który chcemy zaaplikować do listy przedmiotów
 */
Prefs.doFilter = function(filter)
{
    var i;

    var anyVisible = false;

    for (i = 0; i < Prefs.subjects.length; i++)
    {
        var sub = Prefs.subjects[i];

        var isVisible = true;

        if (isVisible && !filter.showHidden)
            if (sub.hidden)
                isVisible = false;

        if (isVisible)
            isVisible = filter.subjectTypes.isEnabled(sub.type);

        if (isVisible && filter.phrase != '')
           isVisible = (sub.name.toLowerCase().indexOf(filter.phrase) >= 0);

        sub.container.style.display = isVisible?'block':'none';
        if (isVisible)
            anyVisible = true;
    }

    Prefs.emptyFilterWarning.style.display = anyVisible?'none':'block';
    Prefs.prefsList.style.display = anyVisible?'block':'none';
};

/*** Filtrowanie - klasa filtra ***********************************************/

/**
 * Klasa filtra przy głosowaniu - konstruktor.
 */
Prefs.Filter = function()
{
    this.phrase = '';
    this.subjectTypes = new SubjectTypeFilter();
    this.showHidden = false;
};

/**
 * Deserializacja filtra, np. z cookie.
 *
 * @param serializedFilter filtr w postaci surowej
 * @return Prefs.Filter obiekt filtra
 */
Prefs.Filter.deserialize = function(serializedFilter)
{
    if (!serializedFilter)
        return null;

    var deserializedFilter = new Prefs.Filter();
    deserializedFilter.setPhrase(serializedFilter.phrase);
    deserializedFilter.subjectTypes = SubjectTypeFilter.
        deserialize(serializedFilter.subjectTypes);
    deserializedFilter.setShowHidden(serializedFilter.showHidden);

    return deserializedFilter;
};

/**
 * Generuje filtr na podstawie zawartości formularza.
 *
 * @return Vote.Filter obiekt filtra z odczytaną zawartością
 */
Prefs.Filter.readFilterFromForm = function()
{
    var newFilter = new Prefs.Filter();

    var phrase = $('#od-prefs-q')[0].value;
    if (phrase != TopBarFilter.emptyFilterText)
        newFilter.setPhrase(phrase);

    newFilter.subjectTypes = SubjectTypeFilter.readFilterFromForm($('#od-prefs-subjtype'));

    newFilter.setShowHidden($('#od-prefs-hidden')[0].checked);

    return newFilter;
};

/**
 * Ustawia formularz na podstawie filtra.
 */
Prefs.Filter.prototype.saveFilterToForm = function()
{
    if (this.phrase == '')
        $('#od-prefs-q')[0].value = TopBarFilter.emptyFilterText;
    else
        $('#od-prefs-q')[0].value = this.phrase;

    this.subjectTypes.saveFilterToForm($('#od-prefs-subjtype'));

    $('#od-prefs-hidden')[0].checked = this.showHidden;
};

/**
 * Ustawia frazę, której szukamy w nazwach przedmiotów.
 *
 * @param phrase fraza, której chcemy szukać
 */
Prefs.Filter.prototype.setPhrase = function(phrase)
{
    this.phrase = $.trim(phrase).toLowerCase();
};

Prefs.Filter.prototype.setShowHidden = function(showHidden)
{
    this.showHidden = !!showHidden;
};

/**
 * Porównuje filtr z innym.
 *
 * @param filter filtr do porównania
 * @return boolean filtry są równe
 */
Prefs.Filter.prototype.isEqual = function(filter)
{
    if (this.phrase != filter.phrase)
        return false;
    if (this.showHidden != filter.showHidden)
        return false;
    if (!this.subjectTypes.isEqual(filter.subjectTypes))
        return false;
    return true;
};
