from django import template
register = template.Library()

@register.filter()
def my_color_filter(isOpen):
    if isOpen == 1:
        td_class = 'bg-success'
    else:
        td_class = ''
    return td_class

@register.filter()
def filter_count_in_impulse(count):
    if count >= 20:
        td_class = 'bg-success'
    else:
        td_class = ''
    return td_class

