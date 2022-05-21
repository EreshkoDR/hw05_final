from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def limit_char(text):
    output = ''
    if len(text) > 30:
        for i in range(31):
            output += text[i]
        return output
    else:
        return text
