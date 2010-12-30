/**
 * Plik dołączany razem z głównym szablonem.
 */

Fereol = new Object();

Fereol.init = function()
{
    $('.main-labelledSelect').change(function()
    {
        $(this).children('.label').remove();
    });
};

$(Fereol.init);
