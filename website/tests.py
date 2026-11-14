import json
from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from veiculos.models import CategoriaVeiculo, Etapa, Feirao, Filial, Vendedor
from ia.gemini import RespostaIA
from ia.models import ConversaIA
from ia.services import responder_chat


class HomePublicaTest(TestCase):
    def test_home_carrega_contagens_e_feiroes_abertos_no_prazo(self):
        agora = timezone.make_aware(datetime(2026, 11, 12, 12, 0))
        usuario = User.objects.create_user(username="admin")
        filial = Filial.objects.create(nome="Filial Centro")

        feirao_aberto = Feirao.objects.create(
            nome="Feirão Aberto",
            filial=filial,
            data=agora.date(),
            data_limite_propostas=agora + timedelta(days=1),
            cadastrado_por=usuario,
        )
        Feirao.objects.create(
            nome="Feirão Encerrado",
            filial=filial,
            data=agora.date(),
            data_limite_propostas=agora - timedelta(seconds=1),
            cadastrado_por=usuario,
        )

        with patch("website.views.timezone.now", return_value=agora):
            resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "website/index.html")
        self.assertEqual(resposta.context["total_feiroes"], Feirao.objects.count())
        self.assertEqual(resposta.context["total_abertos"], 1)
        self.assertEqual(
            list(resposta.context["feiroes_abertos"]),
            [feirao_aberto],
        )
        self.assertContains(resposta, ">2</h3>")
        self.assertContains(resposta, ">1</h3>")
        self.assertContains(resposta, feirao_aberto.nome)
        self.assertContains(resposta, "Feirão Encerrado")

    def test_paginas_publicas_carregam_sem_autenticacao_e_com_links_de_navegacao(self):
        paginas_publicas = (
            ("index", "website/index.html"),
            ("contato", "website/contato.html"),
            ("sobre", "website/sobre.html"),
        )

        for nome_url, template in paginas_publicas:
            with self.subTest(pagina=nome_url):
                resposta = self.client.get(reverse(nome_url))

                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateUsed(resposta, template)

                for destino, texto in (
                    ("index", "Início"),
                    ("contato", "Contato"),
                    ("sobre", "Sobre"),
                ):
                    self.assertContains(
                        resposta,
                        f'href="{reverse(destino)}"',
                    )
                    self.assertContains(resposta, texto)

    def test_login_valido_redireciona_para_home_com_navegacao_autenticada(self):
        usuario = User.objects.create_user(
            username="usuario",
            password="senha-segura-123",
        )

        resposta_login = self.client.get(reverse("login"))
        self.assertEqual(resposta_login.status_code, 200)

        resposta_envio = self.client.post(
            reverse("login"),
            {
                "username": usuario.username,
                "password": "senha-segura-123",
            },
        )

        self.assertRedirects(resposta_envio, reverse("index"))
        self.assertEqual(
            self.client.session["_auth_user_id"],
            str(usuario.pk),
        )

        resposta_home = self.client.get(reverse("index"))
        self.assertEqual(resposta_home.status_code, 200)
        self.assertContains(resposta_home, usuario.username)
        self.assertContains(resposta_home, "Cadastrar")
        self.assertContains(resposta_home, "Listar")
        self.assertContains(resposta_home, "Alterar Senha")
        self.assertContains(resposta_home, "Sair")

    def test_login_invalido_nao_autentica_e_exibe_mensagem_de_erro(self):
        usuario = User.objects.create_user(
            username="usuario",
            password="senha-segura-123",
        )

        resposta = self.client.post(
            reverse("login"),
            {
                "username": usuario.username,
                "password": "senha-incorreta",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "veiculos/form.html")
        self.assertIn("form", resposta.context)
        self.assertTrue(resposta.context["form"].non_field_errors())
        self.assertContains(
            resposta,
            str(resposta.context["form"].non_field_errors()[0]),
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_encerra_sessao_e_bloqueia_area_protegida(self):
        usuario = User.objects.create_user(
            username="usuario",
            password="senha-segura-123",
        )
        self.client.force_login(usuario)

        resposta_logout = self.client.post(reverse("logout"))

        self.assertRedirects(resposta_logout, reverse("index"))
        self.assertNotIn("_auth_user_id", self.client.session)

        resposta_area_protegida = self.client.get(reverse("filial-list"))

        self.assertRedirects(
            resposta_area_protegida,
            f"{reverse('login')}?next={reverse('filial-list')}",
        )

    def test_anonimo_e_redirecionado_ao_login_ao_acessar_lista_de_feiroes(self):
        url_area_protegida = reverse("feirao-list")

        resposta = self.client.get(url_area_protegida)

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={url_area_protegida}",
        )
        self.assertNotIn("Feirão", resposta.content.decode())

    def test_usuario_sem_permissao_nao_cria_filial(self):
        usuario = User.objects.create_user(
            username="usuario-sem-permissao",
            password="senha-segura-123",
        )
        self.client.force_login(usuario)
        url_cadastro = reverse("filial-create")

        resposta_tela = self.client.get(url_cadastro)
        self.assertEqual(resposta_tela.status_code, 403)

        resposta_envio = self.client.post(
            url_cadastro,
            {"nome": "Filial não autorizada"},
        )

        self.assertEqual(resposta_envio.status_code, 403)
        self.assertEqual(Filial.objects.count(), 0)

    def test_administrador_executa_crud_de_filial(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        usuario.groups.add(grupo_administrador)
        self.client.force_login(usuario)

        resposta_cadastro = self.client.post(
            reverse("filial-create"),
            {"nome": "Filial Norte"},
        )

        self.assertRedirects(resposta_cadastro, reverse("filial-list"))
        filial = Filial.objects.get(nome="Filial Norte")

        resposta_edicao = self.client.post(
            reverse("filial-update", kwargs={"pk": filial.pk}),
            {"nome": "Filial Sul"},
        )

        self.assertRedirects(resposta_edicao, reverse("filial-list"))
        filial.refresh_from_db()
        self.assertEqual(filial.nome, "Filial Sul")

        resposta_exclusao = self.client.post(
            reverse("filial-delete", kwargs={"pk": filial.pk}),
        )

        self.assertRedirects(resposta_exclusao, reverse("filial-list"))
        self.assertFalse(Filial.objects.filter(pk=filial.pk).exists())
        resposta_lista = self.client.get(reverse("filial-list"))
        self.assertEqual(resposta_lista.status_code, 200)
        self.assertNotContains(resposta_lista, "Filial Sul")

    def test_administrador_cria_e_lista_categorias_em_ordem_alfabetica(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        usuario.groups.add(grupo_administrador)
        self.client.force_login(usuario)

        resposta_primeira = self.client.post(
            reverse("categoria-create"),
            {"nome": "SUV"},
        )
        resposta_segunda = self.client.post(
            reverse("categoria-create"),
            {"nome": "Hatch"},
        )

        self.assertRedirects(resposta_primeira, reverse("categoria-list"))
        self.assertRedirects(resposta_segunda, reverse("categoria-list"))

        categorias = {
            categoria.nome: categoria
            for categoria in CategoriaVeiculo.objects.all()
        }
        resposta_lista = self.client.get(reverse("categoria-list"))

        self.assertEqual(resposta_lista.status_code, 200)
        self.assertEqual(resposta_lista.context["total_categorias"], 2)
        self.assertEqual(
            list(resposta_lista.context["object_list"]),
            [categorias["Hatch"], categorias["SUV"]],
        )
        self.assertContains(resposta_lista, ">2</div>")
        for categoria in categorias.values():
            self.assertContains(
                resposta_lista,
                reverse("categoria-detail", kwargs={"pk": categoria.pk}),
            )

    def test_cadastro_de_filial_exibe_mensagem_de_sucesso(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario = User.objects.create_user(username="administrador")
        usuario.groups.add(grupo_administrador)
        self.client.force_login(usuario)

        resposta = self.client.post(
            reverse("filial-create"),
            {"nome": "Filial com mensagem"},
            follow=True,
        )

        self.assertContains(resposta, "Operação realizada com sucesso.")

    def test_etapa_rejeita_valores_numericos_negativos(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        usuario.groups.add(grupo_administrador)
        self.client.force_login(usuario)

        for campo_invalido in ("sequencia", "quantidade_negociacoes"):
            with self.subTest(campo=campo_invalido):
                dados = {
                    "nome": f"Etapa inválida {campo_invalido}",
                    "sequencia": "1",
                    "quantidade_negociacoes": "1",
                }
                dados[campo_invalido] = "-1"

                resposta = self.client.post(
                    reverse("etapa-create"),
                    dados,
                )

                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateUsed(resposta, "veiculos/form.html")
                self.assertTrue(resposta.context["form"].errors[campo_invalido])
                self.assertFalse(
                    Etapa.objects.filter(nome=dados["nome"]).exists()
                )

        self.assertEqual(Etapa.objects.count(), 0)

    def test_vendedor_e_associado_a_filial_e_usuario(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        administrador = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        administrador.groups.add(grupo_administrador)
        usuario_vendedor = User.objects.create_user(username="vendedor")
        filial = Filial.objects.create(nome="Filial Centro")
        self.client.force_login(administrador)

        resposta_cadastro = self.client.post(
            reverse("vendedor-create"),
            {
                "nome": "João da Silva",
                "matricula": "VEN-001",
                "filial": filial.pk,
                "usuario": usuario_vendedor.pk,
            },
        )

        self.assertRedirects(resposta_cadastro, reverse("vendedor-list"))
        vendedor = Vendedor.objects.get(matricula="VEN-001")
        self.assertEqual(vendedor.filial, filial)
        self.assertEqual(vendedor.usuario, usuario_vendedor)

        resposta_lista = self.client.get(reverse("vendedor-list"))
        self.assertEqual(resposta_lista.status_code, 200)
        self.assertContains(resposta_lista, vendedor.nome)
        self.assertContains(resposta_lista, vendedor.matricula)
        self.assertContains(
            resposta_lista,
            reverse("vendedor-detail", kwargs={"pk": vendedor.pk}),
        )

        resposta_detalhe = self.client.get(
            reverse("vendedor-detail", kwargs={"pk": vendedor.pk})
        )
        self.assertEqual(resposta_detalhe.status_code, 200)
        self.assertContains(resposta_detalhe, vendedor.nome)
        self.assertContains(resposta_detalhe, filial.nome)
        self.assertContains(resposta_detalhe, usuario_vendedor.username)

    def test_usuario_nao_pode_ser_associado_a_dois_vendedores(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        administrador = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        administrador.groups.add(grupo_administrador)
        usuario_vendedor = User.objects.create_user(username="vendedor")
        filial = Filial.objects.create(nome="Filial Centro")
        self.client.force_login(administrador)

        dados_primeiro = {
            "nome": "Primeiro Vendedor",
            "matricula": "VEN-001",
            "filial": filial.pk,
            "usuario": usuario_vendedor.pk,
        }
        resposta_primeiro = self.client.post(
            reverse("vendedor-create"),
            dados_primeiro,
        )
        self.assertRedirects(resposta_primeiro, reverse("vendedor-list"))
        self.assertEqual(Vendedor.objects.count(), 1)

        dados_segundo = {
            "nome": "Segundo Vendedor",
            "matricula": "VEN-002",
            "filial": filial.pk,
            "usuario": usuario_vendedor.pk,
        }
        resposta_segundo = self.client.post(
            reverse("vendedor-create"),
            dados_segundo,
        )

        self.assertEqual(resposta_segundo.status_code, 200)
        self.assertTemplateUsed(resposta_segundo, "veiculos/form.html")
        self.assertTrue(resposta_segundo.context["form"].errors["usuario"])
        self.assertContains(
            resposta_segundo,
            "já existe",
        )
        self.assertEqual(Vendedor.objects.count(), 1)
        self.assertFalse(
            Vendedor.objects.filter(matricula="VEN-002").exists()
        )

    def test_criacao_de_feirao_atribui_autoria_ao_usuario_autenticado(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario_autenticado = User.objects.create_user(
            username="administrador",
            password="senha-segura-123",
        )
        usuario_indicado = User.objects.create_user(username="outro-usuario")
        usuario_autenticado.groups.add(grupo_administrador)
        filial = Filial.objects.create(nome="Filial Centro")
        categoria = CategoriaVeiculo.objects.create(nome="SUV")
        self.client.force_login(usuario_autenticado)

        resposta = self.client.post(
            reverse("feirao-create"),
            {
                "nome": "Feirão de Novembro",
                "filial": filial.pk,
                "data": "2026-11-20",
                "data_limite_propostas": "2026-11-19 18:00",
                "categorias": [categoria.pk],
                "cadastrado_por": usuario_indicado.pk,
            },
        )

        feirao = Feirao.objects.get(nome="Feirão de Novembro")
        self.assertRedirects(
            resposta,
            reverse("feirao-detail", kwargs={"pk": feirao.pk}),
        )
        self.assertEqual(feirao.cadastrado_por, usuario_autenticado)
        self.assertNotEqual(feirao.cadastrado_por, usuario_indicado)
        self.assertEqual(list(feirao.categorias.all()), [categoria])

    def test_lista_de_feiroes_respeita_o_usuario_criador(self):
        usuario_a = User.objects.create_user(username="usuario-a")
        usuario_b = User.objects.create_user(username="usuario-b")
        filial = Filial.objects.create(nome="Filial Centro")
        categoria = CategoriaVeiculo.objects.create(nome="SUV")
        dados_feirao = {
            "filial": filial,
            "data": "2026-11-20",
            "data_limite_propostas": timezone.make_aware(
                datetime(2026, 11, 19, 18, 0)
            ),
        }
        feirao_a = Feirao.objects.create(
            nome="Feirão do Usuário A",
            cadastrado_por=usuario_a,
            **dados_feirao,
        )
        feirao_b = Feirao.objects.create(
            nome="Feirão do Usuário B",
            cadastrado_por=usuario_b,
            **dados_feirao,
        )
        feirao_a.categorias.add(categoria)
        feirao_b.categorias.add(categoria)

        self.client.force_login(usuario_a)
        resposta_usuario_a = self.client.get(reverse("feirao-list"))

        self.assertEqual(resposta_usuario_a.status_code, 200)
        self.assertEqual(
            list(resposta_usuario_a.context["object_list"]),
            [feirao_a],
        )
        self.assertContains(resposta_usuario_a, feirao_a.nome)
        self.assertNotContains(resposta_usuario_a, feirao_b.nome)

        self.client.force_login(usuario_b)
        resposta_usuario_b = self.client.get(reverse("feirao-list"))

        self.assertEqual(resposta_usuario_b.status_code, 200)
        self.assertEqual(
            list(resposta_usuario_b.context["object_list"]),
            [feirao_b],
        )
        self.assertContains(resposta_usuario_b, feirao_b.nome)
        self.assertNotContains(resposta_usuario_b, feirao_a.nome)

    def test_usuario_nao_edita_feirao_de_outro_usuario(self):
        grupo_administrador = Group.objects.create(name="Administrador")
        usuario_a = User.objects.create_user(username="usuario-a")
        usuario_b = User.objects.create_user(username="usuario-b")
        usuario_a.groups.add(grupo_administrador)
        filial = Filial.objects.create(nome="Filial Centro")
        categoria = CategoriaVeiculo.objects.create(nome="SUV")
        feirao_b = Feirao.objects.create(
            nome="Feirão do Usuário B",
            filial=filial,
            data="2026-11-20",
            data_limite_propostas=timezone.make_aware(
                datetime(2026, 11, 19, 18, 0)
            ),
            cadastrado_por=usuario_b,
        )
        feirao_b.categorias.add(categoria)
        url_edicao = reverse("feirao-update", kwargs={"pk": feirao_b.pk})
        self.client.force_login(usuario_a)

        resposta_tela = self.client.get(url_edicao)
        self.assertEqual(resposta_tela.status_code, 404)

        resposta_detalhe = self.client.get(
            reverse("feirao-detail", kwargs={"pk": feirao_b.pk})
        )
        self.assertEqual(resposta_detalhe.status_code, 404)

        resposta_envio = self.client.post(
            url_edicao,
            {
                "nome": "Feirão alterado indevidamente",
                "filial": filial.pk,
                "data": "2026-11-21",
                "data_limite_propostas": "2026-11-20 18:00",
                "categorias": [categoria.pk],
                "cadastrado_por": usuario_a.pk,
            },
        )
        self.assertEqual(resposta_envio.status_code, 404)

        feirao_b.refresh_from_db()
        self.assertEqual(feirao_b.nome, "Feirão do Usuário B")
        self.assertEqual(feirao_b.data.isoformat(), "2026-11-20")
        self.assertEqual(feirao_b.cadastrado_por, usuario_b)
        self.assertEqual(list(feirao_b.categorias.all()), [categoria])


class GeminiChatAjaxTest(TestCase):
    def test_endpoint_persiste_conversa_e_sanitiza_markdown(self):
        usuario = User.objects.create_user(username="usuario")
        self.client.force_login(usuario)
        resposta_ia = RespostaIA(
            texto="**Olá** <script>alert(1)</script>",
            dados=None,
            tokens_entrada=1,
            tokens_saida=2,
            tokens_raciocinio=0,
            tokens_total=3,
            modelo="falso",
            motivo_fim="STOP",
        )

        with patch("ia.views.responder_chat", return_value=resposta_ia):
            resposta = self.client.post(
                reverse("gemini-chat-api"),
                data=json.dumps({"message": "Olá"}),
                content_type="application/json",
            )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["html"], "<p><strong>Olá</strong> alert(1)</p>")
        self.assertNotIn("<script>", resposta.json()["html"])
        conversa = ConversaIA.objects.get(usuario=usuario)
        self.assertEqual(len(conversa.mensagens), 2)
        self.assertEqual(conversa.mensagens[0]["text"], "Olá")

    def test_endpoint_nao_acessa_conversa_de_outro_usuario(self):
        usuario = User.objects.create_user(username="usuario")
        outro_usuario = User.objects.create_user(username="outro-usuario")
        conversa = ConversaIA.objects.create(
            usuario=outro_usuario,
            mensagens=[],
        )
        self.client.force_login(usuario)

        resposta = self.client.post(
            reverse("gemini-chat-api"),
            data=json.dumps(
                {"conversation_id": conversa.pk, "message": "Acesso indevido"}
            ),
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(
            resposta.json()["erro"],
            "A conversa informada é inválida.",
        )

    @patch("ia.services.chamar_ia")
    def test_service_envia_apenas_as_cinco_mensagens_mais_recentes(self, chamar_ia_mock):
        historico = [
            {"role": "user", "text": f"Mensagem {numero}"}
            for numero in range(7)
        ]

        responder_chat(
            usuario=User.objects.create_user(username="usuario"),
            mensagem="Nova mensagem",
            historico=historico,
        )

        pedido = chamar_ia_mock.call_args.kwargs["montar_pedido"]()
        self.assertEqual(
            [mensagem.texto for mensagem in pedido.historico],
            ["Mensagem 2", "Mensagem 3", "Mensagem 4", "Mensagem 5", "Mensagem 6"],
        )


class IAAdminGroupAccessTest(TestCase):
    def test_grupo_administrador_acessa_paineis_de_ia(self):
        grupo = Group.objects.create(name="Administrador")
        usuario = User.objects.create_user(username="admin-ia")
        usuario.groups.add(grupo)
        self.client.force_login(usuario)

        for nome_url in ("configuracao-ia", "requisicoes-ia"):
            with self.subTest(view=nome_url):
                resposta = self.client.get(reverse(nome_url))
                self.assertEqual(resposta.status_code, 200)

    def test_superusuario_sem_grupo_nao_acessa_paineis_de_ia(self):
        usuario = User.objects.create_superuser(
            username="superuser-sem-grupo",
            password="senha-segura-123",
        )
        self.client.force_login(usuario)

        for nome_url in ("configuracao-ia", "requisicoes-ia"):
            with self.subTest(view=nome_url):
                resposta = self.client.get(reverse(nome_url))
                self.assertEqual(resposta.status_code, 302)