if (typeof Proposal == 'undefined') // todo scalić/wywalić
    Proposal = new Object();

Proposal.history = new Object();

Proposal.history.restoreButtonsAreReady = false;

Proposal.history.initRestoreButtons = function()
{
    if (Proposal.history.restoreButtonsAreReady)
        return;
    Proposal.history.restoreButtonsAreReady = true;

    $('.subjectrestore').click(function()
    {
        return !!confirm("Jesteś pewien?");
    });
};

$(Proposal.history.initRestoreButtons);
