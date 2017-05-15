/* gettext library */
// This function is copied from django admin path

var catalog = new Array();

function pluralidx(count) { return (count == 1) ? 0 : 1; }


function gettext(msgid) {
    var value = catalog[msgid];
    if (typeof(value) == 'undefined') {
    return msgid;
    } else {
    return (typeof(value) == 'string') ? value : value[0];
    }
}

function ngettext(singular, plural, count) {
    value = catalog[singular];
    if (typeof(value) == 'undefined') {
    return (count == 1) ? singular : plural;
    } else {
    return value[pluralidx(count)];
    }
}

function gettext_noop(msgid) { return msgid; }

function interpolate(fmt, obj, named) {
    if (named) {
    return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
    return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
}


function beforeSubmitButton(nameEditPlID,nameEditEnID) 
{ 
    var namePL = document.getElementById(nameEditPlID);
    var nameEN = document.getElementById(nameEditEnID);
    
    if (namePL.value=="") namePL.value=nameEN.value;
    if (nameEN.value=="") nameEN.value=namePL.value;

    var listRows = document.querySelectorAll('[id^="id_studentwork_set-"]');

    for ( var i = listRows.length-1; i>=0 ; i-- ) {
        //id_studentwork_set-2-hours
        var idString = listRows[i].id;

        if (idString.indexOf('id_studentwork_set')==0)
        if (idString.indexOf('-hours')!=-1)
        if (listRows[i].value=="" || listRows[i].value=="0")
        {
            listRows[i].parentElement.parentElement.remove();            
        }
    }
}
