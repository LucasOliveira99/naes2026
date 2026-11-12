from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

# Buscar a rota da url pelo name dela (urls.py)
from django.urls import reverse_lazy

from .models import Filial, Vendedor, CategoriaVeiculo, Etapa, Feirao, Veiculo, Proposta, Negociacao

# Importar o BaseLoginMixin para proteger as views
from django.contrib.auth.mixins import LoginRequiredMixin

# Django braces faz o GroupRequiredMixin para controle de acesso por Grupo
from braces.views import GroupRequiredMixin


# Criar um mixin para proteger as views de cadastro, edição e exclusão
class BaseLoginMixin(LoginRequiredMixin):
    # define o redirecionamento caso o usuário não esteja autenticado ao acessar a view
    login_url = reverse_lazy('login')  


class FilialCreate(GroupRequiredMixin, CreateView):
    group_required = ['Administrador']
    model = Filial
    fields = ['nome']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('filial-list')
    extra_context = {
        'titulo': 'Cadastro de Filial',
        'botao': 'Criar Filial'
    }


class FilialUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']
    model = Filial
    fields = ['nome']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('filial-list')
    extra_context = {
        'titulo': 'Editar dados da Filial',
        'botao': 'Atualizar Filial'
    }


class FilialDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador']
    model = Filial
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('filial-list')
    extra_context = {
        'titulo': 'Excluir Filial',
        'botao': 'Sim, excluir!'
    }


class FilialList(BaseLoginMixin, ListView):
    model = Filial
    template_name = 'veiculos/list/filial.html'
    paginate_by = 30


class FilialDetail(BaseLoginMixin, DetailView):
    model = Filial
    template_name = 'veiculos/detail/filial.html'



#########################################################


class CategoriaCreate(GroupRequiredMixin, CreateView):
    group_required = ['Administrador']
    model = CategoriaVeiculo
    fields = ['nome']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Cadastro de Categoria',
        'botao': 'Criar Categoria'
    }


class CategoriaUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']
    model = CategoriaVeiculo
    fields = ['nome']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Editar dados da Categoria',
        'botao': 'Atualizar Categoria'
    }


class CategoriaDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador']
    model = CategoriaVeiculo
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }


class CategoriaList(BaseLoginMixin, ListView):
    model = CategoriaVeiculo
    template_name = 'veiculos/list/categoria.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_categorias"] = self.get_queryset().count()
        return context


class CategoriaDetail(BaseLoginMixin, DetailView):
    model = CategoriaVeiculo
    template_name = 'veiculos/detail/categoria.html'

#########################################################


class EtapaCreate(GroupRequiredMixin, CreateView):
    group_required = ['Administrador']
    model = Etapa
    fields = ['nome', 'sequencia', 'quantidade_negociacoes']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('etapa-list')
    extra_context = {
        'titulo': 'Cadastro de Etapa',
        'botao': 'Criar Etapa',
        'largura': 8
    }


class EtapaUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador']
    model = Etapa
    fields = ['nome', 'sequencia', 'quantidade_negociacoes']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('etapa-list')
    extra_context = {
        'titulo': 'Editar dados da Etapa',
        'botao': 'Atualizar Etapa'
    }


class EtapaDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador']
    model = Etapa
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('etapa-list')
    extra_context = {
        'titulo': 'Excluir Etapa',
        'botao': 'Sim, excluir!'
    }


class EtapaList(GroupRequiredMixin, ListView):
    group_required = ['Administrador']
    model = Etapa
    template_name = 'veiculos/list/etapa.html'
    paginate_by = 30


class EtapaDetail(GroupRequiredMixin, DetailView):
    group_required = ['Administrador']
    model = Etapa
    template_name = 'veiculos/detail/etapa.html'


class VendedorCreate(BaseLoginMixin, CreateView):
    model = Vendedor
    fields = ['nome', 'matricula', 'filial', 'usuario']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('vendedor-list')
    extra_context = {
        'titulo': 'Cadastro de Vendedor',
        'botao': 'Criar Vendedor'
    }


class VendedorUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador', 'Organização']
    model = Vendedor
    fields = ['nome', 'matricula', 'filial', 'usuario']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('vendedor-list')
    extra_context = {
        'titulo': 'Editar dados do Vendedor',
        'botao': 'Atualizar Vendedor'
    }


class VendedorDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador']
    model = Vendedor
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('vendedor-list')
    extra_context = {
        'titulo': 'Excluir Vendedor',
        'botao': 'Sim, excluir!'
    }


class VendedorList(GroupRequiredMixin, ListView):
    group_required = ['Administrador', 'Organização']
    model = Vendedor
    template_name = 'veiculos/list/vendedor.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('filial')


class VendedorDetail(GroupRequiredMixin, DetailView):
    group_required = ['Administrador', 'Organização']
    model = Vendedor
    template_name = 'veiculos/detail/vendedor.html'

##########################################################


class FeiraoCreate(GroupRequiredMixin, CreateView):
    group_required = ['Administrador', 'Organização']
    model = Feirao
    fields = ['nome', 'filial', 'data', 'data_limite_propostas', 'categorias']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('feirao-list')
    extra_context = {
        'titulo': 'Cadastro de Feirão',
        'botao': 'Criar Feirão'
    }

    def get_success_url(self):
        # Redirecionar para a página de detalhes do feirão criado passando seu pk/id na url
        return reverse_lazy('feirao-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Atribuir o usuário logado ao campo 'cadastrado_por' antes de salvar o formulário
        form.instance.cadastrado_por = self.request.user
        
        # Executa a criação do objeto e faz o INSERT no banco
        url_sucesso = super().form_valid(form)

        return url_sucesso


class FeiraoUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador', 'Organização']
    model = Feirao
    fields = ['nome', 'filial', 'data', 'data_limite_propostas', 'categorias', 'cadastrado_por']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('feirao-list')
    extra_context = {
        'titulo': 'Editar dados do Feirão',
        'botao': 'Atualizar Feirão'
    }

    # queryset é uma consulta personalizada para filtrar os objetos que podem ser editados
    def get_queryset(self):
        return super().get_queryset().filter(cadastrado_por=self.request.user)


class FeiraoDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador']
    model = Feirao
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('feirao-list')
    extra_context = {
        'titulo': 'Excluir Feirão',
        'botao': 'Sim, excluir!'
    }

    def get_queryset(self):
        return super().get_queryset().filter(cadastrado_por=self.request.user)


class FeiraoList(BaseLoginMixin, ListView):
    model = Feirao
    template_name = 'veiculos/list/feirao.html'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(cadastrado_por=self.request.user)
        qs = qs.select_related('filial')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_feiroes"] = Feirao.objects.all().count()
        context["total_filtrado"] = self.get_queryset().count()
        return context

class FeiraoDetail(DetailView):
    model = Feirao
    template_name = 'veiculos/detail/feirao.html'


##########################################################


class VeiculoCreate(BaseLoginMixin, CreateView):
    model = Veiculo
    fields = ['marca', 'modelo', 'ano', 'valor', 'categoria', 'feirao']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('veiculo-list')
    extra_context = {
        'titulo': 'Cadastro de Veículo',
        'botao': 'Criar Veículo'
    }


class VeiculoUpdate(BaseLoginMixin, UpdateView):
    model = Veiculo
    fields = ['marca', 'modelo', 'ano', 'valor', 'categoria', 'feirao']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('veiculo-list')
    extra_context = {
        'titulo': 'Editar dados do Veículo',
        'botao': 'Atualizar Veículo'
    }


class VeiculoDelete(BaseLoginMixin, DeleteView):
    model = Veiculo
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('veiculo-list')
    extra_context = {
        'titulo': 'Excluir Veículo',
        'botao': 'Sim, excluir!'
    }


class VeiculoList(BaseLoginMixin, ListView):
    model = Veiculo
    template_name = 'veiculos/list/veiculo.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('categoria', 'feirao')


class VeiculoDetail(BaseLoginMixin, DetailView):
    model = Veiculo
    template_name = 'veiculos/detail/veiculo.html'


class PropostaCreate(BaseLoginMixin, CreateView):
    model = Proposta
    fields = ['nome_equipe', 'vendedores', 'feirao', 'categoria', 'proposta_por']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('proposta-list')
    extra_context = {
        'titulo': 'Cadastro de Proposta',
        'botao': 'Criar Proposta'
    }


class PropostaUpdate(BaseLoginMixin, UpdateView):
    model = Proposta
    fields = ['nome_equipe', 'vendedores', 'feirao', 'categoria', 'aprovada', 'aprovada_em', 'proposta_por']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('proposta-list')
    extra_context = {
        'titulo': 'Editar dados da Proposta',
        'botao': 'Atualizar Proposta'
    }


class PropostaDelete(BaseLoginMixin, DeleteView):
    model = Proposta
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('proposta-list')
    extra_context = {
        'titulo': 'Excluir Proposta',
        'botao': 'Sim, excluir!'
    }


class PropostaList(BaseLoginMixin, ListView):
    model = Proposta
    template_name = 'veiculos/list/proposta.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('feirao', 'categoria')


class PropostaDetail(BaseLoginMixin, DetailView):
    model = Proposta
    template_name = 'veiculos/detail/proposta.html'


class NegociacaoCreate(GroupRequiredMixin, CreateView):
    group_required = ['Administrador', 'Organização']
    model = Negociacao
    fields = ['proposta_1', 'proposta_2', 'veiculo', 'data_hora', 'etapa', 'categoria', 'proposta_vencedora', 'valor_fechado', 'cadastrado_por']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('negociacao-list')
    extra_context = {
        'titulo': 'Cadastro de Negociação',
        'botao': 'Criar Negociação'
    }


class NegociacaoUpdate(GroupRequiredMixin, UpdateView):
    group_required = ['Administrador', 'Organização']
    model = Negociacao
    fields = ['proposta_1', 'proposta_2', 'veiculo', 'data_hora', 'etapa', 'categoria', 'proposta_vencedora', 'valor_fechado', 'cadastrado_por']
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('negociacao-list')
    extra_context = {
        'titulo': 'Editar dados da Negociação',
        'botao': 'Atualizar Negociação'
    }


class NegociacaoDelete(GroupRequiredMixin, DeleteView):
    group_required = ['Administrador', 'Organização']
    model = Negociacao
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('negociacao-list')
    extra_context = {
        'titulo': 'Excluir Negociação',
        'botao': 'Sim, excluir!'
    }


class NegociacaoList(ListView):
    model = Negociacao
    template_name = 'veiculos/list/negociacao.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related(
            'proposta_1', 'proposta_2', 'etapa', 'veiculo'
        )

class NegociacaoDetail(DetailView):
    model = Negociacao
    template_name = 'veiculos/detail/negociacao.html'
