---
name: commit-padrao
description: "Use sempre que for escrever a mensagem de um commit neste projeto — gera mensagens no padrão Conventional Commits, com resumo no imperativo e um corpo curto que descreve o que foi implementado, nunca apenas um rótulo genérico como fix ou ajustes."
allowed-tools: Bash(git diff *), Bash(git status *), Bash(git log *)
---

# Skill: commit-padrao

## Regras que a mensagem nunca deve quebrar

- Um commit, um assunto. Se o diff mistura uma correção de bug com uma feature nova sem relação, são dois commits; não force uma mensagem que tente cobrir os dois.
- O corpo descreve o que foi implementado, não repete o resumo com outras palavras. Se o resumo diz "valida expiração do token", o corpo explica como.
- Nunca use rótulos vazios como "ajustes diversos", "melhorias" ou "correções gerais". Se não for possível nomear o que mudou em uma frase, o commit deve ser dividido.
- O resumo fica no imperativo: `adiciona`, `remove`, `corrige`, não `adicionado` ou `removi`.
- Não use ponto final no resumo.
- O resumo cabe em uma linha e tem aproximadamente até 72 caracteres.

## Mudanças pendentes

Antes de escrever a mensagem, rode e leia:

```bash
git status
git diff --cached
git log -5 --oneline
```

Se não houver nada staged, informe isso e sugira `git add`; não invente uma mensagem.

Use `git log -5` apenas para conhecer escopos e convenções do projeto. Não copie mensagens genéricas do histórico quando elas contrariarem estas regras.

## Formato

```text
tipo(escopo opcional): resumo no imperativo

O que foi implementado em termos concretos.

Por que a mudança foi necessária, quando o motivo não for óbvio no código.

Rodapé opcional: referências a issues, breaking changes ou outras informações operacionais.
```

A primeira linha deve conter:

- `tipo`: palavra fixa que classifica a natureza da mudança;
- `escopo`: opcional, entre parênteses, como `auth`, `financeiro`, `bot`, `ia` ou `deploy`;
- `resumo`: frase curta, concreta, no imperativo e sem ponto final.

## Tipos válidos

- `feat`: funcionalidade nova para quem usa o sistema.
- `fix`: correção de comportamento incorreto.
- `docs`: somente documentação, comentários ou instruções.
- `style`: formatação sem mudança de comportamento.
- `refactor`: reorganização sem mudança do comportamento externo.
- `perf`: melhoria cujo objetivo principal é desempenho.
- `test`: adição ou ajuste de testes.
- `build`: dependências ou processo de build.
- `ci`: esteira de integração contínua.
- `chore`: manutenção que não se encaixa nas anteriores.

## Instruções

1. A primeira linha segue `tipo(escopo): resumo no imperativo`, sem ponto final e com até 72 caracteres.
2. Separe o cabeçalho do corpo com uma linha em branco.
3. Se o diff tocar mais de um arquivo e passar de aproximadamente 15 linhas, escreva um corpo de 2 a 5 linhas ou bullets, salvo quando a mudança for autoexplicativa.
4. O corpo deve nomear funções, modelos, rotas, templates, testes ou comportamentos concretos do diff.
5. Explique o motivo somente quando ele não for evidente olhando o código.
6. Não descreva algo que não aparece no diff staged.
7. Se houver mudanças sem relação, avise o usuário e sugira separar os commits.
8. Mudanças em `docs/` usam o nome do arquivo como escopo, por exemplo `docs(prd): atualiza requisito de auditoria`.
9. Mudanças que criam ou alteram requisitos, regras, casos de uso ou tarefas devem citar o ID no resumo ou corpo.
10. Não inclua segredos, senhas, tokens ou dados pessoais na mensagem.

## O que o corpo precisa conter

O corpo responde "o que mudou no código?", não "qual é o tema do commit".

- Cite nomes que aparecem no diff: função, classe, rota, template ou teste.
- Prefira bullets se houver mais de uma mudança concreta.
- Não reescreva a primeira linha com sinônimos.
- Inclua migrações, breaking changes e validações quando forem relevantes.

## Exemplos ruins e bons

Ruim:

```text
fix bug
```

Bom:

```text
fix(auth): valida expiração do token antes de liberar o painel

O middleware aceitava tokens expirados porque a checagem comparava
apenas a assinatura, não o campo `exp`. Agora decodifica o payload
e rejeita com 401 quando `exp` já passou.
```

Ruim:

```text
wip
```

Bom:

```text
feat(financeiro): categoriza lançamentos automaticamente via Gemini

Ao salvar um lançamento sem categoria, o service chama o Gemini
com a descrição digitada pelo usuário e preenche `categoria`
antes de gravar no banco.
```

Ruim:

```text
adicionado painel novo
```

Bom:

```text
feat(ia): exibe consumo mensal de tokens por usuário

Adiciona o painel com limite efetivo, tokens usados, saldo restante
e data de renovação. O total vem de `ConsumoIA`, sem reprocessar
as requisições históricas.
```

Ruim:

```text
docs: documentação
```

Bom:

```text
docs(ia): documenta o contrato da porta única de chamadas

Registra o uso de `chamar_ia`, o registry de providers, a auditoria
por tentativa e as regras para preparação de arquivos.
```

Ruim:

```text
refactor: muda models e migrations
```

Bom:

```text
refactor(ia): separa providers da porta de chamada

Move o acesso ao SDK Gemini para `ia/provedores/gemini.py` e mantém
o provider falso para testes. A auditoria e a cota continuam sendo
aplicadas pela porta única.
```

## Rodapé

Use o rodapé para referências e mudanças incompatíveis:

```text
Refs: #123
Closes: #456
BREAKING CHANGE: altera o formato público da configuração
```

Use `BREAKING CHANGE` quando consumidores, APIs, comandos, configurações ou contratos precisarem ser adaptados.

## Checklist

- [ ] O diff staged foi lido com `git status` e `git diff --cached`.
- [ ] O histórico recente foi consultado com `git log -5 --oneline`.
- [ ] O commit trata de um único assunto.
- [ ] O tipo descreve a natureza principal da mudança.
- [ ] O escopo identifica a área afetada quando ajuda.
- [ ] O resumo está no imperativo, em português, sem ponto final.
- [ ] O cabeçalho tem aproximadamente até 72 caracteres.
- [ ] O corpo explica o que mudou e por quê quando necessário.
- [ ] Breaking changes estão declaradas no rodapé.
- [ ] Testes e validações relevantes foram executados.
- [ ] Não há segredos ou dados pessoais na mensagem.

O commit só está correto se `git log -1` mostrar o resumo e o corpo quando ele for exigido. Título sozinho não atende à skill nesses casos.
