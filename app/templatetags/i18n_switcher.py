from django import template
from django.urls import translate_url
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specific language
    Usage: {% change_lang 'en' %}
    """
    path = context.get('request').get_full_path()
    return translate_url(path, lang) or '/'

@register.filter
def translate_url_filter(path, language_code):
    """
    Template filter to translate a URL to the specified language
    Usage: {{ request.path|translate_url_filter:'en' }}
    """
    return translate_url(path, language_code) or path
