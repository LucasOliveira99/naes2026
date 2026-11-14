---
name: backend
applyTo: "**/*.py,manage.py,requirements.txt"
description: "Regras Django e Python do projeto Feirao Motors."
---

- Rode `python manage.py check` após alterações Django.
- Rode `python manage.py test` antes de qualquer commit.
- Não edite arquivos em `migrations/` manualmente; gere-os com `python manage.py makemigrations`.
- Mantenha regras de negócio em services, não em templates ou views.
- Views devem cuidar de autenticação, entrada HTTP, contexto e mensagens para o usuário.
- Use nomes de modelos e campos de domínio em português, respeitando o schema existente.
- Use mensagens de erro em português e não exponha exceções, chaves ou credenciais.
