from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RequisicaoIA(models.Model):
	SITUACAO_INICIADA = "iniciada"
	SITUACAO_SUCESSO = "sucesso"
	SITUACAO_ERRO_TEMPORARIO = "erro_temporario"
	SITUACAO_INVALIDA = "resposta_invalida"
	SITUACAO_COTA = "cota"
	SITUACAO_CONFIGURACAO = "configuracao"
	SITUACAO_CHOICES = (
		(SITUACAO_INICIADA, "Iniciada"),
		(SITUACAO_SUCESSO, "Sucesso"),
		(SITUACAO_ERRO_TEMPORARIO, "Erro temporário"),
		(SITUACAO_INVALIDA, "Resposta inválida"),
		(SITUACAO_COTA, "Cota"),
		(SITUACAO_CONFIGURACAO, "Configuração"),
	)

	criada_em = models.DateTimeField(auto_now_add=True)
	finalidade = models.CharField(max_length=80)
	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="requisicoes_ia",
	)
	origem = models.CharField(max_length=40)
	referencia_tipo = models.ForeignKey(
		ContentType,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name="requisicoes_ia_referenciadas",
	)
	referencia_id = models.CharField(max_length=100, blank=True)
	referencia = GenericForeignKey("referencia_tipo", "referencia_id")
	provedor = models.CharField(max_length=50, default="google-gemini")
	modelo = models.CharField(max_length=120, blank=True)
	versao_prompt = models.CharField(max_length=40)
	situacao = models.CharField(
		max_length=24,
		choices=SITUACAO_CHOICES,
		default=SITUACAO_INICIADA,
	)
	tentativa = models.PositiveIntegerField(default=1)
	motivo_fim = models.CharField(max_length=40, blank=True)
	tokens_entrada = models.PositiveIntegerField(default=0)
	tokens_saida = models.PositiveIntegerField(default=0)
	tokens_raciocinio = models.PositiveIntegerField(default=0)
	tokens_total = models.PositiveIntegerField(default=0)
	custo_estimado = models.DecimalField(
		max_digits=12,
		decimal_places=8,
		null=True,
		blank=True,
	)
	duracao_ms = models.PositiveIntegerField(null=True, blank=True)
	resposta = models.TextField(blank=True)
	erro = models.TextField(blank=True)
	texto_hash = models.CharField(max_length=64, blank=True)
	arquivo_mime = models.CharField(max_length=255, blank=True)
	arquivo_tamanho = models.PositiveBigIntegerField(null=True, blank=True)
	arquivo_hash = models.CharField(max_length=64, blank=True)

	class Meta:
		ordering = ["-criada_em"]
		indexes = [
			models.Index(fields=["usuario", "-criada_em"]),
			models.Index(fields=["situacao", "-criada_em"]),
			models.Index(fields=["referencia_tipo", "referencia_id", "-criada_em"]),
		]


class ConfiguracaoIA(models.Model):
	ACESSO_API_KEY = "api_key"
	ACESSO_ENTERPRISE = "enterprise"
	ACESSO_CHOICES = (
		(ACESSO_API_KEY, "API Key"),
		(ACESSO_ENTERPRISE, "Enterprise"),
	)

	acesso = models.CharField(max_length=20, choices=ACESSO_CHOICES, default=ACESSO_API_KEY)
	api_key = models.CharField(max_length=255, blank=True)
	projeto_gcp = models.CharField(max_length=150, blank=True)
	regiao = models.CharField(max_length=50, default="global")
	provedor = models.CharField(max_length=50, default="google-gemini")
	modelo = models.CharField(max_length=120, default="gemini-3.5-flash-lite")
	temperatura = models.DecimalField(max_digits=3, decimal_places=2, default=0.2)
	max_output_tokens = models.PositiveIntegerField(default=2048)
	nivel_raciocinio = models.CharField(max_length=20, default="minimal")
	tentativas = models.PositiveSmallIntegerField(default=1)
	timeout_segundos = models.PositiveIntegerField(default=60)
	limite_tokens_padrao = models.PositiveIntegerField(default=100000)
	aviso_percentual = models.PositiveSmallIntegerField(default=80)
	reserva_minima_tokens = models.PositiveIntegerField(default=5000)
	teto_mensal_sistema = models.PositiveIntegerField(default=20000000)
	max_arquivo_bytes = models.PositiveBigIntegerField(default=10485760)
	max_paginas_pdf = models.PositiveIntegerField(default=20)
	retencao_dias = models.PositiveIntegerField(default=60)
	preco_entrada_milhao = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
	preco_saida_milhao = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
	atualizada_em = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.pk = 1
		super().save(*args, **kwargs)

	def __str__(self):
		return "Configuração da IA"


class ConfiguracaoIAUsuario(models.Model):
	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="configuracao_ia",
	)
	ia_ligada = models.BooleanField(default=True)
	limite_tokens = models.PositiveIntegerField(null=True, blank=True)
	observacao = models.TextField(blank=True)
	atualizada_em = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Configuração IA: {self.usuario}"


class ConsumoIA(models.Model):
	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="consumos_ia",
	)
	mes = models.DateField()
	tokens_entrada = models.PositiveBigIntegerField(default=0)
	tokens_saida = models.PositiveBigIntegerField(default=0)
	tokens_raciocinio = models.PositiveBigIntegerField(default=0)
	tokens_total = models.PositiveBigIntegerField(default=0)
	custo_estimado = models.DecimalField(max_digits=14, decimal_places=8, null=True, blank=True)
	atualizado_em = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["usuario", "mes"], name="consumo_ia_usuario_mes_unico"),
		]
		indexes = [
			models.Index(fields=["usuario", "-mes"], name="website_con_usuario_8db0d8_idx"),
			models.Index(fields=["-mes"], name="website_con_mes_54e434_idx"),
		]
