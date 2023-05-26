from django import template

register = template.Library()


@register.filter
def golf_score(score):
    if score == 0:
        return "E"
    elif score > 0:
        return "+" + str(score)
    else:
        return str(score)
