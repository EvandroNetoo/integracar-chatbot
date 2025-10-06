from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_htmx.http import HttpResponseClientRefresh
from langchain_core.messages import HumanMessage, SystemMessage
from modelos_ia import chat_model, embedding_model
from pgvector.django import CosineDistance

from ia.forms import ImportarDocumentosForm
from ia.models import Documento, DocumentoStatusChoices, EmbeddingDocumento


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def get(self, request: HttpRequest):
        return render(request, 'ia/chat.html')

    def post(self, request: HttpRequest):
        mensagem = request.POST.get('mensagem', '')
        stream = request.POST.get('stream', '')

        if not mensagem:
            return JsonResponse({'resposta': 'Mensagem vazia'}, status=400)

        embedding_mensagem = embedding_model.embed_query(mensagem)

        documentos_relevantes = EmbeddingDocumento.objects.order_by(
            CosineDistance('embedding', embedding_mensagem)
        )[:5]

        contexto = '\n\n'.join([doc.conteudo for doc in documentos_relevantes])

        # 4. Montar a lista de mensagens
        mensagens = [
            SystemMessage('Responda em português.'),
            SystemMessage('Responda utilizando Markdown.'),
            SystemMessage('Adicione emojis quando fizer sentido.'),
            SystemMessage(
                (
                    f'Você é uma IA que auxilia pessoas responsáveis pelo CAR no Espírito Santo. '
                    f'Sua resposta deve se basear **exclusivamente** nas informações do contexto abaixo:'
                    f'\n\n{contexto}\n\n'
                    '⚠️ Regras importantes:\n'
                    '- Se a resposta não estiver clara ou presente no contexto, responda exatamente: "Não tenho informações sobre isso".\n'
                    '- Não invente, não faça suposições e não utilize conhecimento externo ao contexto.\n'
                    '- Antes de responder, verifique cuidadosamente se a informação está no contexto.\n'
                )
            ),
            HumanMessage(mensagem),
        ]

        if not stream:
            resposta = chat_model.invoke(mensagens).content
            return JsonResponse({'resposta': resposta})

        def funcao_stream():
            for resposta in chat_model.stream(mensagens):
                yield resposta.content

        return StreamingHttpResponse(funcao_stream())


@method_decorator(login_required, name='dispatch')
class DocumentosView(View):
    template_name = 'ia/documentos.html'

    def get(self, request: HttpRequest):
        documentos = Documento.objects.all()

        documentos_processados = documentos.filter(
            status=DocumentoStatusChoices.PROCESSADO
        ).count()

        documentos_pendentes = documentos.filter(
            status__in=[
                DocumentoStatusChoices.PENDENTE,
                DocumentoStatusChoices.PROCESSANDO,
            ]
        ).count()

        context = {
            'importar_documentos_form': ImportarDocumentosForm(),
            'documentos': documentos,
            'documentos_processados': documentos_processados,
            'documentos_pendentes': documentos_pendentes,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ImportarDocumentosView(View):
    form_class = ImportarDocumentosForm

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'components/form.html', context)

        form.save()

        return HttpResponseClientRefresh()
