---
name: django-model-migrations
description: "Use ao criar ou alterar models, campos, relacionamentos ou índices Django neste projeto; orienta a mudança de schema e sua migração segura."
---

# Migrações de modelos Django

Use este fluxo somente quando a tarefa alterar o schema. Para mudanças sem
impacto em models, não gere migração.

1. Leia o model, migrações recentes e instruções de backend.
2. Preserve nomes de domínio já estabelecidos em português e os padrões de
   relações, constraints e índices existentes.
3. Faça a alteração no model; nunca edite arquivos de `migrations/` à mão.
4. Gere a migração com `python manage.py makemigrations` e leia o arquivo
   resultante. Verifique se o Django incluiu operações não relacionadas.
5. Execute `python manage.py makemigrations --check` e `python manage.py check`.
6. Rode testes específicos do model e migração; amplie a suíte se a mudança
   afetar comportamento usado por outros fluxos.

Antes de escolher um campo ou operação, verifique se os dados existentes
precisam de valor padrão, preenchimento em etapas ou proteção contra perda.
Não introduza abstrações ou operações de banco que a mudança não exige.
