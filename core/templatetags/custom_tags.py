from django import template
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        if k == 'page':
            query[k] = str(v)  # Ensure page is a string
        else:
            query[k] = v
    return '?' + urlencode(query)