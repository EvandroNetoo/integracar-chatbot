import re
from typing import Generator

from core.env import env
from django.db.models import (
    QuerySet,
    Value,
)
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.django import CosineDistance

from ia.functions import BM25Score, PdbQueryCast
from ia.models import ChunkDocumeto, Documento, StatusDocumento


class Rag:
    chat = ChatOpenAI(
        model='gpt-4.1-mini-2025-04-14',
        temperature=0.5,
        api_key=env.OPENAI_API_KEY,
    )

    embedding = OpenAIEmbeddings(
        model='text-embedding-3-small',
        dimensions=1536,
        api_key=env.OPENAI_API_KEY,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    @staticmethod
    def extrair_e_salvar_conteudo(id_documento: int) -> None:
        documento = Documento.objects.get(id=id_documento)

        conteudo = ' '.join([
            d.page_content
            for d in PyPDFLoader(documento.arquivo.path, mode='single').load()
        ])

        conteudo = re.sub(r'\s+', ' ', conteudo).strip()

        documento.conteudo = conteudo
        documento.save()

    @staticmethod
    def gerar_e_embedar_chunks(id_documento: int) -> None:
        documento = Documento.objects.get(id=id_documento)
        documento.embeddings.all().delete()

        chunks = Rag.splitter.split_text(documento.conteudo)
        embeddings = Rag.embedding.embed_documents(chunks)

        chunks_documento = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            chunks_documento.append(
                ChunkDocumeto(
                    documento=documento,
                    conteudo=chunk,
                    embedding=embedding,
                )
            )

        ChunkDocumeto.objects.bulk_create(chunks_documento)
        documento.status = StatusDocumento.PROCESSADO
        documento.save()

    @staticmethod
    def top_k_bm25(query: str, k: int) -> QuerySet[ChunkDocumeto]:
        qs = (
            ChunkDocumeto.objects.filter(
                conteudo__bm25=PdbQueryCast(
                    Value('{"match": {"value": "%s"}}' % query)
                ),
            )
            .annotate(score=BM25Score('id'))
            .order_by('-score')[:k]
        )

        return qs

    @staticmethod
    def top_k_similar(query: str, k: int) -> QuerySet[ChunkDocumeto]:
        embedding_query = Rag.embedding.embed_query(query)

        qs = ChunkDocumeto.objects.annotate(
            score=CosineDistance(
                'embedding',
                embedding_query,
            ),
        ).order_by('score')[:k]

        return qs

    @staticmethod
    def top_k_chunks(query: str, k: int = 5) -> list[str]:
        embedding_query = Rag.embedding.embed_query(query)

        bm25_search = '{"match": {"value": "{%s}"}}' % query
        qs = ChunkDocumeto.objects.raw(
            f"""
            WITH bm25_ranked AS (
                SELECT id, RANK() OVER (ORDER BY score DESC) AS rank
                FROM (
                SELECT id, paradedb.score(id) AS score
                FROM ia_chunkdocumeto
                WHERE conteudo @@@ '{bm25_search}'::pdb.query
                ORDER BY paradedb.score(id) DESC
                LIMIT 20
                ) AS bm25_score
            ),
            semantic_search AS (
                SELECT id, RANK() OVER (ORDER BY embedding <=> '{embedding_query}') AS rank
                FROM ia_chunkdocumeto
                ORDER BY embedding <=> '{embedding_query}'
                LIMIT 20
            )
            SELECT
                COALESCE(semantic_search.id, bm25_ranked.id) AS id,
                COALESCE(1.0 / (60 + semantic_search.rank), 0.0) +
                COALESCE(1.0 / (60 + bm25_ranked.rank), 0.0) AS score,
                ia_chunkdocumeto.conteudo,
                ia_chunkdocumeto.embedding
            FROM semantic_search
            FULL OUTER JOIN bm25_ranked ON semantic_search.id = bm25_ranked.id
            JOIN ia_chunkdocumeto ON ia_chunkdocumeto.id = COALESCE(semantic_search.id, bm25_ranked.id)
            ORDER BY score DESC, conteudo
            LIMIT 10;
        """
        )

        return [chunk.conteudo for chunk in qs]

    @staticmethod
    def run(query: str) -> Generator[str, None, None]:
        contexto = '\n\n\n'.join(Rag.top_k_chunks(query, k=10))

        mensagens = [
            SystemMessage('Responda em português.'),
            SystemMessage('Responda utilizando Markdown.'),
            SystemMessage('Adicione emojis quando fizer sentido.'),
            SystemMessage(
                (
                    f'Você é uma IA que auxilia pessoas com informações que estão no contexto. '
                    f'Sua resposta deve se basear **exclusivamente** nas informações do contexto abaixo:'
                    f'\n\n{contexto}\n\n'
                    '⚠️ Regras importantes:\n'
                    '- Se a resposta não estiver clara ou presente no contexto, responda exatamente: "Não tenho informações sobre isso".\n'
                    '- Não invente, não faça suposições e não utiliz    e conhecimento externo ao contexto.\n'
                    '- Antes de responder, verifique cuidadosamente se a informação está no contexto.\n'
                )
            ),
            HumanMessage(query),
        ]

        for resposta in Rag.chat.stream(mensagens):
            yield resposta.content
