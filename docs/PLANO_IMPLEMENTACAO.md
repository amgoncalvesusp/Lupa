# Lupa — Plano de Implementação (próximas análises)

> **Para a IA implementadora:** este documento é autocontido. Leia a seção
> "Contexto e convenções" antes de qualquer código. Implemente as fases na
> ordem. Cada fase tem arquivos exatos, estruturas de dados, critérios de
> aceite e testes obrigatórios. Não quebre nenhum teste existente
> (91 passando hoje).

---

## Contexto e convenções (LEIA PRIMEIRO)

### O que é o Lupa
Aplicativo desktop Windows (PyQt6) para análise de conteúdo e métricas textuais
de PDFs, voltado a pesquisa acadêmica qualitativa (análise de conteúdo de
Bardin; núcleos de significação de Aguiar & Ozella). Corpus típico: documentos
oficiais brasileiros (Mensagens Presidenciais ao Congresso), mas genérico.

### Restrições inegociáveis
- **100% offline.** Nada de chamadas de rede, APIs ou downloads de modelos.
- **Auditável.** Métodos léxicos/regras com citação publicável; nada de
  caixa-preta. Todo número agregado precisa de trilha de detalhe (aba XLSX
  e/ou aba no diálogo de detalhes).
- **Leve.** O .exe (PyInstaller onefile) tem ~125 MB; não adicionar
  dependências pesadas (proibido: torch, transformers, spacy com modelos).
  Novas dependências só se puras-Python e pequenas; preferir vendorizar
  (padrão em `src/core/analysis/vendor/leia/` — com LICENSE e citação).
- **UI e saídas em PT-BR.** Código/comentários em inglês.

### Arquitetura (pipeline de analisadores plugáveis)
`PDFProcessor.process()` extrai texto uma vez → monta `DocumentContext`
(`filename`, `pages_text`, `analytical_page_numbers`, `total_pages`, `stats`)
→ roda a lista de analisadores → mescla os dicts de saída num resultado por
documento.

Cada analisador (`src/core/analysis/*.py`) implementa o Protocol `Analyzer`
(`base.py`): atributo `name`, método `columns() -> list[ColumnSpec]` e
`run(ctx) -> dict`. Exporter e GUI montam o esquema a partir de `columns()` —
nada de colunas hardcoded.

**Receita para adicionar uma análise (siga sempre):**
1. Novo módulo em `src/core/analysis/` com a classe do analisador
   (docstring com metodologia + citação).
2. Registrar em `build_default_analyzers()` em `src/core/analysis/__init__.py`
   (ordem da lista = ordem das colunas) + `__all__`.
3. Se opcional: flag `detect_X`/parâmetro, encadeado por
   `src/core/pdf_processor.py` → `src/gui/workers.py` →
   `src/gui/main_window.py` (checkbox na linha "ANÁLISES:" do card de opções,
   com tooltip; atributo `self._enable_X` em `start_processing`; repassar em
   `export_results`).
4. Linhas de detalhe → nova aba no XLSX em `src/core/exporter.py`
   (usar helpers `_detail_sheet()` e `_style_detail_row()`; aba só criada se
   houver dados) e, quando útil, nova aba em `src/gui/detail_dialog.py`
   (seguir `_build_keywords_tab` como modelo).
5. Testes em `tests/test_<nome>.py` (pytest, marcador `unit`), sintéticos,
   AAA. Atualizar `tests/test_analysis_factory.py` se o conjunto-padrão mudar.
6. Documentar em `src/gui/help_dialog.py`: seção "Metodologias das análises"
   (o que mede / como funciona / citação) e lista de abas do XLSX.
7. Se houver arquivo de configuração: JSON/TXT editável em
   `src/core/data/` (padrão de `presidents.json`, `stopwords_pt.txt`,
   `document_types.json`), carregado com fallback silencioso para não quebrar
   a análise, resolvendo caminho com `sys.frozen`/`sys._MEIPASS` (ver
   `metadata_detector._data_dir()`). O diretório `data/` inteiro já é
   embarcado pelo `build.bat` e pelo `Lupa.spec` — não precisa mexer no build.

### Comandos (Windows; venv do projeto irmão)
```cmd
:: testes (na raiz do Lupa)
"..\WordCounter\venv_build\Scripts\python.exe" -m pytest
:: cobertura (mínimo 80%; hoje ~93%)
"..\WordCounter\venv_build\Scripts\python.exe" -m pytest --cov=src/core
:: build do exe
"..\WordCounter\venv_build\Scripts\python.exe" -m PyInstaller --noconfirm Lupa.spec
:: instalar localmente
powershell -ExecutionPolicy Bypass -File installer\install.ps1
```

### Estado atual (não reimplementar)
Analisadores existentes: metadata (ano/tipo/presidente), doc_stats, word_count,
readability (Flesch-PT), lexical_diversity (TTR/Guiraud), keywords
(+`word_counts` completo), ngrams (bi/trigramas), sentiment (LeIA/VADER-PT,
por sentença), categories (codificação `NOME: t1, t2`), term_search, kwic
(janela 15). XLSX com 8 abas (incl. TF-IDF corpus-level no exporter).
Diálogo de detalhes por documento (duplo clique) com abas.

Chaves de resultado já usadas (não colidir): `filename, year, document,
president, total_pages, pages_with_text, pages_problematic, ocr_pages_count,
words_total, words_analytical, confidence, observations, excluded_pages,
empty_pages, ocr_pages_list, term_results, category_results, sent_*,
sentiment_sentences, leg_*, lex_*, kw_top, keyword_freq, word_counts,
ngram_top, ngram_freq, kwic`.

Commits: conventional commits em PT (`feat:`, `fix:`, `docs:`...), corpo
explicando o quê/por quê. Um commit por fase.

---

## Fase A — Exportação CSV/JSON (interoperabilidade)

**Objetivo:** abrir a cadeia de análise para R, Python, Iramuteq e arquivamento
de dados de pesquisa (reprodutibilidade).

**Implementação:**
- Novo `src/core/exporter_plain.py`:
  - `export_to_csv(results, output_dir, column_specs=None)` — um CSV principal
    (`resultados.csv`, mesmas colunas da aba 1, separador `;`, encoding
    `utf-8-sig` para Excel BR) + um CSV por detalhe existente
    (`sentencas.csv`, `palavras.csv`, `ngramas.csv`, `categorias.csv`,
    `kwic.csv`, `paginas_excluidas.csv`) — só os que tiverem dados.
  - `export_to_json(results, output_path)` — JSON único:
    `{"gerado_por": "Lupa <versão>", "documentos": [<result dicts completos>]}`,
    `ensure_ascii=False`, indent 2. Remover chaves internas iniciadas com `_`.
- GUI: em `export_results` (main_window), trocar o filtro do
  `QFileDialog.getSaveFileName` para
  `"Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)"` e despachar pela extensão
  escolhida (CSV usa o diretório + prefixo do nome).
- Ajuda: nova subseção em "Estrutura do XLSX exportado" → renomear seção para
  "Exportação (XLSX, CSV, JSON)".

**Testes (`tests/test_exporter_plain.py`):** CSV principal tem cabeçalho e
linha por doc; CSVs de detalhe só quando há dados; JSON round-trip
(`json.load` recupera `filename` e contagens); chaves `_*` ausentes no JSON.

**Aceite:** exportar lote de 2 docs sintéticos nos 3 formatos sem exceção;
91+ testes verdes.

---

## Fase B — Emoções discretas (léxico NRC-PT)

**Objetivo:** além de positivo/negativo, medir 8 emoções (alegria, tristeza,
raiva, medo, confiança, repulsa, surpresa, antecipação) — granularidade afetiva
central para núcleos de significação.

**Metodologia/citação:** NRC Word–Emotion Association Lexicon (EmoLex),
Mohammad & Turney (2013), *Crowdsourcing a Word–Emotion Association Lexicon*,
Computational Intelligence 29(3). Usar a tradução PT do próprio NRC.
Licença: gratuita para pesquisa — incluir termos e atribuição em
`vendor/nrc/README` (se a licença impedir redistribuição, gerar
`data/nrc_emolex_pt.txt` com instruções de download manual + fallback vazio).

**Implementação:**
- `src/core/data/nrc_emolex_pt.txt` — formato TSV: `palavra<TAB>emocao` (uma
  associação por linha, só associações=1; palavras sem acento, minúsculas).
- Novo `src/core/analysis/emotions.py` — `EmotionAnalyzer`:
  - Carrega léxico (padrão `_data_dir()`, fallback dict vazio → análise
    retorna zeros, nunca quebra).
  - `run`: tokeniza corpus analítico (reusar `word_counter.tokenize` +
    `term_search.normalize`), conta acertos por emoção; saída:
    `emo_pct_<emocao>` (percentual de palavras associadas, 1 casa decimal),
    `emo_dominante` (nome PT da emoção com maior contagem ou ""),
    `emotion_words` (dict emoção → lista [(palavra, contagem)] top 10 — trilha
    de auditoria).
  - `columns()`: `emo_dominante` + as 8 `emo_pct_*` (grupo `"sentiment"`).
- Flag `detect_emotions=True` (receita passos 2–3; checkbox "Emoções (NRC)").
- XLSX: aba "Emoções (Palavras)" — `Nº Doc., Arquivo, Emoção, Palavra,
  Contagem` (helper `_detail_sheet`).
- Diálogo de detalhes: aba "Emoções" (tabela emoção/palavra/contagem).
- Ajuda: metodologia (léxico de associação, validação por crowdsourcing,
  limitações: polissemia, cobertura da tradução; mesma recomendação de uso
  como triagem auditável).

**Testes (`tests/test_emotions.py`):** léxico sintético injetado (monkeypatch
do dict) → percentuais e dominante correto; corpus vazio → zeros; palavra com
acento encontrada via normalização; analisador desligado ausente do factory.

**Aceite:** colunas `emo_*` no XLSX e detalhes auditáveis; sem dependência nova.

---

## Fase C — Painel temporal / síntese do corpus

**Objetivo:** o corpus típico é anual — revelar trajetórias (ex.: "clima"
1995→2023) sem sair do Lupa.

**Implementação (pós-processamento, não é analisador):**
- Novo `src/core/corpus_summary.py` — `build_corpus_summary(results) -> dict`:
  - Agrupa por `year` (docs sem ano → grupo "s/ ano").
  - Por ano: nº docs, palavras (soma), sentimento composto médio, legibilidade
    média, % sentenças positivas/negativas, contagem analítica por termo e por
    categoria.
- XLSX: aba "Síntese por Ano" (1 linha por ano, colunas dinâmicas por
  termo/categoria) — escrever em `exporter.py` quando houver ≥2 anos distintos.
- GUI: botão "📈 Síntese do corpus" ao lado de "Ver detalhes" (habilitado com
  ≥2 resultados) → novo `src/gui/summary_dialog.py` com tabela anos × métricas
  e, por termo selecionado (QComboBox), gráfico de barras simples por ano
  (desenhar com QPainter ou barras de texto na tabela — NÃO adicionar
  matplotlib ao runtime do exe).
- Ajuda: subseção "Síntese por ano" (média simples entre documentos do mesmo
  ano; sem inferência estatística — descritivo).

**Testes (`tests/test_corpus_summary.py`):** 3 docs sintéticos em 2 anos →
agregados correto; doc sem ano → grupo "s/ ano"; 1 ano só → aba ausente.

**Aceite:** planilha temporal correta; diálogo abre sem erro (import limpo +
lógica testada).

---

## Fase D — Menções territoriais (gazetteer BR)

**Objetivo:** mapear o foco geográfico de cada documento (estados, regiões,
biomas) — encaixe direto com pesquisa em desenvolvimento territorial.

**Implementação:**
- `src/core/data/gazetteer_br.json`:
  ```json
  {"places": [
    {"name": "São Paulo", "type": "estado", "uf": "SP",
     "variants": ["sao paulo", "estado de sao paulo"]},
    {"name": "Amazônia", "type": "bioma",
     "variants": ["amazonia", "floresta amazonica"]}
  ]}
  ```
  Conteúdo mínimo: 26 estados + DF (nome por extenso; NÃO usar siglas soltas —
  ambíguas demais: "PA", "TO"), 5 regiões, 6 biomas. Variantes sem acento.
- Novo `src/core/analysis/geography.py` — `GeographyAnalyzer`:
  - Casamento por token-sequência sem acento (reusar abordagem do
    `kwic.py`: `WORD_PATTERN` + `normalize`), com limites de palavra.
  - Cuidado com sobreposição: variante mais longa vence ("estado de sao paulo"
    não conta também "sao paulo" na mesma posição — consumir tokens).
  - Saída: `geo_top` (célula "Nome (n); ..." top 5), `geo_mentions`
    (lista [(name, type, uf, count)]).
  - `columns()`: `ColumnSpec("geo_top", "Menções territoriais", 50, "text")`.
- Dentro do grupo `detect_textmetrics` (sem checkbox novo).
- XLSX: aba "Menções Territoriais" (`Nº Doc., Arquivo, Local, Tipo, UF,
  Contagem`); diálogo: aba "Território".
- Ajuda: metodologia (gazetteer editável; limitação: homônimos — mitigada por
  variantes explícitas).

**Testes (`tests/test_geography.py`):** estado por extenso detectado com/sem
acento; variante longa consome a curta; lugar fora do corpus analítico não
conta; gazetteer ausente → saída vazia sem exceção.

**Aceite:** contagens corretas no sintético; JSON editável documentado.

---

## Fase E — Co-ocorrência de termos

**Objetivo:** quais termos de busca aparecem *juntos* (mesma sentença) — laços
entre temas, insumo para inferir relações entre categorias/núcleos.

**Implementação:**
- Novo `src/core/analysis/cooccurrence.py` — `CooccurrenceAnalyzer(terms)`:
  - Reusar `sentiment.segment_sentences` para sentenças do corpus analítico;
    para cada par de termos (combinações), contar sentenças onde ambos ocorrem
    (`term_search.count_term(sentence, ...) > 0`).
  - Detail-only (`columns() == []`, padrão `kwic.py`): saída `cooccurrence`
    = lista [(termo_a, termo_b, contagem)] com contagem ≥ 1, ordenada desc.
- Registrar junto do kwic (`detect_kwic` controla ambos — análise de termos).
- XLSX: aba "Co-ocorrência" (`Nº Doc., Arquivo, Termo A, Termo B, Sentenças`);
  diálogo: aba "Co-ocorrência".
- Ajuda: metodologia (janela = sentença; co-ocorrência ≠ relação causal).

**Testes (`tests/test_cooccurrence.py`):** dois termos na mesma sentença
contam 1; em sentenças separadas contam 0; três termos → 3 pares; sem termos →
lista vazia.

**Aceite:** pares e contagens corretos; só roda com ≥2 termos.

---

## Fase F — Entrada DOCX e TXT

**Objetivo:** corpora reais misturam formatos; aceitar .docx e .txt além de PDF.

**Implementação:**
- Nova dependência: `python-docx>=1.1` (pura-Python, leve) em
  `requirements.txt`; adicionar `--collect-submodules docx` no `build.bat` e
  `hiddenimports += collect_submodules('docx')` no `Lupa.spec`.
- Novo `src/core/text_extractor.py`:
  - `extract_pages(path) -> tuple[list[str], dict]` — despacha por extensão:
    `.pdf` → código atual (mover a extração do `pdf_processor` para cá,
    mantendo OCR); `.docx` → blocos de ~3000 chars (python-docx não tem
    páginas reais — documentar); `.txt` → blocos por quebra dupla de linha,
    ~3000 chars.
  - `stats` mantém as chaves atuais (`pages_with_text` etc.; OCR zero para
    docx/txt).
- `PDFProcessor` → renomear classe para `DocumentProcessor` mantendo alias
  `PDFProcessor = DocumentProcessor` (compatibilidade com testes existentes).
- GUI: filtros do file dialog e do DropZone aceitam `*.pdf *.docx *.txt`;
  textos "PDFs" → "documentos" onde aparecer.
- Ajuda: seção curta "Formatos aceitos" (paginação aproximada em docx/txt —
  números de página são de bloco, não de página impressa).

**Testes (`tests/test_text_extractor.py`):** docx sintético (gerar com
python-docx no teste) extrai texto; txt com 2 blocos → 2 páginas; pdf continua
funcionando (fixture existente); extensão desconhecida → ValueError claro.

**Aceite:** processar .txt e .docx de ponta a ponta (analisadores + XLSX) sem
regressão nos testes de PDF.

---

## Fase G — Salvar/carregar projeto de análise

**Objetivo:** reprodutibilidade da *configuração*: termos, categorias e flags
de um estudo salvos num arquivo versionável.

**Implementação:**
- Formato `.lupa.json`:
  ```json
  {"versao": 1, "termos_raw": "clima\nMITIGAÇÃO: carbono, metano",
   "flags": {"ocr": true, "sentimento": true, "presidente": false,
              "metricas": true, "kwic": true},
   "arquivos": ["C:/corpus/msg_2020.pdf"]}
  ```
  Guardar o texto bruto do campo de termos (`termos_raw`) — não a estrutura
  parseada — para o usuário reabrir exatamente o que digitou.
- Novo `src/core/project_io.py`: `save_project(path, data)`,
  `load_project(path) -> dict` (validar `versao`; arquivos inexistentes →
  retornar lista `ausentes` para a GUI avisar sem quebrar).
- GUI: menu Arquivo → "Salvar projeto..." / "Abrir projeto..." (Ctrl+S /
  Ctrl+Shift+O); aplicar flags nos checkboxes, termos no campo, arquivos na
  lista.
- Ajuda: subseção "Projetos (.lupa.json)".

**Testes (`tests/test_project_io.py`):** round-trip salva/carrega; arquivo
ausente listado em `ausentes`; versão desconhecida → ValueError.

**Aceite:** fluxo salvar→fechar→abrir→processar reproduz a mesma configuração.

---

## Ordem, dependências e estimativa

| Fase | Depende de | Risco | Valor |
|------|-----------|-------|-------|
| A — CSV/JSON | — | baixo | interoperabilidade imediata |
| B — Emoções NRC | léxico PT disponível | médio (licença/qualidade da tradução) | alto p/ núcleos de significação |
| C — Temporal | — | baixo | alto p/ corpus anual |
| D — Gazetteer | — | baixo | alto p/ território |
| E — Co-ocorrência | — | baixo | médio |
| F — DOCX/TXT | refatorar extração | médio (única mudança estrutural) | alto |
| G — Projeto | — | baixo | médio |

Implementar **A → C → D → E → B → G → F** (F por último: única fase que mexe
na espinha do pipeline; B pode atrasar por validação do léxico sem bloquear o
resto).

## Checklist de encerramento de cada fase
- [ ] `pytest` verde (sem regressão) e cobertura `src/core` ≥ 80%
- [ ] Ajuda (F1) atualizada: metodologia + citação + abas
- [ ] README: bullet na lista de recursos + seção se houver config nova
- [ ] Commit conventional em PT
- [ ] Build (`Lupa.spec`) + instalação local + abrir o exe sem erro
