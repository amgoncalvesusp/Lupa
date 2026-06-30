# Plano de implementação: metadados, entidades e análises comparativas

> English translation: [METADATA_AND_ANALYSES_PLAN.en.md](METADATA_AND_ANALYSES_PLAN.en.md)

> Status em 20/06/2026: fases 0 a 8 implementadas e integradas às saídas
> escritas, XLSX/CSV/JSON e à exploração visual. A fase 9 possui segmentação,
> importação tabular e Krippendorff Alpha no núcleo. A detecção presidencial
> permanece apenas como compatibilidade interna. Metadados revisados são
> persistidos em projetos v2, e projetos v1 são migrados automaticamente.

## 1. Objetivo

Generalizar o Lupa para corpora heterogêneos e permitir responder, de forma
auditável:

- quem produziu os documentos;
- a quais instituições os autores estavam vinculados;
- quando e onde os documentos foram publicados;
- quais tipos documentais compõem o corpus;
- quais pessoas e instituições mais publicaram sobre uma área;
- como termos, associações e vocabulário variam entre grupos e períodos.

O plano mantém o processamento offline como padrão. Enriquecimento por DOI,
ORCID ou ROR será opcional, enviará somente identificadores públicos e usará
cache local.

## 2. Princípios metodológicos

1. **Evidência antes do valor:** todo metadado detectado guarda origem, trecho,
   página e confiança.
2. **Não adivinhar:** ausência de evidência resulta em "Não identificado".
3. **Pessoa não é instituição:** autores pessoais, autores corporativos,
   editores, orientadores e órgãos emissores são entidades e papéis distintos.
4. **Menção não é autoria:** nomes encontrados no corpo ou nas referências não
   podem ser promovidos automaticamente a autores.
5. **Correção humana prevalece:** valores revisados manualmente ficam bloqueados
   contra nova sobrescrita automática.
6. **Contagem transparente:** consolidações oferecem contagem integral e
   fracionada para documentos com múltiplos autores.
7. **Resultados descritivos:** volume de publicação não será apresentado como
   impacto, qualidade ou influência científica.
8. **Compatibilidade:** projetos e exportações existentes continuam abrindo.

## 3. Mudança de escopo da detecção de presidente

- Remover a opção visível da interface e usar `detect_president=False` por
  padrão.
- Manter `presidents.json`, `_detect_president()` e a flag do projeto para
  compatibilidade e possível reativação futura.
- Não incluir a coluna Presidente em novos projetos.
- Continuar aceitando a chave `presidente` em projetos versão 1 e resultados
  antigos.

## 4. Modelo de dados

### 4.1 Documento

```json
{
  "document_id": "sha256:...",
  "title": "Título detectado ou revisado",
  "publication_year": 2024,
  "document_type": "Artigo científico",
  "language": "pt",
  "publisher": "Editora ou veículo",
  "venue": "Periódico, jornal, evento ou órgão",
  "identifiers": {
    "doi": "10.xxxx/xxxx",
    "isbn": "",
    "issn": "",
    "orcid": [],
    "law_number": "",
    "url": ""
  },
  "contributors": [],
  "metadata_evidence": [],
  "metadata_status": "revisar"
}
```

`document` será mantido temporariamente como alias de `document_type` durante
uma versão para não quebrar exportadores e projetos existentes.

### 4.2 Contribuidor

```json
{
  "entity_id": "person:...",
  "entity_type": "person",
  "raw_name": "Maria da Silva",
  "canonical_name": "Maria da Silva",
  "roles": ["author"],
  "orcid": "",
  "affiliations": [],
  "confidence": "high"
}
```

Tipos de entidade: `person` e `organization`.

Papéis iniciais: `author`, `corporate_author`, `editor`, `advisor`, `issuer`,
`translator` e `reporter`.

### 4.3 Filiação

```json
{
  "raw_name": "Universidade Federal de ...",
  "canonical_name": "Universidade Federal de ...",
  "ror": "",
  "country": "Brasil",
  "department": "Programa de Pós-Graduação ...",
  "evidence": {},
  "confidence": "medium"
}
```

A relação autor-filiação é muitos-para-muitos. Quando o documento informa
instituições, mas não permite associá-las a autores específicos, a filiação
fica no nível do documento e é marcada como `unassigned`.

### 4.4 Evidência

```json
{
  "field": "publication_year",
  "value": 2024,
  "source": "first_page",
  "page": 1,
  "snippet": "Publicado em maio de 2024",
  "confidence": "high",
  "manual_override": false
}
```

Fontes: `doi`, `embedded_metadata`, `first_page`, `filename`, `sidecar`,
`manual` e `legacy`.

## 5. Precedência dos metadados

### 5.1 Ano de publicação

1. API de DOI, quando habilitada e validada;
2. campo estruturado do PDF/DOCX;
3. padrão explícito na primeira página ou cabeçalho bibliográfico;
4. data de publicação em byline de reportagem;
5. nome do arquivo;
6. data de criação do arquivo, apenas como evidência de baixa confiança.

O ano mais frequente nas primeiras páginas deixa de ser regra principal, pois
pode representar anos citados no texto.

### 5.2 Autores e contribuidores

1. DOI/Crossref;
2. propriedades estruturadas do arquivo;
3. bloco de autoria da primeira página;
4. bylines como `Por`, `Autores`, `Author`, `Redação`;
5. órgão emissor para leis, normas e relatórios institucionais.

Referências bibliográficas e nomes no corpo são excluídos da busca de autoria.

### 5.3 Filiações

1. filiações estruturadas associadas ao DOI;
2. blocos numerados ou marcados na primeira página;
3. linhas com vocabulário institucional, como universidade, instituto,
   departamento, ministério, secretaria, empresa e organização;
4. enriquecimento ROR opcional para normalização.

### 5.4 Tipo documental

Expandir `document_types.json` para:

- artigo científico;
- capítulo de livro;
- livro;
- tese;
- dissertação;
- trabalho de conclusão;
- trabalho ou resumo de evento;
- relatório técnico ou institucional;
- nota técnica;
- lei;
- decreto;
- resolução ou portaria;
- decisão judicial;
- projeto de lei;
- reportagem;
- artigo de opinião;
- editorial;
- documento de política pública;
- página ou publicação web;
- outro;
- não identificado.

Cada classificação retorna pontuação, regras acionadas e confiança. Empates ou
evidência fraca permanecem para revisão.

## 6. Arquitetura

### 6.1 Extração

- Criar `extract_source_metadata(path) -> dict` em `text_extractor.py`.
- PDF: usar metadados do PyMuPDF e primeira página.
- DOCX: usar `core_properties` e parágrafos iniciais.
- TXT: metadados vazios, salvo sidecar futuro.
- Adicionar `source_path` e `source_metadata` ao `DocumentContext` com valores
  padrão para preservar testes e plugins existentes.

### 6.2 Detecção bibliográfica

Novos módulos:

- `bibliographic_metadata.py`: orquestra detecção e precedência;
- `identifier_detector.py`: DOI, ISBN, ISSN, ORCID, URL e número legal;
- `contributor_detector.py`: autores, autores corporativos e papéis;
- `affiliation_detector.py`: instituições e relações;
- `entity_normalization.py`: normalização conservadora e aliases;
- `metadata_providers.py`: adaptadores opcionais Crossref, ORCID e ROR;
- `metadata_cache.py`: cache JSON versionado e expiração configurável.

### 6.3 Análises de corpus

Os analisadores atuais operam documento a documento. Criar uma segunda
extensão, sem alterar o contrato existente:

```python
class CorpusAnalyzer(Protocol):
    name: str
    def run(self, results: list[dict], options: dict) -> dict: ...
```

`build_corpus_analyses(results, options)` executará análises que dependem de
comparação entre documentos. Exportadores e gráficos receberão o resultado de
corpus opcionalmente, mantendo compatibilidade com chamadas antigas.

### 6.4 Projetos

Evoluir `.lupa.json` para versão 2 com:

- correções manuais de metadados por `document_id`;
- aliases e fusões de autores/instituições;
- configuração de grupos comparativos;
- preferência de contagem integral ou fracionada;
- consentimento para provedores online;
- cache referenciado, sem incorporar respostas externas completas.

Implementar migração automática de versão 1 para versão 2.

## 7. Fases de implementação

### Fase 0 - Base bibliográfica e generalização

1. Ocultar presidente e alterar o padrão para desabilitado.
2. Introduzir o modelo de metadados e evidências.
3. Extrair metadados estruturados de PDF e DOCX.
4. Detectar identificadores, título, ano, tipo e contribuidores.
5. Detectar filiações sem forçar relações ambíguas.
6. Adicionar editor de metadados e indicador `revisar/revisado`.
7. Persistir correções no projeto.

Saídas:

- colunas resumidas: Título, Ano, Tipo e Autores;
- aba XLSX `Documentos`;
- aba XLSX/CSV `Autores e Filiações`, uma relação por linha;
- JSON estruturado com evidências;
- aba `Metadados` no diálogo de detalhes.

### Fase 1 - Consolidação de pessoas e instituições

1. Criar registro canônico de entidades.
2. Normalizar espaços, caixa, ordem de nomes e pontuação sem remover acentos do
   valor exibido.
3. Sugerir fusões, mas exigir confirmação para nomes ambíguos.
4. Permitir mesclar e desfazer mesclagem.
5. Calcular:
   - documentos por autor e instituição;
   - contagem fracionada `1 / número de autores`;
   - palavras do corpus por entidade;
   - intervalo de anos de publicação;
   - documentos por tipo;
   - termos e categorias por entidade, em valor bruto e normalizado.

Saídas: `Síntese por Autor`, `Síntese por Instituição` e filtros nos gráficos.

### Fase 2 - Dispersão de termos

- Calcular alcance em documentos e blocos/páginas.
- Implementar `DP` para termos, categorias e palavras-chave.
- Exibir frequência, frequência normalizada, alcance e dispersão juntos.
- Marcar termos concentrados em uma única unidade.

Base: Gries (2008), DOI `10.1075/ijcl.13.4.02gri`.

### Fase 3 - Keyness entre grupos

- Comparar grupo-alvo com restante do corpus por ano, tipo, autor, instituição
  ou grupo manual.
- Calcular log-likelihood `G²`, log-ratio, frequências normalizadas e direção.
- Aplicar frequência mínima e correção Benjamini-Hochberg quando p-valores forem
  exibidos.
- Não calcular quando os grupos não atingirem mínimos documentados de textos e
  tokens.

Base: Rayson e Garside (2000) e Dunning (1993).

### Fase 4 - Coocorrência normalizada

- Manter contagem bruta existente.
- Construir tabela 2x2 por janela de sentença.
- Adicionar NPMI e log-likelihood.
- Exigir frequência mínima e mostrar número de sentenças da base.
- Permitir agrupamento por autor, instituição, ano e tipo documental.

### Fase 5 - Diversidade lexical MATTR

- Adicionar MATTR sem remover TTR e Guiraud.
- Janela padrão configurável e registrada na metodologia.
- Documentos menores que a janela usam todos os tokens e recebem aviso.
- Exportar quantidade de janelas e tamanho efetivo.

Base: Covington e McFall (2010), com as limitações discutidas por Bestgen
(2025).

### Fase 6 - Similaridade entre documentos

- Reusar `word_counts` e TF-IDF existentes.
- Calcular similaridade de cosseno.
- Gerar matriz simétrica, pares mais próximos e alerta configurável de possível
  duplicata.
- Não criar agrupamentos automáticos como verdade substantiva; clustering será
  apenas uma visualização opcional.

### Fase 7 - Mudança lexical temporal

- Agregar distribuições por ano.
- Calcular divergência Jensen-Shannon entre períodos consecutivos.
- Listar os termos que mais contribuem para cada mudança.
- Exigir mínimos de documentos e tokens por período.
- Tratar anos ausentes e lacunas temporais explicitamente.

### Fase 8 - Diagnóstico de sentimento

- Informar cobertura do léxico afetivo.
- Informar número de tokens e sentenças que sustentam o escore.
- Calcular intervalo bootstrap de 95% por documento.
- Em agregações, fazer reamostragem por documento para evitar falsa precisão por
  sentenças do mesmo texto.
- Rebaixar confiança quando cobertura ou amostra forem insuficientes.

### Fase 9 - Segmentação temática e codificação humana

Implementar somente após as fases anteriores:

- segmentação por coesão lexical para localizar mudanças internas de assunto;
- aplicação das análises existentes por segmento;
- seleção e codificação manual de trechos;
- importação de codificação de dois ou mais pesquisadores;
- Krippendorff Alpha por código e total;
- trilha de decisões e divergências.

## 8. Interface

### Corpus

- Presidente deixa de aparecer.
- Adicionar controle `Metadados: automático / revisar`.
- Mostrar estado de identificação por documento.

### Resultados

- Colunas padrão: Arquivo, Título, Ano, Tipo, Autores, Instituições, Páginas,
  Palavras e Confiança.
- Nomes longos ficam no detalhe, não em colunas excessivamente largas.
- Ação `Revisar metadados` abre formulário com evidências ao lado de cada campo.

### Exploração

- Novos modos: Autores, Instituições, Dispersão, Keyness, Similaridade,
  Coocorrência e Mudança temporal.
- Filtros coordenados por ano, tipo, autor e instituição.
- Toda visualização conserva tabela exportável e definição metodológica.

## 9. Contagens consolidadas

Para cada autor e instituição, oferecer:

| Medida | Definição |
|---|---|
| Documentos | Um crédito integral por documento |
| Documentos fracionados | Crédito dividido pelo número de autores |
| Palavras | Soma do corpus analítico dos documentos |
| Participação no corpus | Percentual dos documentos ou palavras |
| Período ativo | Primeiro e último ano identificados |
| Termos/categorias | Contagem bruta e por mil palavras |
| Tipos documentais | Distribuição dos documentos por tipo |

Documentos com autor corporativo entram na síntese de organizações. Filiações
não confirmadas não entram no ranking principal e aparecem separadamente como
`Filiação a revisar`.

## 10. Testes e validação

### TDD por fase

1. Teste de unidade falhando para cada regra e cálculo.
2. Implementação mínima.
3. Testes de integração do pipeline e exportadores.
4. Teste E2E do fluxo adicionar, processar, revisar, consolidar e exportar.

### Corpus ouro de metadados

Criar conjunto versionado e legalmente redistribuível com exemplos de:

- artigos científicos;
- leis e normas;
- reportagens;
- teses e dissertações;
- relatórios institucionais;
- documentos sem metadados.

Anotar título, ano, tipo, contribuidores, papéis e filiações. Para campos
classificados como alta confiança, a meta inicial é precisão de pelo menos 95%.
Recall será reportado separadamente; o sistema deve preferir ausência a falso
positivo.

### Invariantes

- resultado manual nunca é sobrescrito;
- mesma entidade consolidada produz mesmo `entity_id`;
- mesclar e desfazer preservam documentos;
- soma fracionada dos créditos de autoria de um documento é 1;
- matrizes de similaridade são simétricas e têm diagonal 1;
- NPMI fica em `[-1, 1]`;
- Jensen-Shannon fica em `[0, 1]` quando usada base 2;
- todas as exportações reconciliam com as contagens da interface;
- cobertura do código próprio permanece em pelo menos 80%.

## 11. Riscos e controles

| Risco | Controle |
|---|---|
| Nome citado confundido com autor | Ler apenas zonas de autoria e excluir referências/corpo |
| Homônimos ou variações de nome | Sugestão de fusão, confirmação humana e ORCID opcional |
| Instituição sem vínculo individual | Marcar `unassigned`, sem inferência automática |
| Ano de referência confundido com publicação | Precedência por fonte e evidência explícita |
| Tipo documental incorreto | Confiança, regras visíveis e revisão manual |
| API indisponível | Offline continua funcional e cache é usado |
| Vazamento de conteúdo | Provedores recebem apenas DOI/ORCID/ROR |
| Rankings interpretados como impacto | Rotular como volume/contribuição documental |
| Grupos pequenos em keyness/JSD | Mínimos obrigatórios e saída indisponível explicada |

## 12. Ordem executiva

1. Fase 0 - base bibliográfica e presidente oculto;
2. Fase 1 - consolidação de autores e instituições;
3. Fase 2 - dispersão;
4. Fase 3 - keyness;
5. Fase 4 - coocorrência normalizada;
6. Fase 5 - MATTR;
7. Fase 6 - similaridade;
8. Fase 7 - mudança temporal;
9. Fase 8 - diagnóstico de sentimento;
10. Fase 9 - segmentação e codificação humana.

Cada fase deve terminar com documentação metodológica, exportação, visualização
quando aplicável, testes, cobertura, revisão de segurança e build executável.

## 13. Referências metodológicas principais

- Gries, S. T. (2008). *Dispersions and adjusted frequencies in corpora*.
  <https://doi.org/10.1075/ijcl.13.4.02gri>
- Rayson, P.; Garside, R. (2000). *Comparing Corpora using Frequency
  Profiling*. <https://aclanthology.org/W00-0901/>
- Dunning, T. (1993). *Accurate Methods for the Statistics of Surprise and
  Coincidence*. <https://aclanthology.org/J93-1003/>
- Church, K.; Hanks, P. (1989). *Word association norms, mutual information,
  and lexicography*. <https://doi.org/10.3115/981623.981633>
- Covington, M.; McFall, J. (2010). *Cutting the Gordian Knot: The
  Moving-Average Type-Token Ratio*. <https://doi.org/10.1080/09296171003643098>
- Bestgen, Y. (2025). *Estimating lexical diversity using MATTR: Pros and
  cons*. <https://doi.org/10.1016/j.rmal.2024.100168>
- Salton, G.; Wong, A.; Yang, C. S. (1975). *A vector space model for automatic
  indexing*. <https://doi.org/10.1145/361219.361220>
- Lin, J. (1991). *Divergence measures based on the Shannon entropy*.
  <https://doi.org/10.1109/18.61115>
- Hearst, M. (1997). *TextTiling: Segmenting Text into Multi-paragraph Subtopic
  Passages*. <https://aclanthology.org/J97-1003/>
- Hayes, A.; Krippendorff, K. (2007). *Answering the Call for a Standard
  Reliability Measure for Coding Data*.
  <https://doi.org/10.1080/19312450709336664>
