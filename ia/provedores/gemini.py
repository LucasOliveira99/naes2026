from google import genai
from google.genai import types


def criar_cliente(config):
    http_options = types.HttpOptions(timeout=config.timeout_segundos * 1000)
    if config.acesso == "api_key":
        if not config.api_key:
            raise ValueError("A chave da API do Gemini não está configurada")
        return genai.Client(api_key=config.api_key, http_options=http_options)
    if config.acesso == "enterprise":
        if not config.projeto_gcp or not config.regiao:
            raise ValueError("Projeto e região são obrigatórios no modo Enterprise")
        return genai.Client(
            enterprise=True,
            project=config.projeto_gcp,
            location=config.regiao,
            http_options=http_options,
        )
    raise ValueError("Modo de acesso do Gemini inválido")


def _conteudos(pedido):
    contents = [
        types.Content(
            role=message.role,
            parts=[types.Part.from_text(text=message.texto)],
        )
        for message in pedido.historico
    ]
    parts = []
    if pedido.texto:
        parts.append(types.Part.from_text(text=pedido.texto))
    for arquivo in pedido.arquivos:
        parts.append(types.Part.from_bytes(data=arquivo.dados, mime_type=arquivo.mime_type))
    contents.append(types.Content(role="user", parts=parts))
    return contents


def contar_tokens(pedido, config, cliente):
    return cliente.models.count_tokens(model=config.modelo, contents=_conteudos(pedido)).total_tokens


def gerar(pedido, config, cliente):
    config_data = {
        "system_instruction": pedido.instrucoes,
        "temperature": float(config.temperatura),
        "max_output_tokens": config.max_output_tokens,
        "thinking_config": types.ThinkingConfig(thinking_level=config.nivel_raciocinio),
    }
    if pedido.esquema:
        config_data["response_mime_type"] = "application/json"
        config_data["response_json_schema"] = pedido.esquema.model_json_schema()
    return cliente.models.generate_content(
        model=config.modelo,
        contents=_conteudos(pedido),
        config=types.GenerateContentConfig(**config_data),
    )


def testar(config, cliente):
    return cliente.models.generate_content(
        model=config.modelo,
        contents="Responda apenas OK.",
        config=types.GenerateContentConfig(max_output_tokens=8, temperature=0),
    )
