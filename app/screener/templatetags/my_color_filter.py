from django import template
register = template.Library()

@register.filter()
def my_color_filter(isOpen):
    if isOpen == 1:
        td_class = 'bg-success'
    else:
        td_class = ''
    return td_class