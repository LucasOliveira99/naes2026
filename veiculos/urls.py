
from django.urls import path
from .views import (
    FilialCreate, FilialUpdate, FilialDelete, FilialList, FilialDetail,
    CategoriaCreate, CategoriaUpdate, CategoriaDelete, CategoriaList, CategoriaDetail,
    EtapaCreate, EtapaUpdate, EtapaDelete, EtapaList, EtapaDetail,
    VendedorCreate, VendedorUpdate, VendedorDelete, VendedorList, VendedorDetail,
    FeiraoCreate, FeiraoUpdate, FeiraoDelete, FeiraoList, FeiraoDetail,
    VeiculoCreate, VeiculoUpdate, VeiculoDelete, VeiculoList, VeiculoDetail,
    PropostaCreate, PropostaUpdate, PropostaDelete, PropostaList, PropostaDetail,
    NegociacaoCreate, NegociacaoUpdate, NegociacaoDelete, NegociacaoList, NegociacaoDetail,
)


urlpatterns = [
    path('cadastrar/filial/', FilialCreate.as_view(), name='filial-create'),
    path('atualizar/filial/<int:pk>/', FilialUpdate.as_view(), name='filial-update'),
    path('excluir/filial/<int:pk>/', FilialDelete.as_view(), name='filial-delete'),
    path('listar/filial/', FilialList.as_view(), name='filial-list'),
    path('detalhar/filial/<int:pk>/', FilialDetail.as_view(), name='filial-detail'),

    path('cadastrar/categoria/', CategoriaCreate.as_view(), name='categoria-create'),
    path('atualizar/categoria/<int:pk>/', CategoriaUpdate.as_view(), name='categoria-update'),
    path('excluir/categoria/<int:pk>/', CategoriaDelete.as_view(), name='categoria-delete'),
    path('listar/categoria/', CategoriaList.as_view(), name='categoria-list'),
    path('detalhar/categoria/<int:pk>/', CategoriaDetail.as_view(), name='categoria-detail'),

    path('cadastrar/etapa/', EtapaCreate.as_view(), name='etapa-create'),
    path('atualizar/etapa/<int:pk>/', EtapaUpdate.as_view(), name='etapa-update'),
    path('excluir/etapa/<int:pk>/', EtapaDelete.as_view(), name='etapa-delete'),
    path('listar/etapa/', EtapaList.as_view(), name='etapa-list'),
    path('detalhar/etapa/<int:pk>/', EtapaDetail.as_view(), name='etapa-detail'),

    path('cadastrar/vendedor/', VendedorCreate.as_view(), name='vendedor-create'),
    path('atualizar/vendedor/<int:pk>/', VendedorUpdate.as_view(), name='vendedor-update'),
    path('excluir/vendedor/<int:pk>/', VendedorDelete.as_view(), name='vendedor-delete'),
    path('listar/vendedor/', VendedorList.as_view(), name='vendedor-list'),
    path('detalhar/vendedor/<int:pk>/', VendedorDetail.as_view(), name='vendedor-detail'),
    
    path('cadastrar/feirao/', FeiraoCreate.as_view(), name='feirao-create'),
    path('atualizar/feirao/<int:pk>/', FeiraoUpdate.as_view(), name='feirao-update'),
    path('excluir/feirao/<int:pk>/', FeiraoDelete.as_view(), name='feirao-delete'),
    path('listar/feirao/', FeiraoList.as_view(), name='feirao-list'),
    path('detalhar/feirao/<int:pk>/', FeiraoDetail.as_view(), name='feirao-detail'),

    path('cadastrar/veiculo/', VeiculoCreate.as_view(), name='veiculo-create'),
    path('atualizar/veiculo/<int:pk>/', VeiculoUpdate.as_view(), name='veiculo-update'),
    path('excluir/veiculo/<int:pk>/', VeiculoDelete.as_view(), name='veiculo-delete'),
    path('listar/veiculo/', VeiculoList.as_view(), name='veiculo-list'),
    path('detalhar/veiculo/<int:pk>/', VeiculoDetail.as_view(), name='veiculo-detail'),

    path('cadastrar/proposta/', PropostaCreate.as_view(), name='proposta-create'),
    path('atualizar/proposta/<int:pk>/', PropostaUpdate.as_view(), name='proposta-update'),
    path('excluir/proposta/<int:pk>/', PropostaDelete.as_view(), name='proposta-delete'),
    path('listar/proposta/', PropostaList.as_view(), name='proposta-list'),
    path('detalhar/proposta/<int:pk>/', PropostaDetail.as_view(), name='proposta-detail'),

    path('cadastrar/negociacao/', NegociacaoCreate.as_view(), name='negociacao-create'),
    path('atualizar/negociacao/<int:pk>/', NegociacaoUpdate.as_view(), name='negociacao-update'),
    path('excluir/negociacao/<int:pk>/', NegociacaoDelete.as_view(), name='negociacao-delete'),
    path('listar/negociacao/', NegociacaoList.as_view(), name='negociacao-list'),
    path('detalhar/negociacao/<int:pk>/', NegociacaoDetail.as_view(), name='negociacao-detail'),
]
