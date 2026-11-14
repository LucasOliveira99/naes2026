---
name: django-testing
description: "Use ao adicionar testes Django, corrigir uma regressão ou validar mudanças neste projeto; escolhe testes focados e amplia a execução conforme o risco."
---

# Testes Django

1. Localize os testes que já cobrem o fluxo e use o `TestCase`, factories,
   fixtures e mocks existentes antes de adicionar infraestrutura.
2. Escreva testes para comportamento observável e limites importantes, não
   para repetir implementação ou testar detalhes internos sem contrato.
3. Para regressões, confirme que o teste falha antes da correção sempre que
   isso for viável; depois rode o teste focado.
4. Para mudanças Django, execute `python manage.py check`. Antes de concluir
   uma alteração, rode `python manage.py test`; use `--keepdb` apenas se a
   criação do banco de teste já existente impedir a execução normal.
5. Investigue falhas e diferencie regressões das falhas que também ocorrem fora
   do escopo. Não altere regras de negócio alheias para deixar a suíte verde.
6. Informe comandos, resultados e limitações de execução com clareza.

Mantenha os testes pequenos: prefira um caso representativo e um caso de borda
que protejam a mudança a duplicar a suíte por método ou classe.
