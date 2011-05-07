if (typeof Poll == 'undefined')
    Poll = new Object();


jQuery.validator.addMethod("have_sections", function(value, element) {
  return $('#sections-list-ul').children().size() > 0;
}, "Ankieta musi mieć pytania");

jQuery.validator.addClassRules("anysection", {
  have_sections: true
});

Poll.create = new Object();

Poll.create.init = function()
{


	Poll.create.submitted     = false;
    Poll.create.sections      = $('#sections');
    Poll.create.chosenSection = $('#sections-list').children('ul')[0];
    Poll.create.firstChosen   = $(Poll.create.sections).children()[0]

    if( $("#group").children().size() < 2)
    {
        $('.type-visibility').hide();
        $('.group-visibility').hide();
        $(Poll.create.changeSubjects)
    }

    $('#section-add').click(Poll.create.addSection);
    $('#semester').change(Poll.create.changeSemester);
    $('#subjects').change(Poll.create.changeSubjects);
    $('#type').change(Poll.create.changeTypes);


    $(Poll.create.chosenSection).sortable({handle : 'p'});
	$("form").keypress(function(e)
	{
  		if (e.which == 13)
  		{
    		return false;
  		}
	});
    $("#poll-create").validate();
}

Poll.create.changeSubjects = function()
{
    var subject = $('#subjects').val();
    
    if ( subject > -1 )
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
    var type    = parseInt($('#type').val());
    var subject = parseInt($('#subjects').val());
    if ( type > 0 && subject > 0 )
    {
        $('.group-visibility').show();
        dataString = 'type=' + type + '&subject=' + subject
        $.ajax({
            type: "POST",
            url: "/grade/poll/ajax_get_groups",
            async: false,
            dataType: 'json',
            data: dataString,
            success: Poll.create.loadGroups
        });
    }
    if (type < 0)
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
        url: "/grade/poll/ajax_get_subjects",
        async: false,
        dataType: 'json',
        data: dataString,
        success: Poll.create.loadSubjects
    });
}

Poll.create.loadSubjects = function(subjects)
{
    $("#subjects").children().remove();
    var item1 =  Poll.create.createOption('-1', 'Nie przypisane do przedmiotu')
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
    return $('<option></option>').val(value).html(text);
}

Poll.create.addSection = function()
{
    var value = $(Poll.create.sections).val();
    if ( value === "-1" )
    {
        return false;
    }



    var newSection  = $('<li>');
    var sectionId   = $('<input type="hidden" name="sections[]"' +
            ' value="'+ value +'">');

    $(newSection).append(sectionId);
    var section = Poll.create.getSection( value );
    $(newSection).append( $(section) )
	$(Poll.create.chosenSection).append(newSection)
      
    $( '#section-content-' + sectionId.value ).hide();
    $( '#section-toggle-' + sectionId.value ).text( '+' );
    $( '.grade-section-toggle-button' ).unbind( 'click' );
    $( '.grade-section-toggle-button' ).click( function(){
        var toToggleId  = $(this).attr( 'id' ).split( '-' )[2];
        var toToggleObj = $('#section-content-' + toToggleId );
        toToggleObj.slideToggle( 250 );
        if ( $(this).text() == '+' ){
            $(this).text( '-' );
        } else {
            if ( $(this).text() == '-' ) {
                $(this).text( '+' );
            }
        }
        return false;

    });
    var sectionRemove =  $('<img src="/site_media/images/remove-ico.png"'+
                           'class="remove" alt="usuń">');

    $('#poll-section-title-' + value).after(sectionRemove);
    $(sectionRemove).click(function()
    {
        $(newSection).remove();
        $(Poll.create.sections).children('option[value="'+ value +'"]').show();
    });
    $(Poll.create.sections).children('option[value="'+ value +'"]').hide();
    $(Poll.create.firstChosen).attr('selected', true);
}

Poll.create.getSection = function( section_id )
{
	var result;
	$.ajax({
        type: "POST",
        url: "/grade/poll/get_section/" + section_id + "/",
        async: false,
        success: function(data)
        {
			result = data;
        }
    });
    return result
}

