if (typeof Proposal == 'undefined') // todo scalić/wywalić
    Proposal = new Object();

Proposal.form = new Object();

Proposal.form.init = function()
{
    Proposal.form.bookList = $('#od-proposal-form-books').children('ul')[0];
    Proposal.form.typeList = $('#od-proposal-form-types').children('ul')[0];
    
    var addBookButton = document.createElement('input');
    addBookButton.type = 'button';
    addBookButton.value = 'dodaj książkę';
    $(addBookButton).click(Proposal.form.addBook);
    $(addBookButton).insertAfter(Proposal.form.bookList);

    var booksListElements = $(Proposal.form.bookList).children('li');
    for (var i = 0; i < booksListElements.length; i++)
        Proposal.form.initBook(booksListElements[i]);

    $(Proposal.form.bookList).sortable({handle : 'img.move'});

    var addTypeButton = document.createElement('input');
    addTypeButton.type = 'button';
    addTypeButton.value = 'kolejny typ';
    $(addTypeButton).click(Proposal.form.addType);
    $(addTypeButton).insertAfter(Proposal.form.typeList);

    var typesListElements = $(Proposal.form.typeList).children('li');
    for (var i = 1; i < typesListElements.length; i++)
        Proposal.form.initType(typesListElements[i]);

    $(Proposal.form.typeList).sortable({handle : 'img.move'});

    $('#od-proposal-form-name').focus();
};

$(Proposal.form.init);

Proposal.form.initBook = function(bookElement)
{
    var bookSortHandler = document.createElement('img');
    bookSortHandler.alt = 'przenieś';
    bookSortHandler.className = 'move';
    bookSortHandler.src = '/site_media/images/varrow.png';
    bookElement.appendChild(bookSortHandler);

    var bookRemoveButton = document.createElement('img');
    bookRemoveButton.alt = 'usuń';
    bookRemoveButton.className = 'remove';
    bookRemoveButton.src = '/site_media/images/remove-ico.png';
    bookElement.appendChild(bookRemoveButton);

    $(bookRemoveButton).click(function()
    {
        Proposal.form.removeBook(bookElement);
    });
};

Proposal.form.initType = function(typeElement)
{
    var typeRemoveButton = document.createElement('img');
    typeRemoveButton.alt = 'usuń';
    typeRemoveButton.className = 'remove';
    typeRemoveButton.src = '/site_media/images/remove-ico.png';
    typeElement.appendChild(typeRemoveButton);

    $(typeRemoveButton).click(function()
    {
        Proposal.form.removeType(typeElement);
    });
};

Proposal.form.addBook = function()
{
    var newBook = document.createElement('li');
    newBook.className = 'book';
    var newBookInput = document.createElement('input');
    newBookInput.type = 'text';
    newBookInput.name = 'books[]';
    newBook.appendChild(newBookInput);

    Proposal.form.initBook(newBook);

    Proposal.form.bookList.appendChild(newBook);
};

Proposal.form.addType = function()
{
    var newType = document.createElement('li');
    newType.className = 'type';
    $(newType).append($('#od-proposal-form-types ul li:first').html())
    Proposal.form.initType(newType);
    Proposal.form.typeList.appendChild(newType);
};


Proposal.form.removeBook = function(bookElement)
{
    $(bookElement).remove();
    if ($(Proposal.form.bookList).children('li').length == 0)
        Proposal.form.addBook();
};

Proposal.form.removeType = function(typeElement)
{
    $(typeElement).remove();
    if( $(Proposal.form.typeList).children('li').length == 0)
        Proposal.form.addType();
}
