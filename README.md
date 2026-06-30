# Lupa

**Lupa** é um software desktop standalone para **análise de conteúdo e métricas textuais** de arquivos PDF, DOCX e TXT, de forma padronizada, auditável e replicável. Voltado à pesquisa acadêmica que exige rigor metodológico na análise de corpus documentais — com ênfase em análise de conteúdo (Bardin) e núcleos de significação (Aguiar & Ozella).

> English documentation is available in [README.en.md](README.en.md). The application interface can be switched between Portuguese and English from the language button in the header.

![Linguagem](https://img.shields.io/badge/Python-3.10%2B-blue)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-lightgrey)
![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen)
![OCR](https://img.shields.io/badge/OCR-Tesseract-yellow)

---

## Visão geral

O Lupa realiza, em lote, a extração e a análise de documentos seguindo regras explícitas e auditáveis. Para cada documento, retorna:

- **Contagem de palavras**: total (todo o texto) e do **corpus analítico** (conteúdo substantivo, com exclusão automática de elementos pré-textuais)
- **Busca de termos e expressões** definidos pelo pesquisador (total e no corpus)
- **Análise de sentimento** (LeIA / VADER-PT) por sentença
- **Emoções discretas** (NRC EmoLex, quando o léxico editável está preenchido)
- **Métricas textuais**: legibilidade (Flesch-PT), diversidade lexical (TTR / Guiraud / MATTR), frequência de palavras-chave
- **Concordância (KWIC)**: contexto ao redor de cada ocorrência dos termos
- **Co-ocorrência**: pares de termos que aparecem na mesma sentença
- **Menções territoriais**: estados, regiões e biomas brasileiros via gazetteer editável
- **Metadados bibliográficos**: título, autores, afiliações, ano, tipo documental e identificadores, com evidências e revisão manual
- **Análises de corpus**: consolidação de autores/instituições, dispersão DP, keyness, NPMI, similaridade e mudança lexical temporal
- **Indicadores de confiabilidade**: páginas com texto, páginas problemáticas, uso de OCR, grau de confiança

Resultados em interface gráfica moderna e exportáveis em XLSX formatado, CSV e JSON, com saídas de resumo e detalhamento (páginas excluídas, sentenças, frequência de palavras, concordância KWIC).

## Principais funcionalidades

- Interface gráfica em PyQt6 com drag-and-drop para múltiplos PDFs, DOCX, TXT e pastas
- Botão de idioma para alternar a interface, ajuda integrada e exportações entre português e inglês
- Processamento assíncrono (não trava a interface) com barra de progresso por arquivo e geral
- OCR automático via Tesseract para PDFs escaneados (idioma português)
- Detecção heurística de páginas pré-textuais (ficha catalográfica, sumário, expediente, lista de ministros etc.)
- Detecção automática offline de título, autores, afiliações, ano, tipo e identificadores a partir de metadados embutidos e cabeçalho
- Revisão manual auditável dos metadados, persistida no projeto; autores e instituições são consolidados no corpus
- A detecção presidencial permanece disponível internamente para compatibilidade, mas fica oculta e desabilitada
- Busca de palavras e expressões com suporte a busca exata entre aspas
- Análise de sentimento em português (LeIA / VADER-PT) por sentença, com detalhamento exportável para análise de conteúdo e núcleos de significação
- Emoções discretas por léxico NRC editável (`data/nrc_emolex_pt.txt`), com trilha de palavras associadas
- Métricas textuais: legibilidade (Flesch-PT), diversidade lexical (TTR / Guiraud / MATTR), frequência e segmentação por coesão lexical
- Concordância KWIC: contexto ao redor de cada ocorrência dos termos de busca (aba "Concordância (KWIC)"), a unidade de contexto da análise de conteúdo
- Co-ocorrência de termos por sentença e síntese temporal por ano do corpus
- Central com 14 gráficos interativos, incluindo autores, instituições, dispersão DP, keyness, similaridade, NPMI, mudança lexical e diagnóstico de sentimento
- Menções territoriais brasileiras via `data/gazetteer_br.json`
- Salvar e abrir projetos `.lupa.json` com arquivos, termos, categorias e flags
- Exportação em XLSX formatado, CSV interoperável (`;`, `utf-8-sig`) e JSON para arquivamento/reuso em R ou Python
- Documentação integrada (atalho F1) explicando todas as regras e fluxos
- Aplicação totalmente offline; nenhum dado é enviado a serviços externos

## Capturas de tela

> Adicione aqui screenshots da interface principal, do diálogo de ajuda e de um XLSX exportado.

---

## Instalação

### Opção 1: Usuário final (instalador Windows)

Execute `LupaSetup-1.0.1-x64.exe`. A instalação é feita por usuário em
`%LOCALAPPDATA%\Programs\Lupa`, sem exigir privilégios administrativos, e cria
atalhos no Menu Iniciar e, opcionalmente, na Área de Trabalho.

O instalador inclui o runtime Python, as dependências do Lupa e o Tesseract OCR.
Windows 10 1809 ou posterior, em arquitetura x64, é necessário.

### Opção 2: Desenvolvimento (a partir do código)

**Requisitos:**

- Python 3.10 ou superior
- Windows 10/11 (testado); Linux/macOS provavelmente compatíveis com ajustes
- Tesseract-OCR instalado (opcional, apenas para PDFs escaneados)

**Passos:**

```bash
git clone https://github.com/<usuario>/Lupa.git
cd Lupa
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

### Tesseract (OCR)

Necessário apenas se você for processar PDFs escaneados (apenas imagem).

1. Baixe a versão para Windows em: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Durante a instalação, marque o pacote de idioma **português** (`por`)
3. Mantenha o caminho padrão `C:\Program Files\Tesseract-OCR` para detecção automática

O software detecta o Tesseract na inicialização e habilita/desabilita a opção de OCR conforme disponibilidade.

---

## Como usar

### Fluxo básico

1. Em **Corpus**, arraste documentos para a área pontilhada ou clique em **Adicionar arquivos**. Pastas também são aceitas (PDF, DOCX e TXT são incluídos).
2. No painel **Configuração da análise**, informe termos/categorias e selecione os módulos desejados.
3. Ative o OCR apenas quando houver PDFs escaneados e clique em **Processar corpus**.
4. A área **Resultados** é aberta ao final com o resumo do lote, a tabela auditável, detalhes e exportação.
5. Use **Exploração** na barra lateral para comparar documentos, filtros e séries sem sair da janela principal.

### Sintaxe da busca de termos

| Entrada                    | Comportamento                                              |
|----------------------------|------------------------------------------------------------|
| `clima`                    | Palavra simples, accent-insensitive e case-insensitive     |
| `mudança do clima`         | Sequência permitindo espaços variáveis entre as palavras   |
| `"efeito estufa"`          | Busca exata da expressão, entre limites de palavra         |
| `# comentário`             | Linha ignorada                                             |
| (linha em branco)          | Ignorada                                                   |

**Exemplo:**

```text
# Termos relacionados a mitigação
carbono
desmatamento
"efeito estufa"
"mudança do clima"
mitigação

# Termos relacionados a adaptação
adaptação
resiliência
"perdas e danos"
```

A busca é insensível a acentos e maiúsculas/minúsculas. Cada termo retorna duas contagens: uma considerando o PDF completo e outra considerando apenas o corpus analítico.

### Formatos aceitos

- **PDF**: extração por PyMuPDF; se o documento for escaneado, o OCR Tesseract pode ser aplicado.
- **DOCX**: extração de parágrafos via `python-docx`; como o formato não expõe páginas impressas, o Lupa cria blocos aproximados de até 3000 caracteres.
- **TXT**: blocos separados por quebras duplas de linha; blocos muito grandes são divididos em partes de até 3000 caracteres.

Em DOCX/TXT, o número de "página" nos detalhes representa bloco textual, não página impressa.

### Regras de contagem de palavras

**Contam como palavra:**

- Sequências de letras (incluindo acentuadas): *política*, *açúcar*
- Palavras hifenizadas como unidade lexical: *cooperação-internacional*
- Siglas formadas por letras: *ONU*, *FMI*, *SUS*, *PIB*
- Abreviações com letras

**Não contam:**

- Números isolados (*2024*, *15*)
- Algarismos romanos como marcadores de capítulo (*III*, *IV*, *XIV*)
- Pontuação e símbolos
- Caracteres soltos provenientes de erro de OCR

### Detecção do corpus analítico

O software identifica automaticamente, com base em palavras-chave e heurísticas, páginas a serem excluídas da contagem do corpus analítico:

- Capa e folha de rosto
- Ficha catalográfica (ISBN, CDD, CDU, Biblioteca da Presidência)
- Sumário ou Índice (detectado também por padrão de linhas pontilhadas)
- Expediente
- Listas de ministros e autoridades
- Páginas em branco

A aba *Páginas Excluídas* do arquivo XLSX exportado contém a lista completa e o motivo de cada exclusão, permitindo auditoria manual.

### Concordância (KWIC)

Para cada termo de busca, a opção **Concordância (KWIC)** (*Keyword-In-Context*,
ligada por padrão) registra o **contexto** ao redor de cada ocorrência — algumas
palavras à esquerda, o termo, e algumas palavras à direita. Diferente da
contagem, é uma saída **qualitativa**: permite ler cada ocorrência em seu
contexto, a *unidade de contexto* da análise de conteúdo de Bardin.

- Requer ao menos um termo de busca; usa a mesma correspondência da busca de
  termos (sem distinção de acentos, frases de várias palavras suportadas).
- A grafia original das palavras de contexto é preservada na exportação.
- Resultados na aba **"Concordância (KWIC)"** do XLSX: nº do documento, arquivo,
  página, termo, contexto à esquerda, ocorrência e contexto à direita.

Referência: Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.

### Co-ocorrência de termos

Quando há pelo menos dois termos de busca, o Lupa conta pares que aparecem na
mesma sentença do corpus analítico. A aba **"Co-ocorrência"** mostra termo A,
termo B e número de sentenças. É uma medida descritiva de associação textual,
não evidência de causalidade.

### Métricas textuais

Conjunto de medidas (caixa "Métricas textuais", ligada por padrão) calculadas
sobre o corpus analítico e exportadas no XLSX. Voltadas à análise de conteúdo e
à identificação de núcleos de significação.

- **Legibilidade — Flesch adaptado ao português:**
  `ILF = 248,835 − 1,015 × (palavras/frases) − 84,6 × (sílabas/palavras)`.
  Classes: Muito fácil (≥75), Fácil (50–75), Difícil (25–50), Muito difícil (<25).
  A contagem de sílabas usa heurística de grupos vocálicos (aproximada).
- **Diversidade lexical:** TTR, Índice de Guiraud e MATTR em janelas móveis. O tamanho efetivo e a quantidade de janelas são exportados.
- **Frequência de palavras-chave:** palavras de conteúdo mais frequentes, após
  remoção de stopwords (lista editável em `data/stopwords_pt.txt`). As 10 mais
  frequentes vão para a tabela; as 30 mais frequentes, para a aba
  **"Frequência de Palavras"** — base quantitativa da análise de conteúdo.

**Referências metodológicas:**

- Martins, T. B. F. et al. (1996). *Readability formulas applied to textbooks in
  Brazilian Portuguese*. Notas do ICMC-USP, n. 28.
- Guiraud, P. (1954). *Les caractères statistiques du vocabulaire*. Paris: PUF.
- Templin, M. (1957). *Certain language skills in children*. University of
  Minnesota Press.
- Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.

### Emoções discretas (NRC)

A análise **Emoções (NRC)** usa um arquivo editável em
`src/core/data/nrc_emolex_pt.txt`, no formato `palavra<TAB>emocao`, para contar
oito emoções: alegria, tristeza, raiva, medo, confiança, repulsa, surpresa e
antecipação. O arquivo é distribuído vazio por padrão para respeitar os termos
do NRC Word-Emotion Association Lexicon; quando preenchido pelo pesquisador, o
XLSX inclui a aba **"Emoções (Palavras)"** com a trilha de auditoria.

Referência: Mohammad, S. M. & Turney, P. D. (2013). *Crowdsourcing a
Word-Emotion Association Lexicon*. Computational Intelligence, 29(3).

### Menções territoriais

O Lupa conta menções a estados, regiões e biomas brasileiros usando o gazetteer
editável `src/core/data/gazetteer_br.json`. Variantes longas têm prioridade
sobre variantes curtas para evitar dupla contagem no mesmo trecho. A saída
aparece na coluna "Menções territoriais" e na aba **"Menções Territoriais"**.

### Síntese temporal do corpus

Quando o lote possui dois ou mais anos distintos, o XLSX inclui a aba
**"Síntese por Ano"**: número de documentos, palavras do corpus, médias
descritivas de sentimento/legibilidade e contagens por termo/categoria. A
janela principal habilita as áreas **Resultados** e **Exploração** após o
processamento.

### Gráficos interativos

A área **Exploração** oferece uma central visual baseada em `QPainter`, sem
dependências pesadas e totalmente offline. Estão disponíveis:

- **Série temporal:** combina volume, sentimento, legibilidade, termos e categorias por ano.
- **Comparação entre documentos:** palavras, termo, categoria, território, emoção ou palavra-chave selecionada.
- **Sentimento:** barras empilhadas de sentenças positivas, neutras e negativas, por documento ou ano.
- **Dispersão lexical:** legibilidade × TTR; tamanho do ponto representa palavras e cor representa sentimento.
- **Matriz de coocorrência:** heatmap simétrico dos pares de termos na mesma sentença.
- **Perfil territorial:** ranking de estados, regiões e biomas mencionados.

Os controles permitem filtrar ano/documento, normalizar contagens por mil
palavras, ocultar séries pela legenda, aplicar zoom com a roda do mouse, copiar
os dados exibidos e exportar o gráfico em PNG. Clicar em uma barra ou ponto de
documento abre seus detalhes. Os gráficos são descritivos: não representam
inferência estatística nem relação causal.

### Detecção de presidente (legada)

A identificação do chefe de Estado permanece no motor para compatibilidade com
projetos históricos, mas a opção fica oculta e desabilitada para corpora gerais.
A coluna "Presidente" é omitida da tabela e do XLSX.

A lista é externa ao código, em `src/core/data/presidents.json`, e pode ser
editada para adaptar a ferramenta a outros países ou períodos:

```json
{
  "presidents": [
    {
      "canonical": "Nome Oficial",
      "start": 2023,
      "end": 2026,
      "variants": ["Nome Oficial", "Apelido"]
    }
  ]
}
```

- `start`/`end`: anos do mandato (AAAA), usados para desambiguar pelo ano do documento.
- `variants`: grafias buscadas (sem distinção de maiúsculas) no início do documento.

Se o arquivo estiver ausente ou inválido, a detecção apenas retorna vazio — o
restante da análise continua normalmente.

### Grau de confiança

| Grau   | Critério                                                              |
|--------|-----------------------------------------------------------------------|
| Alto   | ≥95% das páginas com texto extraído; pouco ou nenhum OCR              |
| Médio  | 80–95% das páginas com texto; ou uso intensivo de OCR                 |
| Baixo  | Menos de 80% das páginas com texto extraído                           |

### Análise de sentimento

A análise de sentimento usa um modelo **baseado em regras e léxico** (VADER), o
que garante **transparência e reprodutibilidade**: cada escore é rastreável até a
palavra e a regra que o produziram — propriedade desejável em pesquisa
qualitativa interpretativa, ao contrário de modelos de "caixa-preta".

- **Método:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*) — léxico
  validado por juízes humanos combinado a heurísticas de negação, intensificadores,
  ênfase em maiúsculas e pontuação. Produz um escore `compound` normalizado em
  `[-1, +1]`.
- **Adaptação ao português:** **LeIA** (*Léxico para Inferência Adaptada*), fork do
  VADER para o português brasileiro (léxico e regras vendorizados no projeto,
  licença MIT, totalmente offline).
- **Unidade de análise:** a **sentença**. Cada sentença recebe escore e classe
  (Positivo `compound ≥ 0,05`; Negativo `≤ -0,05`; Neutro caso contrário). Por
  documento, são reportados a classe geral, o composto médio e o percentual de
  sentenças positivas/negativas/neutras.
- **Saída para análise qualitativa:** o XLSX inclui a aba **"Sentimento
  (Sentenças)"** com cada sentença, página, escore e classe. Esse detalhamento
  fornece as **unidades de registro** da Análise de Conteúdo (Bardin) e os
  **pré-indicadores afetivos** dos Núcleos de Significação (Aguiar & Ozella),
  permitindo agrupar trechos carregados de afeto em indicadores e núcleos.

A análise pode ser ligada/desligada por uma caixa de seleção na interface.

**Referências metodológicas:**

- Hutto, C. J. & Gilbert, E. E. (2014). *VADER: A Parsimonious Rule-based Model for
  Sentiment Analysis of Social Media Text*. ICWSM-14. Ann Arbor, MI.
- Almeida, R. J. de A. *LeIA — Léxico para Inferência Adaptada*.
  <https://github.com/rafjaa/LeIA>
- Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.
- Aguiar, W. M. J. & Ozella, S. (2006; 2013). *Núcleos de significação como
  instrumento para a apreensão da constituição dos sentidos* / *Apreensão dos
  sentidos: aprimorando a proposta dos núcleos de significação*.

### Exportação dos resultados

O Lupa exporta o mesmo lote processado em três formatos:

- **XLSX**: planilha formatada para leitura, auditoria manual e compartilhamento.
- **CSV**: cria uma pasta com `resultados.csv`, `metodologia.txt` e arquivos de detalhe quando houver dados (`sentencas.csv`, `palavras.csv`, `ngramas.csv`, `categorias.csv`, `kwic.csv`, `paginas_excluidas.csv`). Os arquivos usam separador `;` e `utf-8-sig` para compatibilidade com Excel em português.
- **JSON**: arquivo único com `gerado_por`, `metodologia` e `documentos`, preservando os resultados públicos completos de cada documento para arquivamento ou análise em R/Python.

Toda exportação inclui um **relatório metodológico automático** com data, arquivos, formatos, flags, termos/categorias, análises executadas, arquivos de configuração e critérios metodológicos. No XLSX, ele aparece na aba **"Metodologia"**.

### Projetos `.lupa.json`

O menu **Arquivo** permite salvar e abrir projetos de análise. O arquivo guarda
os caminhos dos documentos, o texto bruto dos termos/categorias e as flags das
análises. Ao abrir um projeto, arquivos ausentes são avisados sem impedir o
carregamento dos demais.

### Atalhos de teclado

| Atalho        | Ação                          |
|---------------|-------------------------------|
| `Ctrl+O`      | Adicionar documentos          |
| `Ctrl+S`      | Salvar projeto                |
| `Ctrl+Shift+O`| Abrir projeto                 |
| `Ctrl+E`      | Exportar resultados           |
| `Ctrl+Q`      | Sair                          |
| `F1`          | Abrir documentação integrada  |

---

## Estrutura do projeto

```text
WordCounter/
├── src/
│   ├── main.py                  # entry point
│   ├── core/
│   │   ├── word_counter.py      # regras de contagem (regex Unicode)
│   │   ├── corpus_filter.py     # detecção de páginas a excluir
│   │   ├── metadata_detector.py # detecção de ano/presidente/documento
│   │   ├── term_search.py       # busca de termos e expressões
│   │   ├── ocr_engine.py        # wrapper Tesseract + fallback
│   │   ├── pdf_processor.py     # orquestrador
│   │   └── exporter.py          # exportação XLSX formatada
│   └── gui/
│       ├── main_window.py       # janela principal
│       ├── help_dialog.py       # diálogo de ajuda integrada
│       ├── workers.py           # QThread workers (processamento assíncrono)
│       └── styles.py            # stylesheet (tema escuro Catppuccin Mocha)
├── requirements.txt
├── build.bat                    # script PyInstaller (Windows)
├── LICENSE
└── README.md
```

### Tecnologias

- **PyQt6** — Interface gráfica
- **PyMuPDF (fitz)** — Extração de texto e renderização de páginas
- **pytesseract** + **Pillow** — Wrapper Python sobre Tesseract para OCR
- **openpyxl** — Geração de XLSX
- **regex** — Suporte Unicode avançado para classes `\p{L}`
- **PyInstaller** — Empacotamento em executável (build)

---

## Build do executável

Em ambiente Windows com Python e dependências instaladas:

```cmd
build.bat
```

Saída: `dist\Lupa.exe`

Para gerar um instalador local, veja a pasta [`installer/`](installer/) (script
PowerShell `install.ps1`, sem dependências, e script Inno Setup `Lupa.iss`).

Se o Tesseract estiver instalado em `C:\Program Files\Tesseract-OCR`, o script o embarca automaticamente no executável. Caso contrário, o usuário final precisará instalá-lo separadamente.

---

## Reprodutibilidade

Toda a contagem segue regras determinísticas, sem componentes aleatórios. Processar os mesmos PDFs nas mesmas condições produz resultados idênticos. Diferenças entre execuções só podem ocorrer quando o OCR é aplicado a páginas marginais cuja qualidade de imagem varia o reconhecimento.

A documentação completa dos critérios de contagem, exclusão e classificação de confiança está embutida no software (atalho F1) e neste README, garantindo auditabilidade do processo.

---

## Testes

A suíte usa **pytest** e cobre o motor de contagem, a busca de termos, o filtro de
corpus, a detecção de metadados, os analisadores (incluindo sentimento) e a
exportação, além de um teste de integração do pipeline completo sobre um PDF
sintético.

```bash
pip install -r requirements-dev.txt
pytest                       # executa a suíte
pytest --cov=src/core        # com relatório de cobertura
```

Cobertura atual do código próprio (excluindo a biblioteca vendorizada LeIA): **~92%**.

---

## Limitações conhecidas

- A detecção de páginas pré-textuais é heurística e pode produzir falsos positivos em layouts atípicos. Verifique sempre a aba *Páginas Excluídas* do XLSX exportado.
- A detecção automática de ano e presidente baseia-se em padrões textuais; em PDFs com baixa qualidade de extração, pode falhar (campos retornam vazios).
- O OCR adiciona tempo significativo de processamento (segundos por página). Use apenas quando necessário.

---

## Autoria

Trabalho desenvolvido no âmbito do Programa de Pós-graduação em Desenvolvimento Territorial e Meio Ambiente da Universidade de Araraquara (UNIARA):

- Adriano Marques Gonçalves — Universidade de Araraquara (UNIARA)
- Thaís Angeli — Secretaria de Educação de Araraquara

---

## Licença

MIT — consulte o arquivo [LICENSE](LICENSE) para detalhes.

---

## Citação

Caso utilize este software em sua pesquisa, sugere-se a seguinte citação:

> GONÇALVES, A. M.; ANGELI, T. *Lupa: ferramenta para análise de conteúdo e métricas textuais de corpora documentais em PDF*. Araraquara: UNIARA, 2026.

> Lupa deriva do *Contador de Palavras*. Um DOI próprio será atribuído em publicação futura.
