from django import template

register = template.Library()

@register.inclusion_tag("tags/form_field_for.html")
def form_field_for(form_field):
    return { 'form_field': form_field }