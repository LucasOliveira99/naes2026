
from django.urls import path
from .views import CadastroView, IndexView, ContatoView, SobreView, AlterarSenhaView

# Importas as views para gerenciamento de usuários
from django.contrib.auth.views import (
    LoginView,
    LogoutView, 
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("sobre/", SobreView.as_view(), name="sobre"),
    path("cadastro/", CadastroView.as_view(), name="cadastro"),
    
    # URL para login e usuários reutiliza o meu template de form e recebe o texto do titulo e botão
    path("login/", LoginView.as_view(
            template_name="veiculos/form.html",
            extra_context = {
                'titulo': 'Autenticação de Usuário',
                'botao': 'Entrar'
            }
        ), name="login"),

    # a URL de logout não precisa de template
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # AlterarSenhaView tem success_url próprio, evitando o redirect padrão para password_change_done
    path("alterar-senha/", AlterarSenhaView.as_view(), name="alterar-senha"),
]
