
from django import template

register = template.Library()

@register.filter
def addstr(str1, str2):
    return str1 + str2