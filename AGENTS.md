# Instruções do projeto

Este é um projeto Django.

## Regras gerais

- Use Python/Django e preserve os padrões existentes do projeto.
- Rode `python manage.py test` antes de qualquer commit.
- Siga a nomenclatura em português para modelos e campos de domínio.
- Escreva o código novo em inglês quando isso não conflitar com nomes de domínio já estabelecidos.
- Explique erros e mensagens técnicas ao usuário em português.
- Nunca edite arquivos dentro de `migrations/` manualmente; altere os models e gere migrações com `python manage.py makemigrations`.
- Não exponha segredos em código, templates, logs, auditoria ou respostas.
- Preserve alterações existentes do usuário e mantenha as mudanças focadas.

## Commits

- Para escrever a mensagem de um commit, use a skill `commit-padrao`.

## Regras por assunto

- Backend Django/Python: `.github/instructions/backend.instructions.md`
- Templates e frontend: `.github/instructions/templates.instructions.md`
- Integração de IA: `.github/instructions/ia.instructions.md`

Leia a rule específica antes de editar arquivos daquele assunto. Use skills somente quando a tarefa exigir um workflow especializado, não como substituto destas regras permanentes.
