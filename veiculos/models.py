from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Filial(models.Model):
    nome = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.nome}"
    
    class Meta:
        verbose_name_plural = "Filiais"
        ordering = ['nome']
    
    
class CategoriaVeiculo(models.Model):
    nome = models.CharField(max_length=60, help_text="Exemplo: Sedan, SUV, Picape, Hatch, etc.")

    def __str__(self):
        return f"{self.nome}"
    
    class Meta:
        verbose_name_plural = "Categorias de Veículo"
        ordering = ['nome']
    

class Etapa(models.Model):
    nome = models.CharField(max_length=60)
    sequencia = models.PositiveSmallIntegerField(verbose_name="sequência da etapa", help_text="Informe a sequência da etapa, ex: 1 para leilão final, 2 para feirão, 3 para pré-venda, etc.")
    quantidade_negociacoes = models.PositiveSmallIntegerField(
        verbose_name="quantidade de negociações",
        help_text="Informe quantas negociações acontecem nesta etapa, ex: Leilão final tem 4 negociações."
    )

    def __str__(self):
        return f"{self.nome} ({self.quantidade_negociacoes})"
    

class Vendedor(models.Model):
    nome = models.CharField(max_length=60)
    matricula = models.CharField(
        max_length=100,
        verbose_name="matrícula do vendedor",
        help_text="Informe a matrícula do vendedor, ex: nome#1234"
    )
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT)
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"
    

class Feirao(models.Model):
    nome = models.CharField(max_length=100)
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT)
    data = models.DateField()
    data_limite_propostas = models.DateTimeField(verbose_name="data limite para propostas", help_text="Informe a data limite para envio de propostas, ex: 2024-12-31")
    categorias = models.ManyToManyField(CategoriaVeiculo)
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nome} ({self.data})"
    

class Veiculo(models.Model):
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    ano = models.PositiveSmallIntegerField(verbose_name="ano do veículo")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="valor de tabela")
    categoria = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)
    feirao = models.ForeignKey(Feirao, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.ano})"
    

class Proposta(models.Model):
    nome_equipe = models.CharField(max_length=60, verbose_name="Nome da equipe", help_text="Informe o nome da equipe de vendedores, ex: Equipe Alpha")
    vendedores = models.ManyToManyField(Vendedor)
    feirao = models.ForeignKey(Feirao, on_delete=models.PROTECT)
    categoria = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)
    
    aprovada = models.BooleanField(default=False)
    aprovada_em = models.DateTimeField(null=True, blank=True)

    proposta_em = models.DateTimeField(auto_now_add=True)
    proposta_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        if self.aprovada:
            return f"{self.nome_equipe} - {self.feirao} [✅]"
        else:
            return f"{self.nome_equipe} - {self.feirao} [❌]"
    
    
class Negociacao(models.Model):
    proposta_1 = models.ForeignKey(Proposta, on_delete=models.PROTECT, related_name="proposta_1")
    proposta_2 = models.ForeignKey(Proposta, on_delete=models.PROTECT, related_name="proposta_2")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT)
    data_hora = models.DateTimeField(null=True, blank=True, verbose_name="data e hora da negociação", help_text="Informe a data e hora da negociação, ex: 2024-12-31 18:00")
    etapa = models.ForeignKey(Etapa, on_delete=models.PROTECT)
    categoria = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)
    
    proposta_vencedora = models.ForeignKey(Proposta, on_delete=models.PROTECT, null=True, blank=True, related_name="proposta_vencedora")
    valor_fechado = models.CharField(max_length=30, null=True, blank=True, verbose_name="valor fechado da negociação", help_text="Informe o valor fechado da negociação, ex: R$ 45.000")

    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"Negociação #{self.pk} às {self.data_hora}"