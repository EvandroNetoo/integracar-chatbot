from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from contas.forms import SigninForm


class SigninView(View):
    template_name = 'contas/login.html'
    form_class = SigninForm

    def get(self, request: HttpRequest):
        context = {
            'form': self.form_class(),
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest):
        form = self.form_class(request, request.POST)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

        login(request, form.get_user())

        redirect_url = request.GET.get('next', '') or reverse('chat')
        return redirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def post(self, request: HttpRequest):
        logout(request)
        return redirect('login')
