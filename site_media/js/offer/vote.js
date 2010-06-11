/**
 * Funkcje i klasy odpowiedzialne za głosowanie studentów na ofertę dydaktyczną.
 */

Vote = Object();

/**
 * Zainicjowanie formularza głosowania.
 */
Vote.init = function()
{
    var i;

    $('#od-vote-top-bar')[0].style.display = 'block';

    $('#od-vote-reset').click(function()
    {
        $('#od-vote-q')[0].value = TopBarFilter.emptyFilterText;
    });

    // licznik punktów dla konkretnego semestru
    var assignSemesterCounter = function(semesterNode)
    {
        var counterContainer = document.createElement('span');
        $(semesterNode).children('h2').append(counterContainer);
        counterContainer.appendChild(document.createTextNode(' (punktów: '));
        var counter = document.createElement('span');
        counterContainer.appendChild(counter);
        counterContainer.appendChild(document.createTextNode(')'));

        var votes = $(semesterNode).find('select');

        var countSemester = function()
        {
            var count = 0;
            for (var i = 0; i < votes.length; i++)
            {
                var voteValue = parseInt($.trim(votes[i].value));
                if (isNaN(voteValue) || voteValue < 0)
                    throw new Error('Vote.refreshCounters: nieprawidłowa wartość głosu');
                count += voteValue;
            }

            $(counter).text(count);
        };
        countSemester();

        votes.change(countSemester);
    };

    // dodawanie do semestrów komunikatów o pustym filtrze oraz liczników punktów
    var semesters = $('div.od-vote-semester');
    for (i = 0; i < semesters.length; i++)
    {
        var semester = semesters[i];

        var emptyFilterWarning = document.createElement('p');
        emptyFilterWarning.className = 'emptyFilterWarning';
        emptyFilterWarning.style.display = 'none';
        semester.appendChild(emptyFilterWarning);
        emptyFilterWarning.appendChild(document.createTextNode(
            'Do podanego filtra nie pasuje żaden przedmiot z tego semestru.'));

        assignSemesterCounter(semester);
    }

    // ustawianie początkowego filtra
    var cookieFilter = Vote.Filter.deserialize($.cookies.get('vote-filter'));
    if (cookieFilter)
    {
        Vote.currentFilter = cookieFilter;
        cookieFilter.saveFilterToForm();
    }
    else
        Vote.currentFilter = Vote.Filter.readFilterFromForm();
    Vote.doFilter(Vote.currentFilter);
    Vote.filterThread();


    // ogólne liczniki punktów
    var maxPointsNode = $('#od-vote-maxPoints');
    Vote.maxPoints = parseInt($.trim(maxPointsNode.children('span').text()));
    if (isNaN(Vote.maxPoints))
        throw new Error('Vote.init: Niepoprawna wartość maxPoints');

    maxPointsNode.empty();
    maxPointsNode = maxPointsNode[0];
    maxPointsNode.appendChild(document.createTextNode('Wykorzystane punkty w sumie: '));
    Vote.maxPointsNode = document.createElement('span');
    maxPointsNode.appendChild(Vote.maxPointsNode);
    maxPointsNode.appendChild(document.createTextNode('.'));

    Vote.totalSubjectsCount = $('#od-vote-form').find('select').length;
    Vote.wantedSubjectsCount = $('#od-vote-form').find('.isFan').length;

    var onlyWantedLabel = $('#od-vote-onlywanted').parent().children('label')[0];
    onlyWantedLabel.appendChild(document.createTextNode(' (' +
        Vote.wantedSubjectsCount + ' z ' + Vote.totalSubjectsCount + ')'));

    $('#od-vote-form').find('select').change(Vote.refreshCounters);

    Vote.refreshCounters();

    // weryfikacja formularza (i tak potem jest to sprawdzane po stronie serwera)

    $('#od-vote-form').submit(function()
    {
        MessageBox.clear();
        Vote.refreshCounters();
        if (Vote.totalPoints <= Vote.maxPoints)
            return true;
        MessageBox.display('Przekroczono limit głosowania. Limit wynosi ' +
            Vote.maxPoints + ', a oddano głos o watości ' + Vote.totalPoints + '.');
        return false;
    });
};

$(Vote.init);

/**
 * Odświeża liczniki w formularzu (wykorzystane punkty, przedmioty "na które
 * chce iść").
 */
Vote.refreshCounters = function()
{
    var votes = $('#od-vote-form').find('select');
    var totalPoints = 0;

    for (var i = 0; i < votes.length; i++)
    {
        var voteValue = parseInt($.trim(votes[i].value));
        if (isNaN(voteValue) || voteValue < 0)
            throw new Error('Vote.refreshCounters: nieprawidłowa wartość głosu');
        totalPoints += voteValue;
    }

    $(Vote.maxPointsNode).text(totalPoints + ' z ' + Vote.maxPoints);
    Vote.maxPointsNode.className = (totalPoints > Vote.maxPoints)?'warning':'';

    Vote.totalPoints = totalPoints;
};


/*******************************************************************************
 * Filtrowanie
 ******************************************************************************/

/**
 * "Wątek" sprawdza, czy formularz nie zmienił zawartości - jeżeli tak, to
 * aplikuje filtr.
 */
Vote.filterThread = function()
{
    var newFilter = Vote.Filter.readFilterFromForm();

    if (!Vote.currentFilter.isEqual(newFilter))
    {
        Vote.currentFilter = newFilter;
        $.cookies.set('vote-filter', Vote.currentFilter);
        Vote.doFilter(Vote.currentFilter);
    }

    setTimeout(Vote.filterThread, 50);
};

/**
 * Aplikuje wybrany filtr do listy przedmiotów.
 *
 * @param filter filtr, który chcemy zaaplikować do listy przedmiotów
 */
Vote.doFilter = function(filter)
{
    var i;

    var subjects = $('#od-vote-form').find('li.od-vote-subject');
    for (i = 0; i < subjects.length; i++)
    {
        var isVisible = false;
        var subject = subjects[i];

        if (filter.onlyWanted)
        {
            if ($(subject).hasClass('isFan'))
                isVisible = true;
        }
        else
            isVisible = true;

        if (isVisible)
            isVisible = filter.subjectTypes.haveEnabledTypeClass(subject);

        if (isVisible && filter.phrase != '')
            isVisible = ($(subject).children('label').text().toLowerCase().
                indexOf(filter.phrase) >= 0)

        if (isVisible)
        {
            $(subject).addClass('visible');
            $(subject).removeClass('hidden');
        }
        else
        {
            $(subject).removeClass('visible');
            $(subject).addClass('hidden');
        }
    }

    var lists = $('#od-vote-form').find('ul');
    for (i = 0; i < lists.length; i++)
    {
        var visibleElements = $(lists[i]).children('li.visible');
        if (visibleElements.length == 0)
        {
            lists[i].style.display = 'none';
            $(lists[i].parentNode).children('.emptyFilterWarning')[0].style.display = 'block';
        }
        else
        {
            $(lists[i].parentNode).children('.emptyFilterWarning')[0].style.display = 'none';
            lists[i].style.display = '';
            for (var j = 0; j < visibleElements.length - 1; j++)
                visibleElements[j].style.borderBottomWidth = '1px';
            visibleElements[visibleElements.length - 1].style.borderBottomWidth = '0';
        }
    }
};

/*** Filtrowanie - klasa filtra ***********************************************/

/**
 * Klasa filtra przy głosowaniu - konstruktor.
 */
Vote.Filter = function()
{
    this.phrase = '';
    this.subjectTypes = new SubjectTypeFilter();
    this.onlyWanted = false;
};

/**
 * Deserializacja filtra, np. z cookie.
 *
 * @param serializedFilter filtr w postaci surowej
 * @return Vote.Filter obiekt filtra
 */
Vote.Filter.deserialize = function(serializedFilter)
{
    if (!serializedFilter)
        return null;

    var deserializedFilter = new Vote.Filter();
    deserializedFilter.setPhrase(serializedFilter.phrase);
    deserializedFilter.setOnlyWanted(serializedFilter.onlyWanted);
    deserializedFilter.subjectTypes = SubjectTypeFilter.
        deserialize(serializedFilter.subjectTypes);

    return deserializedFilter;
};

/**
 * Generuje filtr na podstawie zawartości formularza.
 *
 * @return Vote.Filter obiekt filtra z odczytaną zawartością
 */
Vote.Filter.readFilterFromForm = function()
{
    var newFilter = new Vote.Filter();

    var phrase = $('#od-vote-q')[0].value;
    if (phrase != TopBarFilter.emptyFilterText)
        newFilter.setPhrase(phrase);
    newFilter.setOnlyWanted($('#od-vote-onlywanted')[0].checked);

    newFilter.subjectTypes = SubjectTypeFilter.readFilterFromForm($('#od-vote-subjtype'));

    return newFilter;
};

/**
 * Ustawia formularz na podstawie filtra.
 */
Vote.Filter.prototype.saveFilterToForm = function()
{
    if (this.phrase == '')
        $('#od-vote-q')[0].value = TopBarFilter.emptyFilterText;
    else
        $('#od-vote-q')[0].value = this.phrase;

    $('#od-vote-onlywanted')[0].checked = this.onlyWanted;

    this.subjectTypes.saveFilterToForm($('#od-vote-subjtype'));
};

/**
 * Ustawia frazę, której szukamy w nazwach przedmiotów.
 *
 * @param phrase fraza, której chcemy szukać
 */
Vote.Filter.prototype.setPhrase = function(phrase)
{
    this.phrase = $.trim(phrase).toLowerCase();
};

/**
 * Ustawia flagę przepuszczającą przez filtr tylko przedmioty, na które
 * zagłosowano (głos > 0).
 *
 * @param onlyWanted czy wyświetlać tylko przedmioty, na które zagłosowano
 */
Vote.Filter.prototype.setOnlyWanted = function(onlyWanted)
{
    this.onlyWanted = !!onlyWanted;
};

/**
 * Porównuje filtr z innym.
 *
 * @param filter filtr do porównania
 * @return boolean filtry są równe
 */
Vote.Filter.prototype.isEqual = function(filter)
{
    if (this.phrase != filter.phrase)
        return false;
    if (this.onlyWanted != filter.onlyWanted)
        return false;
    if (!this.subjectTypes.isEqual(filter.subjectTypes))
        return false;
    return true;
};
