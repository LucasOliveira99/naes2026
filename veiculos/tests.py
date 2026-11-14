from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Filial


class FilialListFilterTest(TestCase):
    def test_busca_filtra_e_paginacao_preserva_parametro(self):
        usuario = User.objects.create_user(username="usuario")
        Filial.objects.bulk_create(
            [Filial(nome=f"Filial Norte {numero}") for numero in range(31)]
            + [Filial(nome="Filial Sul")]
        )
        self.client.force_login(usuario)

        resposta = self.client.get(
            reverse("filial-list"),
            {"busca": "Norte", "page": 2},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["filter"].form.cleaned_data["busca"], "Norte")
        self.assertEqual(resposta.context["paginator"].count, 31)
        self.assertEqual(resposta.context["page_obj"].number, 2)
        self.assertContains(resposta, "Filial Norte 9")
        self.assertNotContains(resposta, "Filial Sul")
        self.assertContains(resposta, "?busca=Norte&amp;page=1")
