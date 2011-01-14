if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.create = new Object();

Poll.create.init = function()
{
    Poll.create.sections      = $('#sections');
    Poll.create.chosenSection = $('#sections-list').children('ul')[0];

    $('#section-add').click(Poll.create.addSection);
    $('#semester').change(Poll.create.changeSemester);
    $('#subjects').change(Poll.create.changeSubjects);
    $('#type').change(Poll.create.changeTypes);

    $('.type-visibility').hide();
    $('.group-visibility').hide();

    $(Poll.create.chosenSection).sortable({handle : 'p'});
}

$(Poll.create.init);

Poll.create.changeSubjects = function()
{
    var subject = $('#subjects').val();
    if ( subject > 0 )
    {
        $('.type-visibility').show();
        Poll.create.changeTypes();
    }
    else if (subject == 0)
    {
        $('.type-visibility').show();
        Poll.create.changeTypes();
    }
    else
    {
        $('.type-visibility').hide();
        $('.group-visibility').hide();
    }
}

Poll.create.changeTypes = function()
{
    var type    = $('#type').val();
    var subject = $('#subjects').val();
    if ( type > 0 && subject > 0 )
    {
        $('.group-visibility').show();
        dataString = 'type=' + type + '&subject=' + subject
        $.ajax({
            type: "POST",
            url: "grade/poll/ajax_get_groups",
            async: false,
            dataType: 'json',
            data: dataString,
            success: Poll.create.loadGroups
        });
    }
    if (type < 1)
    {
        $('.group-visibility').hide();
        
    }
}

Poll.create.loadGroups  = function(groups)
{
    $("#group").children().remove();
    $("#group").append( Poll.create.createOption('0', 'Wszystkie grupy') );
    $.each(groups, function(key, group)
    {
        $("#group").append( Poll.create.createOption( group[0], group[1] ) );
    });
}

Poll.create.changeSemester = function()
{
    var semester = $('#semester').val();
    dataString = 'semester=' + semester
    $.ajax({
        type: "POST",
        url: "grade/poll/ajax_get_subjects",
        async: false,
        dataType: 'json',
        data: dataString,
        success: Poll.create.loadSubjects
    });
}

Poll.create.loadSubjects = function(subjects)
{
    $("#subjects").children().remove();
    var item1 = Poll.create.createOption('-1', 'Nie przypisane do przedmiotu')
    var item2 = Poll.create.createOption('0', 'Wszystkie grupy')
    $("#subjects").append(item1);
    $("#subjects").append(item2);
    $.each(subjects, function(key, value)
    {
        $("#subjects").append( Poll.create.createOption( value[0], value[1] ) );
    });

}

Poll.create.createOption = function(value, text)
{
    var item = document.createElement('option');
    item.value = value
    $(item).text(text)
    return item
}
Poll.create.initSection = function(sectionElement)
{


    /*
        TODO: rozwin
        TODO: zwin
        TODO: edytuj
     */

    var sectionLabel = document.createElement('p');
    label = $('#sections option:selected').text();
    $(sectionLabel).text(label);

    var sectionRemoveButton = document.createElement('img');
    sectionRemoveButton.alt = 'usuń';
    sectionRemoveButton.className = 'remove';
    sectionRemoveButton.src = '/site_media/images/remove-ico.png';
    sectionLabel.appendChild(sectionRemoveButton);

    sectionElement.appendChild(sectionLabel);
    $(sectionRemoveButton).click(function()
    {
        Poll.create.removeSection(sectionElement);
    });

}

Poll.create.addSection = function()
{
    var newSection  = document.createElement('li');
    var sectionId   = document.createElement('input');
    sectionId.type  = 'hidden';
    sectionId.value = $(Poll.create.sections).val()
    sectionId.name  = 'sections[]'

    newSection.appendChild(sectionId);
    Poll.create.initSection(newSection);
    Poll.create.chosenSection.appendChild(newSection);
}

Poll.create.removeSection = function(sectionElement)
{
    $(sectionElement).remove();
}


