from django.contrib.postgres.indexes import PostgresIndex


class BM25Index(PostgresIndex):
    suffix = 'bm25'

    def get_with_params(self):
        return [f"key_field = '{self.fields[0]}'"]
