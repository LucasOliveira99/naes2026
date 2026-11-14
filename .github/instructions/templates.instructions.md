---
name: templates
applyTo: "**/templates/**/*.html"
description: "Regras para templates Django e interface do Feirao Motors."
---

- Todo template deve estender o layout base já adotado pelo projeto.
- Textos visíveis para o usuário devem estar em português.
- Evite CSS inline; prefira as classes e estilos compartilhados existentes.
- Preserve responsividade, acessibilidade básica e proteção CSRF em formulários POST.
- Não coloque regras de negócio ou chamadas de provedor nos templates.
- Não exiba chaves de API, tokens, prompts privados ou dados sensíveis de auditoria.
