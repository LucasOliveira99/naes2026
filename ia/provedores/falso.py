from types import SimpleNamespace


def criar_cliente(config):
    return SimpleNamespace()


def contar_tokens(pedido, config, cliente):
    return max(1, len(pedido.texto) // 4)


def gerar(pedido, config, cliente):
    return SimpleNamespace(
        text='{"tipo":"informacao","resposta":"Resposta falsa de teste","dados":{}}',
        usage_metadata=SimpleNamespace(
            prompt_token_count=1,
            candidates_token_count=1,
            thoughts_token_count=0,
            total_token_count=2,
        ),
        candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name="STOP"))],
        model_version="falso",
    )


def testar(config, cliente):
    return gerar(SimpleNamespace(texto="", historico=[], arquivos=[], instrucoes="", esquema=None), config, cliente)
