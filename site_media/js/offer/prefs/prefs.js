Filtr = new Object();

Filtr.work = function()
{
    function strpos (haystack, needle) {
        var i = (haystack+'').indexOf(needle);
        return i;
    }
   var query = $("#od-prefs-q").val();
   var q;
   if (query=='Filtruj'||query=='') q = false;
        else q = true;
        
   var types = $('.od-filter-checkbox');
   var t = false;
   var typesArray = new Array();
   jQuery.each(types, function(){
        if($(this).children('input')[0].checked){
            t = true;
            typesArray.push($(this).children('input').val());
        }
   });
   var all = $("#od-prefs-list-tree").children();
   jQuery.each(all, function(){
        var name = $(this).children(".pref_name").val();
        var type = $(this).children(".pref_type").val();
        if(q && strpos(name.toLowerCase(), query.toLowerCase())<0){
            $(this).addClass('od-filter-hide');
            return true;
        }
        if(t && jQuery.inArray(type, typesArray)<0){
            $(this).addClass('od-filter-hide');
            return true;
        }
        $(this).removeClass('od-filter-hide');
   });
}

$(document).ready(function(){
     Filtr.work();
    $(".od-filter").keypress(function(e) {
            if(e.which == 10 || e.which == 13) {
                return false;
            }
        });

    $(".od-filter").keyup(function(){
        Filtr.work();
    });
    
    $('.od-filter-checkbox').change(function(){
        Filtr.work();
    });
    
    if( !$("#od-prefs-hidden")[0].checked ){
        $(".od-prefs-tree-hidden").hide();
    }
    if( $("#od-prefs-only-new")[0].checked ){
        $(".od-prefs-tree-hidden").hide();
        $(".od-prefs-tree-show").hide();    
    }
    $("#od-prefs-hidden").change(function(){
        if( this.checked && ! ($("#od-prefs-only-new")[0].checked)) {
            $(".od-prefs-tree-hidden").show();
        }
        else {
            $(".od-prefs-tree-hidden").hide();
        }
    });
    $("#od-prefs-only-new").change(function(){
            if( this.checked ) {
                $(".od-prefs-tree-hidden").hide();
                $(".od-prefs-tree-show").hide();
            }
            else {
                $(".od-prefs-tree-show").show();
                if($("#od-prefs-hidden")[0].checked){
                    $(".od-prefs-tree-hidden").show();
                }
            }
    });
    url = $("#od-prefs-undecided-list").text();
    Prefs.getList( url );
});

Prefs = new Object();
Prefs.unset = new Array();
Prefs.getList = function( url )
{
 $.ajax({  
   url: url,
   dataType: 'json',
   async: false,  
   success: function(data){  
                list = Prefs.generateList(data);
                $.each(list, function(key, value){
                    $("#od-prefs-undecided").append(value);
                });
                }  
 });  
}

Prefs.generateList = function( data )
{
    result = new Array();
    $.each(data.unset, function(){
        result.push( Prefs.generateElem(this) );
    });
    return result;
}

Prefs.generateElem = function( elem )
{
    Prefs.unset[elem.id] = new Object();
    Prefs.unset[elem.id].name = elem.name;
    Prefs.unset[elem.id].type = elem.type;
    Prefs.unset[elem.id].hideUrl  = elem.hideUrl;
    Prefs.unset[elem.id].showUrl  = elem.showUrl;
    // more???
    return "<li><input type=\"button\" value=\"&lt\" onclick=\"Prefs.initPref(this, '" + elem.url + "', " + elem.id + ")\" /> " + elem.name +"</li>";
}

Prefs.savePref = function ( elem )
{
    data = new Object();
    data.lecture        = $(elem).parent().children().children("li:nth-child(1)").children("select").val();
    data.review_lecture = $(elem).parent().children().children("li:nth-child(2)").children("select").val();
    data.tutorial       = $(elem).parent().children().children("li:nth-child(3)").children("select").val();
    data.lab            = $(elem).parent().children().children("li:nth-child(4)").children("select").val();
    id = $(elem).parent().children("input:nth-child(4)").val();
    url =  $("#od-prefs-save-url").text().replace(/0/, id);
 

 $.post(url,
           { lecture: data.lecture, review_lecture: data.review_lecture, tutorial:data.tutorial, lab:data.lab },
           function(result){
           }
          );
    
}

Prefs.initPref = function(elem, url, id)
{
    $.ajax({
        type: 'post',
        url: url,
        success: function(data)
        {
            var li = elem.parentNode;
            var ul = li.parentNode;
            $(li).remove();
            Prefs.addPref( id );
        }
    });
};

Prefs.addPref = function( id )
{
    var elem = $("<li>"); 
    $(elem).addClass("od-refs-tree-new");
    
    var button = $('<input type="button">');
    $(button).addClass("od-prefs-toggleCollapse");
    $(button).val("+");
    $(button).attr( "onclick", "Prefs.toggleCollapse(this)" );
    $(button).appendTo(elem);
    
    $(elem).append(" " + Prefs.unset[id].name);

    button = $('<input type="button">');
    button.addClass("od-prefs-toggleHidden hidden");
    $(button).attr( "onclick", "Prefs.toggleHidden(this, false, '" + Prefs.unset[id].showUrl + "')" );
    $(button).val("Nie ukrywaj");
    $(button).appendTo(elem);
    
    button = $('<input type="button">');
    button.addClass("od-prefs-toggleHidden");
    $(button).attr( "onclick", "Prefs.toggleHidden(this, true, '" + Prefs.unset[id].hideUrl + "')" );
    $(button).val("Ukryj");
    $(button).appendTo(elem);

    hidden = $('<input type="hidden">');
    hidden.addClass("pref_id");
    $(hidden).val(id);
    $(hidden).appendTo(elem);

    hidden = $('<input type="hidden">');
    hidden.addClass("pref_name");
    $(hidden).val(Prefs.unset[id].name);
    $(hidden).appendTo(elem);
    
    hidden = $('<input type="hidden">');
    hidden.addClass("pref_type");
    $(hidden).val(Prefs.unset[id].type);
    $(hidden).appendTo(elem);
    
    var ul = $("<ul>");
    
    Prefs.generateSelect(ul, id, "Wykład:", "lecture_select");
    Prefs.generateSelect(ul, id, "Repetytorium:", "review_lecture_select");
    Prefs.generateSelect(ul, id, "Ćwiczenia:", "tutorial_select");
    Prefs.generateSelect(ul, id, "Pracownia:", "lab_select");

    $(ul).appendTo(elem);
    
    $("#od-prefs-list-tree").append(elem); 
}

Prefs.generateSelect = function (parent, id, name, type)
{
    var li =  $("<li>");
    $(li).append(name);
    var select = $("<select>"); 
    $(select).addClass(type);
    $(select).attr("id", "id_"+ id +"_"+ type);
    $(select).append( $("#od-prefs-list-option").html() );
    $(select).appendTo(li);
    $(li).appendTo(parent); 
}

Prefs.toggleHidden = function(elem, hide, url)
{
    $.ajax({
        type: 'post',
        url: url,
        success: function(data)
        {
            var li = elem.parentNode;
            $(elem).addClass('hidden');
            if(hide){    
                $(elem).prev('input').removeClass('hidden');
                $(li).removeClass("od-prefs-tree-show");
                $(li).addClass("od-prefs-tree-hidden");
                if( !$("#od-prefs-hidden")[0].checked ){
                    $(".od-prefs-tree-hidden").hide();
                }
                Prefs.savePref(elem);
            } else {
                $(elem).next().removeClass('hidden');
                $(li).addClass("od-prefs-tree-show");
                $(li).removeClass("od-prefs-tree-hidden");
            }
            
        }
    });

};

Prefs.toggleCollapse = function(elem)
{
    var coll = $(elem.parentNode);
    if (coll.hasClass('subtree-visible'))
    {
        elem.value = '+';
        coll.removeClass('subtree-visible');
    }
    else
    {
        elem.value = '-';
        coll.addClass('subtree-visible');
    }
};

