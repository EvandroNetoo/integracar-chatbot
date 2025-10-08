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

from ia.forms import ImportarDocumentosForm
from ia.models import Documento, StatusDocumento
from ia.rag import Rag


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def get(self, request: HttpRequest):
        # q = (
        #     ChunkDocumeto.objects.filter(
        #         conteudo__bm25=PdbQueryCast(Value('{"match": {"value": "Jaimel"}}')))
        #     .annotate(score=BM25Score('id'))
        #     .order_by('-score')
        # )
        return render(request, 'ia/chat.html')

    # def post(self, request: HttpRequest):
    #     mensagem = request.POST.get('mensagem', '')
    #     stream = request.POST.get('stream', '')

    #     if not mensagem:
    #         return JsonResponse({'resposta': 'Mensagem vazia'}, status=400)

    #     embedding_mensagem = embedding_model.embed_query(mensagem)

    #     documentos_relevantes = ChunkDocumeto.objects.annotate(
    #         score=L2Distance(
    #             'embedding',
    #             embedding_mensagem,
    #         ),
    #     ).order_by('-score')[:5]

    #     print('Documentos relevantes:')
    #     for doc in documentos_relevantes:
    #         print(f'- Score: {doc.score}, Conteúdo: {doc.conteudo[:30]}')

    #     contexto = '\n\n'.join([doc.conteudo for doc in documentos_relevantes])

    #     # 4. Montar a lista de mensagens
    #     mensagens = [
    #         SystemMessage('Responda em português.'),
    #         SystemMessage('Responda utilizando Markdown.'),
    #         SystemMessage('Adicione emojis quando fizer sentido.'),
    #         SystemMessage(
    #             (
    #                 f'Você é uma IA que auxilia pessoas responsáveis pelo CAR no Espírito Santo. '
    #                 f'Sua resposta deve se basear **exclusivamente** nas informações do contexto abaixo:'
    #                 f'\n\n{contexto}\n\n'
    #                 '⚠️ Regras importantes:\n'
    #                 '- Se a resposta não estiver clara ou presente no contexto, responda exatamente: "Não tenho informações sobre isso".\n'
    #                 '- Não invente, não faça suposições e não utilize conhecimento externo ao contexto.\n'
    #                 '- Antes de responder, verifique cuidadosamente se a informação está no contexto.\n'
    #             )
    #         ),
    #         HumanMessage(mensagem),
    #     ]

    #     if not stream:
    #         resposta = chat_model.invoke(mensagens).content
    #         return JsonResponse({'resposta': resposta})

    #     def funcao_stream():
    #         for resposta in chat_model.stream(mensagens):
    #             yield resposta.content

    #     return StreamingHttpResponse(funcao_stream())

    def post(self, request: HttpRequest):
        mensagem = request.POST.get('mensagem', '')
        stream = request.POST.get('stream', '')

        if not mensagem:
            return JsonResponse({'resposta': 'Mensagem vazia'}, status=400)

        resposta = Rag.run(mensagem)

        if not stream:
            resposta = ''.join(resposta)
            return JsonResponse({'resposta': resposta})

        return StreamingHttpResponse(resposta)


@method_decorator(login_required, name='dispatch')
class DocumentosView(View):
    template_name = 'ia/documentos.html'

    def get(self, request: HttpRequest):
        documentos = Documento.objects.all()

        documentos_processados = documentos.filter(
            status=StatusDocumento.PROCESSADO
        ).count()

        documentos_pendentes = documentos.filter(
            status__in=[
                StatusDocumento.PENDENTE,
                StatusDocumento.PROCESSANDO,
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
