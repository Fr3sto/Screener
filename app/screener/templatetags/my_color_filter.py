from django import template
from ..models import Impulses
register = template.Library()

def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list

register.filter(is_in)
@register.filter()
def my_color_filter(impulse : Impulses):
    if isinstance(impulse, Impulses):
        if impulse.type == "L":
            if impulse.isOpen == 1:
                return 'bg-success'
        elif impulse.type == "S":
            if impulse.isOpen == 1:
                return 'bg-danger'
        return ''



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

