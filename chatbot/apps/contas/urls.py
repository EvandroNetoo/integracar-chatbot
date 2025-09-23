from django.urls import path

from contas.views import LogoutView, SigninView

urlpatterns = [
    path('login/', SigninView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
