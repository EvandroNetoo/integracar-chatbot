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
        return render(request, 'ia/chat.html')

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
