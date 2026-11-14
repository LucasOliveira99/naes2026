---
name: django-crud
description: "Use ao implementar ou modificar cadastro, listagem, edição ou exclusão Django neste projeto, incluindo filtros, mensagens e isolamento por proprietário."
---

# CRUD Django do projeto

1. Leia as views, URLs, models, templates e testes relacionados. Siga os
   mixins, nomes de rotas e templates já usados; leia as instruções de backend
   e templates antes de editar.
2. Mantenha validação de domínio nos forms/services apropriados e deixe a view
   tratar autenticação, entrada HTTP, contexto e mensagens.
3. Em recursos pertencentes a um usuário, aplique a restrição de proprietário
   em toda leitura por identificador e em listas, além de validar a autoria ao
   criar ou alterar. Não confie em IDs enviados pelo navegador.
4. Reutilize mensagens, paginação, filtros e componentes existentes. Adicione
   somente o comportamento pedido, com textos visíveis em português.
5. Adicione um teste de comportamento que cubra o caminho feliz e, quando
   pertinente, a negação de acesso a dados de outro usuário.
6. Execute os testes focados e `python manage.py check`. Se a suíte completa
   revelar falhas não relacionadas, descreva-as separadamente.

Não crie mixins, serviços ou componentes genéricos quando um padrão existente
resolver a alteração sem duplicação relevante.
