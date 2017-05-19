function effectsTagsFiltersToggled()
{
    var filtersVisibility = $("#tagsEffectsFilters").css("display");

    if (filtersVisibility === "none")
    {
        $("#tagsEffectsFilters").css("display", "block");
        $("#tagsEffectsFiltersToggle").text("ukryj filtry efektów/tagów");
    }

    else
    {
        $("#tagsEffectsFilters").css("display", "none");
        $("#tagsEffectsFiltersToggle").text("pokaż filtry efektów/tagów");

        $("#effectsSearchEnabled").attr("checked", false);
        $("#tagsSearchEnabled").attr("checked", false);
    }
}

function unselectAllOptions(listId)
{
    $("#enr-courseFilter-" + listId + " option").each(function()
    {
        $(this).removeAttr("selected");
    });
}

function onEffectsFilterToggled()
{
    unselectAllOptions("effects", false);

    if ($("#effectsSearchEnabled").is(":checked"))
    {
        $("#enr-courseFilter-effects").removeAttr("disabled");
        $('#enr-courseFilter-effects').change();
    }

    else
    {
        $('#enr-courseFilter-effects').change();
        $("#enr-courseFilter-effects").attr("disabled", "disabled");
    }
}

function onTagsFilterToggled()
{
    unselectAllOptions("tags", false);

    if ($("#tagsSearchEnabled").is(":checked"))
    {
        $("#enr-courseFilter-tags").removeAttr("disabled");
        $('#enr-courseFilter-tags').change();
    }

    else
    {
        $('#enr-courseFilter-tags').change();
        $("#enr-courseFilter-tags").attr("disabled", "disabled");
    }
}

$(document).ready(function()
{
    unselectAllOptions("effects", false);
    unselectAllOptions("tags", false);
});
