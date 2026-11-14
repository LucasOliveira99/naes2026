import logging
import hashlib
import os
import time
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Literal
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from ia.arquivos import metadados_arquivos, preparar_pedido
from ia.provedores import PROVEDORES
from ia.models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA, RequisicaoIA

load_dotenv()

PROMPT_VERSION = "feirao-v2"
logger = logging.getLogger(__name__)
CONFIG_CACHE_KEY = "configuracao_ia:atual"
CONFIG_CACHE_SECONDS = 30
_client_cache_signature = None
_client_cache = None
SYSTEM_INSTRUCTION = (
	Path(__file__).resolve().parent.parent / "contexto_projeto.md"
).read_text(encoding="utf-8").strip()


class CotaIAExcedida(Exception):
	pass


class ConfiguracaoIAInvalida(Exception):
	pass


def _decimal_env(name):
	try:
		return Decimal(os.environ[name])
	except (KeyError, InvalidOperation):
		return None


def get_configuracao_ia():
	config = cache.get(CONFIG_CACHE_KEY)
	if config is None:
		config, _ = ConfiguracaoIA.objects.get_or_create(pk=1)
		if not config.api_key:
			config.api_key = os.environ.get("GEMINI_API_KEY", "")
		cache.set(CONFIG_CACHE_KEY, config, CONFIG_CACHE_SECONDS)
	return config


def limpar_cache_configuracao_ia():
	cache.delete(CONFIG_CACHE_KEY)


def limpar_requisicoes_antigas(*, lote=1000, agora=None):
	config = get_configuracao_ia()
	agora = agora or timezone.now()
	limite = agora - timedelta(days=config.retencao_dias)
	removidas = 0
	while True:
		ids = list(
			RequisicaoIA.objects
			.filter(criada_em__lt=limite)
			.order_by("pk")
			.values_list("pk", flat=True)[:lote]
		)
		if not ids:
			return removidas
		quantidade, _ = RequisicaoIA.objects.filter(pk__in=ids).delete()
		removidas += quantidade

def testar_conexao(config=None):
	config = config or get_configuracao_ia()
	provedor = PROVEDORES.get(config.provedor)
	if provedor is None:
		raise ConfiguracaoIAInvalida("Provedor de IA não configurado")
	provider_client = _cliente_gemini(config)
	return provedor.testar(config, provider_client)


def _configuracao_usuario(usuario):
	return ConfiguracaoIAUsuario.objects.filter(usuario=usuario).first()


def _cliente_gemini(config):
	global _client_cache, _client_cache_signature
	provedor = PROVEDORES.get(config.provedor)
	if provedor is None:
		raise ConfiguracaoIAInvalida("Provedor de IA não configurado")
	signature = (
		config.pk,
		config.atualizada_em,
		config.provedor,
		config.acesso,
		config.api_key,
		config.projeto_gcp,
		config.regiao,
	)
	if signature == _client_cache_signature and _client_cache is not None:
		return _client_cache
	_client_cache = provedor.criar_cliente(config)
	_client_cache_signature = signature
	return _client_cache


def _mes_sao_paulo():
	agora = timezone.localtime(timezone.now(), ZoneInfo("America/Sao_Paulo"))
	return agora.date().replace(day=1)


def _limite_usuario(usuario, config):
	excecao = _configuracao_usuario(usuario)
	if excecao and not excecao.ia_ligada:
		raise CotaIAExcedida("A IA está desativada para este usuário")
	if excecao and excecao.limite_tokens is not None:
		return excecao.limite_tokens
	return config.limite_tokens_padrao


def _verificar_cota(usuario, config, tokens_estimados):
	limite = _limite_usuario(usuario, config)
	mes = _mes_sao_paulo()
	reserva = config.reserva_minima_tokens
	necessario = tokens_estimados + reserva
	with transaction.atomic():
		consumo, _ = ConsumoIA.objects.get_or_create(usuario=usuario, mes=mes)
		consumo = ConsumoIA.objects.select_for_update().get(pk=consumo.pk)
		total_sistema = (
			ConsumoIA.objects.filter(mes=mes).aggregate(total=Sum("tokens_total"))["total"]
			or 0
		)
		if limite == 0 or consumo.tokens_total + necessario > limite:
			raise CotaIAExcedida("O limite mensal de tokens do usuário foi atingido")
		if config.teto_mensal_sistema and total_sistema + necessario > config.teto_mensal_sistema:
			raise CotaIAExcedida("O teto mensal de tokens do sistema foi atingido")


def _registrar_consumo(usuario, config, resposta):
	mes = _mes_sao_paulo()
	custo = _custo_estimado(resposta, config)
	with transaction.atomic():
		consumo, _ = ConsumoIA.objects.get_or_create(usuario=usuario, mes=mes)
		atualizacao = {
			"tokens_entrada": F("tokens_entrada") + resposta.tokens_entrada,
			"tokens_saida": F("tokens_saida") + resposta.tokens_saida,
			"tokens_raciocinio": F("tokens_raciocinio") + resposta.tokens_raciocinio,
			"tokens_total": F("tokens_total") + resposta.tokens_total,
		}
		if custo is not None:
			atualizacao["custo_estimado"] = Coalesce(
				F("custo_estimado"),
				Decimal("0"),
			) + custo
		ConsumoIA.objects.filter(pk=consumo.pk).update(**atualizacao)


class MensagemIA(BaseModel):
	role: Literal["user", "model"]
	texto: str


class RespostaFeirao(BaseModel):
	tipo: Literal["informacao", "analise", "esclarecimento"]
	resposta: str = Field(description="Texto curto para apresentar ao usuario")
	dados: dict[str, Any] = Field(
		default_factory=dict,
		description="Dados estruturados relevantes para o sistema",
	)


@dataclass
class PedidoIA:
	instrucoes: str = SYSTEM_INSTRUCTION
	texto: str = ""
	arquivos: list[Any] = field(default_factory=list)
	historico: list[MensagemIA] = field(default_factory=list)
	esquema: type[BaseModel] | None = RespostaFeirao


@dataclass
class RespostaIA:
	texto: str
	dados: BaseModel | None
	tokens_entrada: int
	tokens_saida: int
	tokens_raciocinio: int
	tokens_total: int
	modelo: str
	motivo_fim: str


@dataclass
class RespostaInvalida(RespostaIA):
	erro: str


def _finish_reason(response):
	candidates = getattr(response, "candidates", []) or []
	if not candidates:
		return "UNKNOWN"
	reason = getattr(candidates[0], "finish_reason", None)
	return getattr(reason, "name", str(reason or "UNKNOWN"))


def _executar_pedido(pedido, config, provider_client):
	provedor = PROVEDORES[config.provedor]
	response = provedor.gerar(pedido, config, provider_client)
	texto = response.text or ""
	usage = get_usage_metadata(response)
	response_data = {
		"texto": texto,
		"tokens_entrada": usage["prompt_token_count"],
		"tokens_saida": usage["candidates_token_count"],
		"tokens_raciocinio": usage["thoughts_token_count"],
		"tokens_total": usage["total_token_count"],
		"modelo": getattr(response, "model_version", config.modelo) or config.modelo,
		"motivo_fim": _finish_reason(response),
	}
	if not pedido.esquema:
		return RespostaIA(dados=None, **response_data)
	try:
		dados = pedido.esquema.model_validate_json(texto)
	except ValidationError as error:
		return RespostaInvalida(dados=None, erro=str(error), **response_data)
	return RespostaIA(dados=dados, **response_data)



def _executar_com_retentativas(pedido, config, provider_client, ao_tentar_novamente=None):
	ultima_excecao = None
	for numero_tentativa in range(1, max(1, config.tentativas) + 1):
		try:
			return _executar_pedido(pedido, config, provider_client)
		except Exception as error:
			ultima_excecao = error
			if numero_tentativa < max(1, config.tentativas) and ao_tentar_novamente:
				ao_tentar_novamente(numero_tentativa + 1, error)
	if ultima_excecao:
		raise ultima_excecao
	raise RuntimeError("Nenhuma tentativa de chamada foi executada")


def _arquivo_metadados(pedido):
	return metadados_arquivos(pedido.arquivos)


def _classificar_erro(error):
	if isinstance(error, CotaIAExcedida):
		return RequisicaoIA.SITUACAO_COTA
	if isinstance(error, ConfiguracaoIAInvalida):
		return RequisicaoIA.SITUACAO_CONFIGURACAO
	mensagem = str(error).lower()
	if "quota" in mensagem or "rate limit" in mensagem or "resource exhausted" in mensagem:
		return RequisicaoIA.SITUACAO_COTA
	if "api key" in mensagem or "credential" in mensagem or "configur" in mensagem:
		return RequisicaoIA.SITUACAO_CONFIGURACAO
	return RequisicaoIA.SITUACAO_ERRO_TEMPORARIO


def _referencia_auditoria(referencia):
	if referencia is None:
		return {"referencia_tipo": None, "referencia_id": ""}
	if not getattr(referencia, "_meta", None) or not getattr(referencia, "pk", None):
		raise ValueError("referencia deve ser uma instância Django persistida ou None")
	return {
		"referencia_tipo": ContentType.objects.get_for_model(
			referencia,
			for_concrete_model=False,
		),
		"referencia_id": str(referencia.pk),
	}


def _custo_estimado(resposta, config):
	if config.preco_entrada_milhao is None or config.preco_saida_milhao is None:
		return None
	return (
		(
			Decimal(resposta.tokens_entrada) * config.preco_entrada_milhao
			+ Decimal(resposta.tokens_saida + resposta.tokens_raciocinio)
			* config.preco_saida_milhao
		)
		/ Decimal(1_000_000)
	).quantize(Decimal("0.00000001"))


def _criar_auditoria(**dados):
	try:
		return RequisicaoIA.objects.create(**dados)
	except Exception:
		logger.exception("Falha ao gravar auditoria de tentativa de IA")
		return None


def _atualizar_auditoria(auditoria, **dados):
	if auditoria is None:
		return
	try:
		RequisicaoIA.objects.filter(pk=auditoria.pk).update(**dados)
	except Exception:
		logger.exception("Falha ao atualizar auditoria de tentativa de IA")


def chamar_ia(*, finalidade, usuario, origem, referencia, montar_pedido, versao_prompt, tentativa=1):
	if not getattr(usuario, "pk", None):
		raise ValueError("chamar_ia exige um usuario Django persistido")
	inicio = time.perf_counter()
	auditoria = _criar_auditoria(
		finalidade=finalidade,
		usuario=usuario,
		origem=origem,
		**_referencia_auditoria(referencia),
		versao_prompt=versao_prompt,
		tentativa=tentativa,
		provedor="google-gemini",
		texto_hash="",
	)
	try:
		config = get_configuracao_ia()
		config_usuario = _configuracao_usuario(usuario)
		if config_usuario and not config_usuario.ia_ligada:
			raise CotaIAExcedida("A IA está desativada para este usuário")
		pedido = montar_pedido()
		if not isinstance(pedido, PedidoIA):
			raise TypeError("montar_pedido deve retornar um PedidoIA")
		pedido = preparar_pedido(pedido, config)
		auditoria_dados = {
			"texto_hash": hashlib.sha256(pedido.texto.encode("utf-8")).hexdigest(),
			**_arquivo_metadados(pedido),
		}
		_atualizar_auditoria(auditoria, **auditoria_dados)
		if (
			auditoria_dados["arquivo_tamanho"] is not None
			and auditoria_dados["arquivo_tamanho"] > config.max_arquivo_bytes
		):
			raise ConfiguracaoIAInvalida("O arquivo excede o tamanho máximo configurado")
		provider_client = _cliente_gemini(config)
		tokens_estimados = count_input_tokens(pedido, config, provider_client)
		_verificar_cota(usuario, config, tokens_estimados)

		def ao_tentar_novamente(numero, error):
			nonlocal auditoria
			_atualizar_auditoria(
				auditoria,
				situacao=RequisicaoIA.SITUACAO_ERRO_TEMPORARIO,
				erro=str(error),
				duracao_ms=round((time.perf_counter() - inicio) * 1000),
			)
			auditoria = _criar_auditoria(
				finalidade=finalidade,
				usuario=usuario,
				origem=origem,
				**_referencia_auditoria(referencia),
				versao_prompt=versao_prompt,
				tentativa=numero,
				provedor=config.provedor,
				**auditoria_dados,
			)

		resposta = _executar_com_retentativas(
			pedido,
			config,
			provider_client,
			ao_tentar_novamente=ao_tentar_novamente,
		)
		_registrar_consumo(usuario, config, resposta)
		status = (
			RequisicaoIA.SITUACAO_INVALIDA
			if isinstance(resposta, RespostaInvalida)
			else RequisicaoIA.SITUACAO_SUCESSO
		)
		_atualizar_auditoria(
			auditoria,
			situacao=status,
			modelo=resposta.modelo,
			motivo_fim=resposta.motivo_fim,
			tokens_entrada=resposta.tokens_entrada,
			tokens_saida=resposta.tokens_saida,
			tokens_raciocinio=resposta.tokens_raciocinio,
			tokens_total=resposta.tokens_total,
			custo_estimado=_custo_estimado(resposta, config),
			resposta=resposta.texto[:20000],
			duracao_ms=round((time.perf_counter() - inicio) * 1000),
			erro=resposta.erro if isinstance(resposta, RespostaInvalida) else "",
		)
		return resposta
	except Exception as error:
		_atualizar_auditoria(
			auditoria,
			situacao=_classificar_erro(error),
			duracao_ms=round((time.perf_counter() - inicio) * 1000),
			erro=str(error),
		)
		raise


def count_input_tokens(pedido, config, provider_client):
	provedor = PROVEDORES[config.provedor]
	return provedor.contar_tokens(pedido, config, provider_client)


def get_usage_metadata(response):
	usage = getattr(response, "usage_metadata", None)
	return {
		"prompt_token_count": getattr(usage, "prompt_token_count", 0) or 0,
		"candidates_token_count": getattr(usage, "candidates_token_count", 0) or 0,
		"thoughts_token_count": getattr(usage, "thoughts_token_count", 0) or 0,
		"total_token_count": getattr(usage, "total_token_count", 0) or 0,
	}
