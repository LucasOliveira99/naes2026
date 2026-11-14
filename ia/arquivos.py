import hashlib
import io
import os
from dataclasses import dataclass, replace

from PIL import Image, ImageOps
from pypdf import PdfReader


MAX_IMAGE_PIXELS = 20_000_000
MAX_PREPARED_IMAGE_DIMENSION = 2048


class ArquivoInvalido(Exception):
    pass


@dataclass
class ArquivoPreparado:
    dados: bytes
    mime_type: str
    tamanho_original: int
    hash_original: str


def _tamanho_antes_de_ler(arquivo):
    tamanho = getattr(arquivo, "size", None)
    if tamanho is not None:
        return int(tamanho)
    if not all(hasattr(arquivo, atributo) for atributo in ("tell", "seek")):
        raise ArquivoInvalido("Não foi possível verificar o tamanho do arquivo")
    posicao = arquivo.tell()
    arquivo.seek(0, os.SEEK_END)
    tamanho = arquivo.tell()
    arquivo.seek(posicao)
    return tamanho


def preparar_arquivo(arquivo, config):
    if isinstance(arquivo, ArquivoPreparado):
        return arquivo
    if hasattr(arquivo, "uri"):
        raise ArquivoInvalido("Arquivos remotos precisam ser preparados antes do pedido")
    tamanho = _tamanho_antes_de_ler(arquivo)
    if tamanho > config.max_arquivo_bytes:
        raise ArquivoInvalido("O arquivo excede o tamanho máximo configurado")
    posicao = arquivo.tell() if hasattr(arquivo, "tell") else None
    dados = arquivo.read()
    if posicao is not None and hasattr(arquivo, "seek"):
        arquivo.seek(posicao)
    mime_type = getattr(arquivo, "content_type", "application/octet-stream")
    hash_original = hashlib.sha256(dados).hexdigest()

    if mime_type.startswith("image/"):
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
        try:
            with Image.open(io.BytesIO(dados)) as imagem:
                imagem.load()
                if imagem.width * imagem.height > MAX_IMAGE_PIXELS:
                    raise ArquivoInvalido("A imagem excede o limite seguro de pixels")
                imagem = ImageOps.exif_transpose(imagem)
                imagem.thumbnail(
                    (MAX_PREPARED_IMAGE_DIMENSION, MAX_PREPARED_IMAGE_DIMENSION),
                    Image.Resampling.LANCZOS,
                )
                if imagem.mode not in ("RGB", "L"):
                    imagem = imagem.convert("RGB")
                saida = io.BytesIO()
                imagem.save(saida, format="JPEG", quality=85, optimize=True)
                return ArquivoPreparado(saida.getvalue(), "image/jpeg", tamanho, hash_original)
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            raise ArquivoInvalido("A imagem foi rejeitada pelo limite anti-bomba") from error

    if mime_type == "application/pdf":
        try:
            paginas = len(PdfReader(io.BytesIO(dados)).pages)
        except Exception as error:
            raise ArquivoInvalido("PDF inválido ou ilegível") from error
        if paginas > config.max_paginas_pdf:
            raise ArquivoInvalido("O PDF excede o número máximo de páginas")

    return ArquivoPreparado(dados, mime_type, tamanho, hash_original)


def preparar_pedido(pedido, config):
    return replace(pedido, arquivos=[preparar_arquivo(arquivo, config) for arquivo in pedido.arquivos])


def metadados_arquivos(arquivos):
    if not arquivos:
        return {"arquivo_mime": "", "arquivo_tamanho": None, "arquivo_hash": ""}
    hashes = [arquivo.hash_original for arquivo in arquivos]
    return {
        "arquivo_mime": ",".join(sorted({arquivo.mime_type for arquivo in arquivos})),
        "arquivo_tamanho": sum(arquivo.tamanho_original for arquivo in arquivos),
        "arquivo_hash": hashes[0] if len(hashes) == 1 else hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest(),
    }
