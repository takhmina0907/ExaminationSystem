from django import template

from things.models import Question, Option

register = template.Library()


@register.filter
def modulo(num, val):
    return num % val


@register.filter
def count_correct(question):
    return question.options.filter(is_correct=True).count()