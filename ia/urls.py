from django.urls import path

from .views import (
    ConfiguracaoIAUsuariosView,
    ConfiguracaoIAView,
    GeminiChatClearView,
    GeminiChatAjaxView,
    GeminiChatView,
    MeuConsumoIAView,
    RequisicaoIADetailView,
    RequisicoesIAView,
)


urlpatterns = [
    path("gemini/", GeminiChatView, name="gemini-chat"),
    path("gemini/limpar/", GeminiChatClearView, name="gemini-chat-clear"),
    path("gemini/api/", GeminiChatAjaxView, name="gemini-chat-api"),
    path("configuracao-ia/", ConfiguracaoIAView, name="configuracao-ia"),
    path(
        "configuracao-ia/usuarios/",
        ConfiguracaoIAUsuariosView,
        name="configuracao-ia-usuarios",
    ),
    path("ia/requisicoes/", RequisicoesIAView, name="requisicoes-ia"),
    path(
        "ia/requisicoes/<int:pk>/",
        RequisicaoIADetailView,
        name="requisicao-ia-detail",
    ),
    path("ia/meu-consumo/", MeuConsumoIAView, name="meu-consumo-ia"),
]
