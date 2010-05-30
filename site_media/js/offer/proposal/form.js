if (typeof Proposal == 'undefined') // todo scalić/wywalić
    Proposal = new Object();

Proposal.form = new Object();

Proposal.form.init = function()
{
    Proposal.form.bookList = $('#od-proposal-form-books').children('ul')[0];

    var addBookButton = document.createElement('input');
    addBookButton.type = 'button';
    addBookButton.value = 'dodaj książkę';
    $(addBookButton).click(Proposal.form.addBook);
    $(addBookButton).insertAfter(Proposal.form.bookList);

    var booksListElements = $(Proposal.form.bookList).children('li');
    for (var i = 0; i < booksListElements.length; i++)
        Proposal.form.initBook(booksListElements[i]);

    $(Proposal.form.bookList).sortable({handle : 'img.move'});

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

Proposal.form.removeBook = function(bookElement)
{
    $(bookElement).remove();
    if ($(Proposal.form.bookList).children('li').length == 0)
        Proposal.form.addBook();
};
