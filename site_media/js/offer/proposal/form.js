$(document).ready(
    function()
    {
        $('#addBook').click(addBook);
        
        $('#books').sortable({
            handle : 'img',
            update : function ()
            {
                refreshBookOrder();
            }
        });
        refreshBookOrder();
    }
);  

function addBook()
{    
    var books = $('#books .book');
    
    var newBook = $(
        '<li class="book"> ' +
        '   <input type="text" name="books[]" />' +
        '   <span><img src="/site_media/images/arrow.jpg" alt="" /></span>' +          
        '</li>'
    );
    
    var lastBook = books.eq(books.length-1);
    lastBook.after(newBook);
    
    refreshBookOrder();
        
    return false;
}

function refreshBookOrder()
{
    var bookOrder = '';
    
    var first = true;
    var bookId;
    
    books = $('#books .book input').each(
        function()
        {
            if (!first)
            {
                bookOrder += ';';
            }
            
            bookId = $(this).attr('bookId');
                        
            if (bookId)
            {
                bookOrder += bookId;                
            }
            else
            {
                bookOrder += '_';
            }
            
            first = false;
        }
    );
    
    $('[name=bookOrder]').val(bookOrder);
}