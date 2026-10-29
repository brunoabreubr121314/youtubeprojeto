# Agenda de Conteúdo · documentação completa

Documento para retomar o projeto em outro chat ou com outro assistente. Explica o que o site faz, como ele funciona por dentro, onde está cada peça e como fazer reparos sem perder dados.

Dono: Bruno (GitHub `brunoabreubr121314`, Cloudflare `brunovisuals`).
Última atualização deste documento: 29/10/2026.

---

## 1. O que é

Um site para gerenciar a **programação de conteúdo** de vários canais (YouTube, Instagram etc.). O site não guarda roteiro nem detalhes técnicos, só **o que vai sair, em qual canal e quando**.

Tem duas partes:

| Parte | Endereço | Quem usa | O que faz |
|---|---|---|---|
| Página pública | https://canais.obunker.pro | Amigos e colaboradores | Vê a agenda e marca o check de "agendado no YouTube". Não edita nada. |
| Página do colaborador | https://canais.obunker.pro/<nome> (ex.: `/pedro`) | Cada colaborador | Igual à pública, mas só com os canais daquele colaborador. |
| Área de edição | https://canais.obunker.pro/admin123 | Só o Bruno | Programa, edita e exclui temas, gerencia canais e publica para a página pública. |

Endereço alternativo (redireciona para o domínio): https://brunoabreubr121314.github.io/youtubeprojeto/

---

## 2. Visão geral da arquitetura

```
             ┌──────────────────────────── GitHub (repo público) ───────────────────────────┐
             │  brunoabreubr121314/youtubeprojeto  (branch main, GitHub Pages ligado)       │
             │                                                                              │
             │   index.html ............ página pública (somente leitura)                   │
             │   admin123/index.html ... área de edição                                     │
             │   data.json ............. A AGENDA (canais + temas). Fonte da verdade.       │
             │   CNAME ................. canais.obunker.pro                                 │
             │   fonte/ ................ código-fonte e script que gera os dois HTML         │
             └──────────────────────────────────────────────────────────────────────────────┘
                     ▲  grava data.json pela API do GitHub          ▲ lê data.json
                     │  (chave pessoal salva no navegador)          │ (a cada 2 min)
              ┌──────┴──────┐                                ┌──────┴──────┐
              │  /admin123  │                                │  página     │
              │  (Bruno)    │                                │  pública    │
              └──────┬──────┘                                └──────┬──────┘
                     │ lê/grava checks                              │ lê/grava checks
                     ▼                                              ▼
             ┌──────────────────────── Cloudflare ──────────────────────────────┐
             │ Worker  agenda-checks  → https://agenda-checks.brunovisuals.workers.dev/ │
             │ KV namespace agenda-checks (binding CHECKS) guarda os checks     │
             │ DNS obunker.pro: CNAME  canais → brunoabreubr121314.github.io    │
             │                  (nuvem cinza / DNS only)                        │
             └──────────────────────────────────────────────────────────────────┘
```

Tudo é gratuito: GitHub Pages (repositório público), Cloudflare Workers e KV no plano grátis.

---

## 3. Arquivos do repositório

| Arquivo | Para que serve | Pode editar à mão? |
|---|---|---|
| `index.html` | Página pública. **Gerado** pelo `fonte/build.py`. | Não. Edite `fonte/base.html` e rode o build. |
| `404.html` | Página do colaborador. **Gerado** pelo `fonte/build.py`. O GitHub Pages serve esse arquivo para qualquer endereço que não existe, e ele lê o nome no endereço. | Não. Mesmo motivo. |
| `admin123/index.html` | Área de edição. **Gerado** pelo `fonte/build.py`. | Não. Mesmo motivo. |
| `data.json` | A agenda publicada. A área de edição reescreve esse arquivo a cada mudança. | Só para restaurar uma versão antiga (veja a seção 9). |
| `CNAME` | Domínio personalizado do GitHub Pages. | Só se trocar o domínio. |
| `.nojekyll` | Faz o GitHub Pages servir os arquivos como estão. | Não. |
| `fonte/base.html` | **Código-fonte único** das duas páginas (HTML + CSS + JS num arquivo só). | Sim. É aqui que se mexe. |
| `fonte/build.py` | Gera as duas páginas a partir do `base.html`. | Sim, quando a diferença entre pública e admin mudar. |
| `fonte/worker.js` | Código do Worker do Cloudflare (checks). Cópia de referência; o que roda está no Cloudflare. | Sim, mas precisa colar de novo no Cloudflare. |
| `DOCUMENTACAO.md` | Este documento. | Sim. |

Como os arquivos de `fonte/` ficam no GitHub Pages, eles também podem ser acessados pelo endereço do site. Não há nada secreto neles.

---

## 4. Formato dos dados

### `data.json`

```json
{
  "canais": [
    {
      "id": "mt",
      "nome": "Mentalista",
      "colab": "Pedro",
      "link": "https://www.instagram.com/...",
      "cor": "roxo",
      "ordem": 1
    }
  ],
  "posts": [
    {
      "id": "pmvkzo9objyl6",
      "tema": "Ele esfriou de uma hora pra outra",
      "canal": "mt",
      "data": "2026-10-23",
      "hora": "09:30",
      "link": "https://drive.google.com/...",
      "status": "planejado",
      "criado": 1792761104891
    }
  ],
  "atualizado": "2026-10-25T22:51:01.541Z"
}
```

- `canais[].id`: identificador fixo. Os temas apontam para ele em `posts[].canal`. Os canais criados pelo site ganham ids como `c<timestamp>`; os três originais eram `wl`, `mt` e `li`.
- `canais[].cor`: uma destas: `verde`, `roxo`, `laranja`, `azul`, `rosa`, `ambar`, `ciano`, `vermelho`.
- `canais[].colab`: nome do colaborador responsável (opcional). A lista de colaboradores do formulário é montada a partir dos nomes já usados.
- `canais[].link`: link do canal (opcional). Quando existe, o nome do canal vira link nos cartões.
- `canais[].plat`: campo antigo (plataforma), que pode aparecer em canais antigos. Não é mais usado.
- `posts[].data`: no formato `AAAA-MM-DD`. `hora` é opcional (`HH:MM`).
- `posts[].link`: link do Drive (opcional). Quando existe, o título do tema vira link.
- `posts[].status`: legado. Temas com `"publicado"` saem da fila; não há mais botão para isso.

### Checks (no Cloudflare KV, chave `checks`)

```json
{ "pmvkzo9objyl6": { "em": "2026-10-25T23:29:37.279Z" } }
```

O id do tema está presente quando ele foi marcado como agendado no YouTube; desmarcar remove a entrada.

---

## 5. Funcionalidades

### Comum às duas páginas
- Relógios ao vivo de **Brasília** e **Nova York**.
- **Cartões por canal**: nome (clicável se tiver link), colaborador e etiqueta de situação da fila: verde "Em dia" (7 dias ou mais de conteúdo), laranja "Acaba em X dias" ou vermelha "Fila vazia". Mostram também o número de **Programados** (com "X de Y agendados"), a data **Fila até** e a faixa do **próximo tema**, com o botão **+N** que abre a lista dos seguintes.
- **Calendário mensal** com os temas na cor do canal. O dia de hoje tem contorno azul. No celular, mostra bolinhas coloridas em vez dos títulos.
- Painéis do **dia selecionado** e dos **Próximos 14 dias**.
- **Check "agendado no YouTube"**: um círculo ao lado de cada tema. Fica verde ✓ quando marcado, é compartilhado entre todos e é atualizado a cada 45 segundos.
  Ao clicar, abre uma confirmação (`<dialog id="ckDlg">`): "Você é **<colaborador do canal>** e já agendou esse vídeo no YouTube?", com **Sim** e **Não**. Esc, clicar fora ou **Não** fecham sem marcar. Para desmarcar, pergunta "Remover o check de agendado desse vídeo?". Se o canal não tem colaborador, a pergunta omite o nome. Funciona em PC e celular (no celular aparece perto da parte de baixo da tela).
- Títulos com link do Drive aparecem com ↗ e abrem em nova guia.
- Modo claro e escuro automáticos, conforme o sistema.

### Só na página pública
- Nenhum botão de edição.
- **Ícone de olho** em cada cartão, que esconde os temas daquele canal. A escolha fica salva no navegador de cada pessoa (`localStorage` `agenda.hidden`).
- Recarrega `data.json` a cada 2 minutos.
- Mostra "Atualizado dd/mm às hh:mm".

### Só na página do colaborador (/<nome>)
- Mostra só os canais cujo campo **Colaborador** bate com o nome no endereço. Não diferencia maiúsculas nem acentos, e espaços viram hífen (`Pedro` → `/pedro`, `João Silva` → `/joao-silva`).
- Título vira "Agenda de <nome>". Calendário, próximos 14 dias e checks mostram só os temas desses canais.
- Endereço sem canais mostra "Não encontrei canais para …".
- Não precisa criar nada: ao pôr um colaborador num canal pelo admin, o endereço dele já funciona.
- É só um filtro de visualização. Como o `data.json` e a página principal são públicos, o colaborador ainda consegue ver os outros canais se abrir a página principal.
- `noindex` para não aparecer no Google.

### Só na área de edição (/admin123)
- Formulário **Programar tema**: tema, canal, data, horário (opcional) e link do Drive (opcional).
- **Editar** e **Excluir** temas. Excluir pede um segundo clique para confirmar. Também dá para arrastar um tema para outro dia no calendário.
- **Gerenciar canais**: adicionar, editar e remover canais, com nome, colaborador (escolhido da lista ou criado novo), link e cor. Remover um canal apaga os temas dele (pede confirmação). Não é possível remover o último canal.
- **Publicação automática** para a página pública (seção 6).
- **Baixar backup** e **Restaurar backup** (arquivo JSON com canais e temas).
- `noindex` para não aparecer no Google.

---

## 6. Como a publicação funciona (área de edição)

1. Toda mudança é salva primeiro no navegador (`localStorage`: `agenda.posts`, `agenda.canais`) e marca `agenda.dirty = "1"`.
2. Cerca de 2 segundos depois, a página grava o `data.json` no GitHub pela API:
   `PUT https://api.github.com/repos/brunoabreubr121314/youtubeprojeto/contents/data.json`
   usando a **chave pessoal** (token *fine-grained*) salva em `localStorage` `agenda.ghtoken`.
3. O GitHub Pages leva mais ou menos 1 minuto para servir a versão nova. A página pública lê com `?t=<timestamp>` para escapar do cache.

**Proteção contra sobrescrever** (foi adicionada depois de um incidente em que uma aba antiga apagou os temas):
- A página guarda o `sha` da versão do `data.json` em que está baseada (`agenda.baseSha`).
- Antes de publicar, confere o `sha` atual no GitHub. Se for diferente, alguém (outra aba ou outro aparelho) publicou no meio do caminho. Nesse caso a página **não publica** e mostra o aviso "A agenda foi alterada em outra aba ou aparelho", com os botões **Usar a versão online** e **Publicar a versão deste aparelho**.
- Ao voltar para uma aba parada, se não houver mudanças locais pendentes, a página puxa a versão mais nova sozinha.
- Ao abrir, com a chave configurada, lê o `data.json` direto da API do GitHub, sem o atraso do Pages.

**Chave do GitHub (token)**
- Criada em https://github.com/settings/personal-access-tokens/new
- Repository access: **Only select repositories** › `youtubeprojeto`
- Permissions › Repository permissions › **Contents: Read and write**
- Expiration: o Bruno escolheu **sem validade**.
- Fica salva só no navegador onde foi colada. Para editar de outro aparelho, é preciso colar a chave lá também (botão **Conectar GitHub**).
- Sem a chave, a área de edição funciona, mas só salva no próprio aparelho ("Salvo só neste aparelho").
- Nunca colocar essa chave no código nem num arquivo do repositório. O repositório é público.

---

## 7. Checks compartilhados (Cloudflare Worker)

- Worker: `agenda-checks` na conta Cloudflare `brunovisuals`.
- Endereço: `https://agenda-checks.brunovisuals.workers.dev/`
- Binding: **KV namespace** `agenda-checks` com o nome de variável **`CHECKS`**.
- Código: `fonte/worker.js`.
- API:
  - `GET /` devolve o mapa de checks.
  - `POST /` com o corpo `{"id":"<id do tema>","done":true|false}` marca ou desmarca e devolve o mapa atualizado.
- Qualquer pessoa pode marcar e desmarcar checks (é de propósito, para os amigos), mas não pode alterar temas nem canais.
- O endereço está na constante `CHECK_URL` em `fonte/base.html`. Se ela estiver vazia, os checks ficam escondidos.
- O KV tem consistência eventual: em lugares diferentes do mundo, uma marcação pode levar alguns segundos para aparecer.

---

## 8. Como alterar o site (para quem for dar manutenção)

1. Clone o repositório: `git clone https://github.com/brunoabreubr121314/youtubeprojeto`
2. Edite **`fonte/base.html`**. É um arquivo único com HTML, CSS e JS, sem bibliotecas externas além das Google Fonts (Bricolage Grotesque, Figtree, JetBrains Mono).
3. Rode na raiz do repositório: `python3 fonte/build.py`. Isso regenera `index.html`, `admin123/index.html` e `404.html`.
4. Antes de commitar, puxe o repositório (`git pull`), porque a área de edição faz commits "Atualiza agenda" o tempo todo.
5. **Nunca sobrescreva `data.json`** com uma cópia antiga ao fazer deploy de código.
6. Faça commit e push. O GitHub Pages publica em mais ou menos 1 minuto. Peça um **Ctrl+F5** a quem estiver com a página aberta.

### Como o `build.py` funciona
Ele faz substituições de texto exatas em `base.html` (a função `rep()` falha se não encontrar o trecho) e gera duas versões:
- **Pública** (`READONLY = true`, `DATA_URL = "data.json"`): adiciona a classe `ro` ao `<html>`, o que esconde tudo com a classe `admin-only` (formulário, gerenciar canais, backup). Desliga arrastar e editar. Lê só o `data.json`. Inclui o olho.
- **Colaborador** (`404.html`, `READONLY = true`, `DATA_URL = "/data.json"`): igual à pública, mais a função `slug()`, a constante `COLAB` (tirada do endereço) e o filtro de canais e temas logo depois de carregar o `data.json`.
- **Admin** (`READONLY = false`, `DATA_URL = "../data.json"`): adiciona o cartão "Publicar para os amigos" e os botões de publicação, toda a lógica de API do GitHub, a proteção de conflito e o `noindex`.

Se uma alteração em `base.html` mudar um trecho que o `build.py` procura, o build falha com `AssertionError` mostrando o trecho. Basta ajustar o texto procurado no `build.py`.

### Pontos de atenção no código
- O JS chama `render()` para redesenhar tudo: `renderQueues`, `renderCal`, `renderDay`, `renderUp`, `renderChans` e `renderMg`.
- `CH` e `ORDER` são montados por `buildCH()` a partir de `chans`.
- As cores vêm de tokens CSS `--c-<cor>` e `--c-<cor>-s`, aplicados por elemento via `style="--c:...;--cs:..."` com a função `cv()`.
- Links passam por `safeUrl()`, que só aceita http e https e completa com `https://` quando falta.
- Existe código morto herdado da primeira versão (dentro do Claude), com as variáveis `store`/`chStore`. Ele não roda, porque `store` é sempre `null`.

---

## 9. Problemas comuns e soluções

| Sintoma | Causa provável | Solução |
|---|---|---|
| Mudança não aparece para os amigos | O Pages leva cerca de 1 minuto, ou a página está em cache | Esperar 1 minuto e apertar Ctrl+F5. Ver no admin se o topo diz "Publicado". |
| Admin mostra "Salvo só neste aparelho" | Chave não configurada neste navegador | Clicar em **Conectar GitHub** e colar a chave. |
| "Chave do GitHub inválida ou sem permissão" | Token expirado, apagado ou sem Contents: Read and write | Criar outra chave (seção 6) e colar de novo. |
| "A agenda foi alterada em outra aba ou aparelho" | Duas abas ou aparelhos editando | Escolher **Usar a versão online** (descarta as mudanças locais) ou **Publicar a versão deste aparelho** (sobrescreve a online). |
| Temas ou canais sumiram | Uma versão antiga publicou por cima | Restaurar pelo histórico: `git log -- data.json`, achar a versão boa e rodar `git show <commit>:data.json > data.json`, depois commit e push. Depois, Ctrl+F5 no admin e **Usar a versão online**. |
| Checks não aparecem | `CHECK_URL` vazio ou Worker fora do ar | Abrir o endereço do Worker: deve mostrar `{}` ou um JSON. Conferir o binding `CHECKS` no Cloudflare. |
| Cadeado ou HTTPS com erro | Certificado do GitHub Pages | Settings › Pages: Custom domain `canais.obunker.pro` com DNS verificado e **Enforce HTTPS** marcado. O DNS no Cloudflare precisa estar com a **nuvem cinza**. |
| "DNS check unsuccessful" no GitHub | Checagem feita antes da propagação | Clicar em **Check again** depois de alguns minutos. O CNAME correto é `canais → brunoabreubr121314.github.io`. |

---

## 10. Segurança, resumo

- O repositório é público, então qualquer pessoa pode ver o código e descobrir o endereço `/admin123`. Quem protege a edição é a **chave do GitHub**, que fica só no navegador do Bruno.
- Sem a chave, alguém no `/admin123` só altera uma cópia no próprio navegador, que ninguém mais vê.
- Os checks são abertos de propósito: qualquer pessoa com o link marca e desmarca.
- Se a chave vazar: apagar em https://github.com/settings/personal-access-tokens e criar outra.

---

## 11. Histórico do que foi feito

1. Primeira versão criada como artifact dentro do Claude: calendário, cadastro de temas e três canais (Wealth Mind, Mentalista, Turma da Lili). O canal tinha sido chamado de "Wealth Logic" e foi corrigido para "Wealth Mind".
2. Adicionados os relógios de Brasília e Nova York e o destaque azul no dia de hoje.
3. Cartões dos canais redesenhados: etiqueta de situação, números grandes e lista expansível dos próximos temas.
4. Versão para baixar (HTML offline) com backup e restauração.
5. Gerenciamento de canais: adicionar, editar e remover, com cor.
6. Publicado no GitHub Pages (repo `youtubeprojeto`) e ligado ao domínio `canais.obunker.pro` via CNAME no Cloudflare.
7. Separação entre **página pública somente leitura** e **/admin123**, com publicação automática pela API do GitHub e chave fine-grained.
8. Campo "Plataforma" trocado por **Colaborador** (lista reutilizável de nomes).
9. **Link do canal** (nome clicável) e **link do Drive** nos temas.
10. Olho para esconder canal: removido e depois recolocado, só na página pública.
11. Incidente: uma aba antiga publicou uma versão vazia. Restaurado pelo histórico, e criada a **proteção contra sobrescrever** (comparação de `sha`).
12. Ícone da aba (favicon).
13. **Check "agendado no YouTube"** compartilhado, via Cloudflare Worker e KV.
14. Código-fonte e script de build guardados em `fonte/`, junto com este documento.
15. Confirmação antes de marcar ou desmarcar o check ("Você é <colaborador>…?", com Sim e Não; Esc fecha).
16. Página do colaborador: `canais.obunker.pro/<nome>` mostra só os canais dele (via `404.html`). Projeto passou a ser mantido no Claude (Cowork).

O artifact original dentro do Claude ("Agenda de Conteúdo") **não está ligado a este site** e ficou desatualizado. Use o site.

---

## 12. Instruções para outro assistente

- Leia este arquivo inteiro antes de mexer em qualquer coisa.
- Para mudar layout ou comportamento: edite `fonte/base.html` e rode `python3 fonte/build.py`. Não edite `index.html` nem `admin123/index.html` diretamente.
- Sempre rode `git pull` antes de commitar, porque a área de edição faz commits "Atualiza agenda" com frequência.
- Não altere nem apague `data.json` sem o Bruno pedir, exceto para restaurar uma versão.
- Não peça a chave do GitHub para colar em código. Ela só pode ficar no navegador do Bruno.
- Teste localmente com `python3 -m http.server` na raiz (abrir `/` e `/admin123/`) antes de publicar. O `http.server` simples não serve o `404.html`; para testar `/<nome>`, use um servidor que devolva o `404.html` nos endereços inexistentes.
- Mudanças no Worker precisam ser coladas no editor do Cloudflare (Workers & Pages › `agenda-checks` › Edit code › Deploy).
