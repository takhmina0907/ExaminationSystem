import itertools
from django.db.models import Func


def lower_headers(iterator):
    return itertools.chain([next(iterator).lower()], iterator)


class Round(Func):
    function = 'ROUND'
    arity = 2
