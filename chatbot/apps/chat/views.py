from ai_models import chat_model
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from langchain_core.messages import HumanMessage, SystemMessage


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def get(self, request: HttpRequest):
        return render(request, 'chat/chat.html')

    def post(self, request: HttpRequest):
        mensagem = request.POST.get('mensagem', '')
        stream = request.POST.get('stream', '')

        if not mensagem:
            return JsonResponse({'resposta': 'Mensagem vazia'}, status=400)

        mensages = [
            SystemMessage('Você é um assistente útil.'),
            SystemMessage('Responda em português.'),
            SystemMessage('Responda utilizando a lingagem Markdown.'),
            SystemMessage('Utilize emojis.'),
            HumanMessage(mensagem),
        ]

        if not stream:
            resposta = chat_model.invoke(mensages).content
            return JsonResponse({'resposta': resposta})

        def funcao_stream():
            for resposta in chat_model.stream(mensages):
                yield resposta.content

        return StreamingHttpResponse(funcao_stream())
