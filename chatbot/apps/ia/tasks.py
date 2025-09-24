from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import TokenTextSplitter
from modelos_ia import embedding_model

from ia.models import Documento, DocumentoStatusChoices, EmbeddingDocumento


def gerar_embedding_documento(documento_id: int):
    documento = Documento.objects.get(id=documento_id)
    documento.status = DocumentoStatusChoices.PROCESSANDO
    documento.save()

    text_splitter = TokenTextSplitter(
        chunk_size=512,
        chunk_overlap=256,
    )

    conteudo = PyPDFLoader(documento.arquivo.path, mode='single').load()

    chunks = text_splitter.split_documents(conteudo)
    chunks = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(chunks)

    embeddings = [
        EmbeddingDocumento(
            documento=documento,
            conteudo=chunk,
            embedding=embedding,
        )
        for chunk, embedding in zip(chunks, embeddings, strict=False)
    ]

    documento.embeddings.all().delete()

    EmbeddingDocumento.objects.bulk_create(embeddings)
    documento.status = DocumentoStatusChoices.PROCESSADO
    documento.save()
