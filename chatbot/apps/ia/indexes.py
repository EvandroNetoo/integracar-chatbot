from django.contrib.postgres.indexes import PostgresIndex


class BM25Index(PostgresIndex):
    suffix = 'bm25'

    def __init__(self, *expressions, key_field: str | None = None, **kwargs):
        self.key_field = key_field
        super().__init__(*expressions, **kwargs)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        if self.key_field is not None:
            kwargs['key_field'] = self.key_field
        return path, args, kwargs

    def get_with_params(self):
        with_params = []
        if self.key_field is not None:
            with_params.append(f'key_field = {self.key_field}')
        return with_params
