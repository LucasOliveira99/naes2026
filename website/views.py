from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from veiculos.models import Feirao

from .forms import CadastroForm


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos_feiroes = Feirao.objects.all()
        context["total_feiroes"] = todos_feiroes.count()
        context["ultimos_feiroes"] = todos_feiroes.order_by("-cadastrado_em")[:5]
        context["feiroes_abertos"] = todos_feiroes.filter(
            data_limite_propostas__gt=timezone.now()
        )
        context["total_abertos"] = context["feiroes_abertos"].count()
        return context


class ContatoView(TemplateView):
    template_name = "website/contato.html"


class SobreView(TemplateView):
    template_name = "website/sobre.html"


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
        "titulo": "Alterar minha senha",
        "botao": "Alterar Senha",
    }
