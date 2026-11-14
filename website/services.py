from ia.chamada import chamar_ia
from website.gemini import MensagemIA, PedidoIA, PROMPT_VERSION


def responder_chat(*, usuario, mensagem, historico):
    def montar_pedido():
        return PedidoIA(
            texto=mensagem,
            historico=[
                MensagemIA(role=item["role"], texto=item["text"])
                for item in historico
            ],
        )

    return chamar_ia(
        finalidade="chatbot_resposta",
        usuario=usuario,
        origem="site",
        referencia=None,
        montar_pedido=montar_pedido,
        versao_prompt=PROMPT_VERSION,
    )
