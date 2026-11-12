from django.views.generic import FormView, TemplateView
from veiculos.models import Feirao

# import timezone do django
from django.utils import timezone

# Reutilizados pela view de alterar senha (evita depender do redirect padrão password_change_done)
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from .forms import CadastroForm


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