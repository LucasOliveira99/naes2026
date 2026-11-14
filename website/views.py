import json
import logging
from django.views.generic import FormView, TemplateView
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from veiculos.models import Feirao

# import timezone do django
from django.utils import timezone

# Reutilizados pela view de alterar senha (evita depender do redirect padrão password_change_done)
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from .forms import CadastroForm, ConfiguracaoIAForm, ConfiguracaoIAUsuarioForm
from .gemini import (
	CotaIAExcedida,
	ConfiguracaoIAInvalida,
	RespostaInvalida,
    get_configuracao_ia,
	limpar_cache_configuracao_ia,
	testar_conexao,
)
from .models import ConfiguracaoIAUsuario, ConsumoIA, ConversaIA, RequisicaoIA
from .services import renderizar_markdown_seguro, responder_chat


logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # pega todos os feirões e conta quantos tem e coloca numa lista no contexto
        todos_feiroes = Feirao.objects.all()
        # conta quantos feirões tem e coloca no contexto o valor inteiro
        context["total_feiroes"] = todos_feiroes.count()
        
        # pega os 5 feirões mais recentes e coloca numa lista no contexto (LIMITE DE 5)
        feiroes = todos_feiroes.order_by("-cadastrado_em")[:5]
        context["ultimos_feiroes"] = feiroes

        # Filtrar pela data "greater than" (data_limite_propostas__gt) a data atual (timezone.now()) para pegar apenas os feirões que ainda estão com propostas abertas
        context["feiroes_abertos"] = todos_feiroes.filter(data_limite_propostas__gt=timezone.now())
        # Contar quantos feirões estão com propostas abertas e colocar no contexto o valor inteiro
        context["total_abertos"] = context["feiroes_abertos"].count()
        

        return context

class ContatoView(TemplateView):
    template_name = "website/contato.html"
    
class SobreView(TemplateView):
    template_name = "website/sobre.html"


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(_is_superuser)
@require_http_methods(["GET", "POST"])
def ConfiguracaoIAView(request):
    config = get_configuracao_ia()
    form = ConfiguracaoIAForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        if not form.cleaned_data.get("api_key"):
            form.instance.api_key = config.api_key
        config = form.save()
        limpar_cache_configuracao_ia()
        if request.POST.get("action") == "testar":
            try:
                testar_conexao(config)
                messages.success(request, "Conexão com o Gemini testada com sucesso.")
            except Exception:
                messages.error(request, "Não foi possível testar a conexão com o Gemini.")
        else:
            messages.success(request, "Configuração da IA salva.")

    return render(request, "website/configuracao_ia.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def GeminiChatView(request):
    conversa = ConversaIA.objects.filter(usuario=request.user).first()
    if request.method == "POST" and request.POST.get("action") == "clear":
        if conversa:
            conversa.delete()
        return redirect("gemini-chat")

    historico = conversa.mensagens if conversa else []
    historico = [
        {
            **mensagem,
            "html": (
                renderizar_markdown_seguro(mensagem["text"])
                if mensagem.get("role") == "model"
                else ""
            ),
        }
        for mensagem in historico
    ]
    return render(request, "website/gemini_chat.html", {
        "history": historico,
        "conversation_id": conversa.pk if conversa else "",
    })


@login_required
@require_http_methods(["POST"])
def GeminiChatAjaxView(request):
    try:
        dados = json.loads(request.body) if request.content_type.startswith("application/json") else request.POST
    except json.JSONDecodeError:
        return JsonResponse({"erro": "O corpo da requisição não é um JSON válido."}, status=400)

    mensagem = str(dados.get("message", "")).strip()
    if not mensagem:
        return JsonResponse({"erro": "Digite uma mensagem antes de enviar."}, status=400)
    if len(mensagem) > 4000:
        return JsonResponse({"erro": "A mensagem deve ter no máximo 4000 caracteres."}, status=400)

    conversation_id = dados.get("conversation_id")
    conversa = None
    if conversation_id:
        try:
            conversa = get_object_or_404(
                ConversaIA,
                pk=int(conversation_id),
                usuario=request.user,
            )
        except (Http404, TypeError, ValueError):
            return JsonResponse({"erro": "A conversa informada é inválida."}, status=400)

    historico = conversa.mensagens if conversa else []
    try:
        response = responder_chat(
            usuario=request.user,
            mensagem=mensagem,
            historico=historico,
        )
        if isinstance(response, RespostaInvalida):
            return JsonResponse(
                {"erro": "O Gemini devolveu uma resposta fora do formato esperado."},
                status=502,
            )
    except CotaIAExcedida:
        return JsonResponse({"erro": "O limite de uso da IA foi atingido."}, status=429)
    except ConfiguracaoIAInvalida:
        return JsonResponse({"erro": "A IA não está configurada para uso."}, status=503)
    except Exception:
        logger.exception("Falha ao responder conversa IA via AJAX")
        return JsonResponse(
            {"erro": "Não foi possível conversar com o Gemini agora. Tente novamente."},
            status=503,
        )

    texto_resposta = response.dados.resposta if response.dados else response.texto
    mensagem_usuario = {"role": "user", "text": mensagem}
    mensagem_modelo = {
        "role": "model",
        "text": texto_resposta,
        "usage": {
            "prompt_token_count": response.tokens_entrada,
            "candidates_token_count": response.tokens_saida,
            "thoughts_token_count": response.tokens_raciocinio,
            "total_token_count": response.tokens_total,
            "model": response.modelo,
            "finish_reason": response.motivo_fim,
        },
    }
    if conversa is None:
        conversa = ConversaIA.objects.create(
            usuario=request.user,
            mensagens=[mensagem_usuario, mensagem_modelo],
        )
    else:
        conversa.mensagens = [*historico, mensagem_usuario, mensagem_modelo]
        conversa.save(update_fields=["mensagens", "atualizada_em"])

    return JsonResponse({
        "conversation_id": conversa.pk,
        "message": mensagem_modelo,
        "html": renderizar_markdown_seguro(texto_resposta),
    })


@user_passes_test(_is_superuser)
def RequisicoesIAView(request):
    requisicoes = RequisicaoIA.objects.select_related("usuario").all()
    if request.GET.get("usuario"):
        requisicoes = requisicoes.filter(usuario__username__icontains=request.GET["usuario"])
    if request.GET.get("situacao"):
        requisicoes = requisicoes.filter(situacao=request.GET["situacao"])
    if request.GET.get("finalidade"):
        requisicoes = requisicoes.filter(finalidade=request.GET["finalidade"])
    if request.GET.get("de"):
        requisicoes = requisicoes.filter(criada_em__date__gte=request.GET["de"])
    if request.GET.get("ate"):
        requisicoes = requisicoes.filter(criada_em__date__lte=request.GET["ate"])
    resumo = (
        ConsumoIA.objects.filter(mes=_mes_atual_sao_paulo())
        .values("usuario__username")
        .annotate(tokens=Sum("tokens_total"))
        .order_by("-tokens")[:10]
    )
    return render(request, "website/requisicoes_ia.html", {
        "requisicoes": requisicoes[:200],
        "resumo": resumo,
        "situacoes": RequisicaoIA.SITUACAO_CHOICES,
        "filtros": request.GET,
    })


@user_passes_test(_is_superuser)
def RequisicaoIADetailView(request, pk):
    requisicao = get_object_or_404(RequisicaoIA.objects.select_related("usuario"), pk=pk)
    return render(request, "website/requisicao_ia_detail.html", {"requisicao": requisicao})


def _mes_atual_sao_paulo():
    from zoneinfo import ZoneInfo
    agora = timezone.localtime(timezone.now(), ZoneInfo("America/Sao_Paulo"))
    return agora.date().replace(day=1)


@login_required
def MeuConsumoIAView(request):
    mes = _mes_atual_sao_paulo()
    consumo = ConsumoIA.objects.filter(usuario=request.user, mes=mes).first()
    config = get_configuracao_ia()
    excecao = ConfiguracaoIAUsuario.objects.filter(usuario=request.user).first()
    limite = excecao.limite_tokens if excecao and excecao.limite_tokens is not None else config.limite_tokens_padrao
    usado = consumo.tokens_total if consumo else 0
    proximo_mes = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
    ultimas = RequisicaoIA.objects.filter(usuario=request.user).order_by("-criada_em")[:10]
    return render(request, "website/meu_consumo_ia.html", {
        "consumo": consumo,
        "limite": limite,
        "usado": usado,
        "restante": max(0, limite - usado),
        "percentual": min(100, round(usado * 100 / limite)) if limite else 100,
        "renova_em": proximo_mes,
        "ultimas": ultimas,
        "ia_ligada": not excecao or excecao.ia_ligada,
    })


@user_passes_test(_is_superuser)
@require_http_methods(["GET", "POST"])
def ConfiguracaoIAUsuariosView(request):
    User = get_user_model()
    selecionado = request.GET.get("usuario") or request.POST.get("usuario_id")
    usuario = get_object_or_404(User, pk=selecionado) if selecionado else None
    if request.method == "POST" and usuario:
        if request.POST.get("action") == "resetar":
            ConfiguracaoIAUsuario.objects.filter(usuario=usuario).delete()
            messages.success(request, "O usuário voltou a usar o limite padrão.")
        else:
            form = ConfiguracaoIAUsuarioForm(request.POST, instance=ConfiguracaoIAUsuario.objects.filter(usuario=usuario).first())
            if form.is_valid():
                form.save()
                messages.success(request, "Exceção de IA salva.")
    form = ConfiguracaoIAUsuarioForm(instance=ConfiguracaoIAUsuario.objects.filter(usuario=usuario).first()) if usuario else None
    usuarios = User.objects.order_by("username")
    linhas = []
    mes = _mes_atual_sao_paulo()
    config = get_configuracao_ia()
    for item in usuarios:
        excecao = ConfiguracaoIAUsuario.objects.filter(usuario=item).first()
        consumo = ConsumoIA.objects.filter(usuario=item, mes=mes).first()
        linhas.append({"usuario": item, "excecao": excecao, "consumo": consumo, "limite": excecao.limite_tokens if excecao and excecao.limite_tokens is not None else config.limite_tokens_padrao})
    return render(request, "website/configuracao_ia_usuarios.html", {"usuarios": linhas, "usuario": usuario, "form": form})


class CadastroView(FormView):
    template_name = "website/cadastro.html"
    form_class = CadastroForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AlterarSenhaView(SuccessMessageMixin, PasswordChangeView):
    template_name = "veiculos/form.html"
    success_url = reverse_lazy("index")
    success_message = "Senha alterada com sucesso!"
    extra_context = {
        'titulo': 'Alterar minha senha',
        'botao': 'Alterar Senha'
    }