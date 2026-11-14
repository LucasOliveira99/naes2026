from django.core.management.base import BaseCommand

from website.gemini import limpar_requisicoes_antigas


class Command(BaseCommand):
    help = "Remove requisicoes de IA antigas em lotes; preserva o consumo mensal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--lote",
            type=int,
            default=1000,
            help="Quantidade maxima de requisicoes removidas por lote.",
        )

    def handle(self, *args, **options):
        lote = options["lote"]
        if lote < 1:
            self.stdout.write(self.style.ERROR("--lote deve ser maior que zero."))
            return
        removidas = limpar_requisicoes_antigas(lote=lote)
        self.stdout.write(self.style.SUCCESS(f"{removidas} requisicao(oes) removida(s)."))
