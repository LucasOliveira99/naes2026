import django_filters
from django import forms

from .models import (
    CategoriaVeiculo,
    Etapa,
    Feirao,
    Filial,
    Negociacao,
    Proposta,
    Veiculo,
    Vendedor,
)


class TextoBuscaFilterSet(django_filters.FilterSet):
    busca = django_filters.CharFilter(
        label="Buscar",
        method="filtrar_busca",
        widget=forms.TextInput(
            attrs={"placeholder": "Digite sua busca", "class": "form-control"}
        ),
    )

    def filtrar_busca(self, queryset, name, value):
        raise NotImplementedError


class FilialFilter(TextoBuscaFilterSet):
    class Meta:
        model = Filial
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(nome__icontains=value)


class CategoriaVeiculoFilter(TextoBuscaFilterSet):
    class Meta:
        model = CategoriaVeiculo
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(nome__icontains=value)


class EtapaFilter(TextoBuscaFilterSet):
    class Meta:
        model = Etapa
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(nome__icontains=value)


class VendedorFilter(TextoBuscaFilterSet):
    class Meta:
        model = Vendedor
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            nome__icontains=value
        ) | queryset.filter(
            matricula__icontains=value
        ) | queryset.filter(
            filial__nome__icontains=value
        )


class FeiraoFilter(TextoBuscaFilterSet):
    class Meta:
        model = Feirao
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            nome__icontains=value
        ) | queryset.filter(
            filial__nome__icontains=value
        )


class VeiculoFilter(TextoBuscaFilterSet):
    class Meta:
        model = Veiculo
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            marca__icontains=value
        ) | queryset.filter(
            modelo__icontains=value
        ) | queryset.filter(
            categoria__nome__icontains=value
        ) | queryset.filter(
            feirao__nome__icontains=value
        )


class PropostaFilter(TextoBuscaFilterSet):
    class Meta:
        model = Proposta
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            nome_equipe__icontains=value
        ) | queryset.filter(
            feirao__nome__icontains=value
        ) | queryset.filter(
            categoria__nome__icontains=value
        )


class NegociacaoFilter(TextoBuscaFilterSet):
    class Meta:
        model = Negociacao
        fields = ["busca"]

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            proposta_1__nome_equipe__icontains=value
        ) | queryset.filter(
            proposta_2__nome_equipe__icontains=value
        ) | queryset.filter(
            veiculo__marca__icontains=value
        ) | queryset.filter(
            veiculo__modelo__icontains=value
        ) | queryset.filter(
            etapa__nome__icontains=value
        ) | queryset.filter(
            valor_fechado__icontains=value
        )
