$(document).ready(
    function()
    {
        $('#addBook').click(addBook);
    }
);  

function addBook()
{    
    var books = $('.book');
    
    var newBook = $(
        '<div class="book"> ' +
        '   <div class="label" >&nbsp;</div>' + 
        '   <div class="field"><input type="text" name="books[]" /></div>' + 
        '</div>'
    );
    
    var lastBook = books.eq(books.length-2);
    lastBook.after(newBook);
        
    return false;
}