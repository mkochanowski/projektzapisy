var $ = django.jQuery;
$(document).ready(function() {
    $('.field-limit').find('p').append("" +
       "<label style='float:right'>Zmień limit na: <input type='text' name='new_limit' id='new_limit'><button id='change_group_limit'>Zmień</button></label><div id='hidden_form_container' style='display:hidden'></div>");
    $('#change_group_limit').click(function(event){
        event.preventDefault();
        var limit = $('#new_limit').val();
        var group = $('.field-id div p').text();
        if(!limit || !group){
            return;
        }
        var theForm, newInput1, newInput2, newInput3;
          theForm = document.createElement('form');
          theForm.action = '/fereol_admin/courses/group/change_limit/';
          theForm.method = 'post';
        newInput1 = document.createElement('input');
        newInput1.type = 'hidden';
        newInput1.name = 'limit';
        newInput1.value = limit;
        newInput2 = document.createElement('input');
        newInput2.type = 'hidden';
        newInput2.name = 'group_id';
        newInput2.value = group;
        newInput3 = document.createElement('input');
        newInput3.type = 'hidden';
        newInput3.name = 'csrfmiddlewaretoken';
        newInput3.value = $('input[name="csrfmiddlewaretoken"]').val();
        // Now put everything together...
        theForm.appendChild(newInput1);
        theForm.appendChild(newInput2);
        theForm.appendChild(newInput3);
        document.getElementById('hidden_form_container').appendChild(theForm);
        theForm.submit();

    });
});