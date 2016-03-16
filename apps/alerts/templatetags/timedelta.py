
from django import template
from django.utils.timesince import timesince
from datetime import datetime

register = template.Library()

#Time to minutes converter for Notifications bar
#TODO test
@register.filter
def timedelta(value, arg=None):
    if not value:
        return ''
    if arg:
        cmp = arg
    else:
        cmp = datetime.now()
    if value > cmp:
        return "in %s" % timesince(cmp, value)
    else:
        return "%s ago" % timesince(value, cmp)

#register.filter('timedelta',timedelta)
