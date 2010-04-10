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
        '<tr class="book"> ' +
        '   <td class="label" ></td>' + 
        '   <td class="field"><input type="text" name="books[]" /></td>' + 
        '</tr>'
    );
    
    var lastBook = books.eq(books.length-1);
    lastBook.after(newBook);
        
    return false;
}