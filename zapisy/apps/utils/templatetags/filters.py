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


@register.filter(name="max")
def maximum(first, second):
    if isinstance(first, str):
        first = type(second)(first)
    return max(first, second)


@register.filter(name="min")
def minimum(first, second):
    if isinstance(first, str):
        first = type(second)(first)
    return min(first, second)
