from django import template

register = template.Library()


@register.inclusion_tag('components/search.html')
def search_form(form):
    return {'form': form}
