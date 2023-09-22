from django import template
register = template.Library()

def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list

register.filter(is_in)
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

@register.filter()
def filter_count_OrderL(count):
    if count >= 5:
        td_class = 'bg-success'
    else:
        td_class = ''
    return td_class

@register.filter()
def filter_count_OrderS(count):
    if count >= 5:
        td_class = 'bg-danger'
    else:
        td_class = ''
    return td_class

