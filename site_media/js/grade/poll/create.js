if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.create = new Object();

Poll.create.init = function()
{
    Poll.create.sections      = $('#sections');
    Poll.create.chosenSection = $('#sections-list').children('ul')[0];

    $('#section-add').click(function()
    {
        Poll.create.addSection();
    });

    $(Poll.create.chosenSection).sortable({handle : 'p'});
}

$(Poll.create.init);

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


