from django.db.models import Func


class BM25Score(Func):
    function = 'paradedb.score'
    template = '%(function)s(%(expressions)s)'


class PdbQueryCast(Func):
    function = 'CAST'
    template = '%(expressions)s::pdb.query'
