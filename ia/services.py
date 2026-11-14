import bleach
import markdown

from ia.chamada import chamar_ia
from .gemini import MensagemIA, PedidoIA, PROMPT_VERSION


MARKDOWN_TAGS_PERMITIDAS = {
    "p", "br", "strong", "em", "del", "ul", "ol", "li", "blockquote",
    "code", "pre", "h1", "h2", "h3", "h4", "hr", "table", "thead",
    "tbody", "tr", "th", "td",
}
MAX_CHAT_MESSAGES = 5


def renderizar_markdown_seguro(texto):
    html = markdown.markdown(
        texto,
        extensions=["fenced_code", "tables"],
    )
    return bleach.clean(
        html,
        tags=MARKDOWN_TAGS_PERMITIDAS,
        attributes={},
        protocols={"http", "https", "mailto"},
        strip=True,
    )


def responder_chat(*, usuario, mensagem, historico):
    def montar_pedido():
        return PedidoIA(
            texto=mensagem,
            historico=[
                MensagemIA(role=item["role"], texto=item["text"])
                for item in historico[-(MAX_CHAT_MESSAGES - 1):]
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
