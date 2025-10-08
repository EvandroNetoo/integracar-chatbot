from typing import Generator

from core.env import env
from django.db.models import QuerySet, Value
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pgvector.django import CosineDistance

from ia.functions import BM25Score, PdbQueryCast
from ia.models import ChunkDocumeto, Documento, StatusDocumento


class Rag:
    chat = ChatOpenAI(
        model='gpt-4.1-2025-04-14',
        temperature=0.5,
        api_key=env.OPENAI_API_KEY,
    )

    embedding = OpenAIEmbeddings(
        model='text-embedding-3-large',
        dimensions=1024,
        api_key=env.OPENAI_API_KEY,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    @staticmethod
    def extrair_e_salvar_conteudo(id_documento: int) -> None:
        documento = Documento.objects.get(id=id_documento)

        conteudo = ' '.join([
            d.page_content
            for d in PyPDFLoader(documento.arquivo.path, mode='single').load()
        ])

        while '\n' in conteudo:
            conteudo = conteudo.replace('\n', ' ')

        while '  ' in conteudo:
            conteudo = conteudo.replace('  ', ' ')

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
        ).order_by('-score')[:k]

        return qs

    @staticmethod
    def top_k_chunks(query: str, k: int = 5) -> list[str]:
        top_k_bm25 = Rag.top_k_bm25(query, k)
        top_k_similar = Rag.top_k_similar(query, k)

        return [c.conteudo for c in top_k_similar] + [
            c.conteudo for c in top_k_bm25
        ]

    @staticmethod
    def run(query: str) -> Generator[str, None, None]:
        contexto = '\n\n'.join(Rag.top_k_chunks(query, k=10))

        mensagens = [
            SystemMessage('Responda em português.'),
            SystemMessage('Responda utilizando Markdown.'),
            SystemMessage('Adicione emojis quando fizer sentido.'),
            SystemMessage(
                (
                    f'Você é uma IA que auxilia pessoas com informações sobre o genesis as informações sobre ele esta no contexto. '
                    f'Sua resposta deve se basear **exclusivamente** nas informações do contexto abaixo:'
                    f'\n\n{contexto}\n\n'
                    '⚠️ Regras importantes:\n'
                    '- Se a resposta não estiver clara ou presente no contexto, responda exatamente: "Não tenho informações sobre isso".\n'
                    '- Não invente, não faça suposições e não utilize conhecimento externo ao contexto.\n'
                    '- Antes de responder, verifique cuidadosamente se a informação está no contexto.\n'
                )
            ),
            HumanMessage(query),
        ]

        for resposta in Rag.chat.stream(mensagens):
            yield resposta.content
