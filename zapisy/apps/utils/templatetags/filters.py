from django import template

register = template.Library()


@register.filter
def add_class(field, class_name):
    return field.as_widget(attrs={"class": " ".join([field.css_classes(), class_name])})


@register.filter(name="lookup")
def lookup(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    return None


@register.filter(name="next")
def next_iterator(iterator):
    return next(iterator)
