from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite obtener dictionary[key] en la plantilla.
    """
    try:
        return dictionary.get(int(key)) or dictionary.get(str(key))
    except (ValueError, AttributeError):
        return None

#Para el reproductor de videos
register = template.Library()

@register.filter
def get_itemVid(dict_obj, key):
    return dict_obj.get(key)

@register.filter
def youtube_embed(url: str) -> str:
    if not url:
        return ''
    m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]+)', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'
    if 'embed/' in url:
        return url
    return url

#para login
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add a CSS class to a Django form field.
    Usage: {{ form.field|add_class:"class-name" }}
    """
    if hasattr(field, 'field'):
        return field.as_widget(attrs={"class": css_class})
    else:
        return field