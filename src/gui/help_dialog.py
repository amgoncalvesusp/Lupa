"""In-app help dialog."""

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout


HELP_HTML = """
<style>
    body { font-family: "Segoe UI", sans-serif; color: #1f2933; font-size: 11pt; line-height: 1.55; }
    h1 { color: #103d3a; font-family: "Georgia", serif; font-size: 18pt; margin-top: 12px; }
    h2 { color: #0f766e; font-size: 14pt; margin-top: 18px; padding-bottom: 4px; }
    h3 { color: #b5670a; font-size: 12pt; margin-top: 14px; }
    code { background: #e9f1ef; color: #115e59; padding: 2px 6px; border-radius: 4px; }
    pre { background: #faf7f0; color: #1f2933; padding: 12px; border-radius: 8px;
          border-left: 3px solid #0f766e; }
    .tip { background: #eef6f4; padding: 12px; border-left: 3px solid #0f766e;
           border-radius: 6px; margin: 10px 0; }
    .warn { background: #fbf2e5; padding: 12px; border-left: 3px solid #b5670a;
            border-radius: 6px; margin: 10px 0; }
    ul { margin-left: 8px; padding-left: 16px; }
    li { margin: 4px 0; }
    .key { background: #e4ddcf; color: #1f2933; padding: 2px 8px; border-radius: 4px;
           font-family: monospace; font-size: 10pt; }
</style>

<h1>Como usar o Lupa</h1>

<p>Software para análise de conteúdo e métricas textuais de documentos PDF, DOCX e TXT, de forma padronizada e auditável. Voltado à pesquisa acadêmica: contagem, busca de termos, análise de sentimento, emoções discretas, legibilidade, diversidade lexical, palavras-chave, território, co-ocorrência e concordância (KWIC). Inclui suporte opcional a metadados de Mensagens Presidenciais ao Congresso Nacional.</p>

<h2>Fluxo básico de uso</h2>
<ol>
    <li><b>Adicionar documentos</b> — Arraste arquivos PDF, DOCX ou TXT para a área pontilhada ou clique em <code>Adicionar Arquivos</code>.</li>
    <li><b>(Opcional) Definir termos de busca</b> — Digite termos no campo de busca, um por linha.</li>
    <li><b>(Opcional) Marcar OCR</b> — Ative se algum PDF for escaneado (apenas imagem).</li>
    <li><b>Processar</b> — Clique em <code>▶ Processar documentos</code>. O progresso aparece na barra inferior.</li>
    <li><b>Exportar</b> — Após conclusão, clique em <code>⬇ Exportar</code> e escolha XLSX, CSV ou JSON.</li>
</ol>

<h2>Formatos aceitos</h2>
<ul>
    <li><b>PDF:</b> extração por PyMuPDF; OCR opcional para páginas escaneadas.</li>
    <li><b>DOCX:</b> parágrafos extraídos por <code>python-docx</code>, agrupados em blocos aproximados de até 3000 caracteres.</li>
    <li><b>TXT:</b> blocos por quebra dupla de linha; blocos grandes são divididos.</li>
</ul>
<div class="warn">Em DOCX/TXT, o número de página exibido nos detalhes representa bloco textual, não página impressa.</div>

<h2>Busca de termos e expressões</h2>

<p>Permite contar quantas vezes cada palavra ou expressão aparece em cada documento, tanto no PDF completo quanto no corpus analítico.</p>

<h3>Regras de sintaxe</h3>
<ul>
    <li><b>Palavra simples:</b> <code>clima</code> — conta todas as ocorrências da palavra, ignorando acentos e maiúsculas/minúsculas.</li>
    <li><b>Expressão sem aspas:</b> <code>mudança do clima</code> — busca a sequência permitindo espaços variáveis entre palavras.</li>
    <li><b>Expressão com aspas (busca exata):</b> <code>"efeito estufa"</code> — exige correspondência literal da expressão entre limites de palavra.</li>
    <li><b>Categoria (codificação):</b> <code>NOME: termo1, termo2, "frase"</code> —
    soma as ocorrências de todos os termos membros em um único número por
    categoria (categorias de codificação de Bardin). O nome vira coluna própria
    na tabela e no XLSX; o detalhamento por termo membro fica na aba
    "Categorias".</li>
    <li><b>Linha em branco</b> ou iniciada com <code>#</code> — ignorada (comentário).</li>
</ul>

<h3>Exemplo de entrada</h3>
<pre># Termos individuais
carbono
desmatamento
"efeito estufa"

# Categorias de codificação (somam os membros)
MITIGAÇÃO: carbono, "efeito estufa", reflorestamento
ADAPTAÇÃO: adaptação, resiliência, "perdas e danos"</pre>

<div class="tip">
    <b>Acentos e maiúsculas:</b> A busca é case-insensitive e accent-insensitive por padrão. <code>clima</code> encontra <i>Clima</i>, <i>CLIMA</i>, <i>clíma</i> (caso ocorra erro de OCR).
</div>

<h2>Regras de contagem de palavras</h2>

<h3>Contam como palavra</h3>
<ul>
    <li>Sequências de letras, incluindo acentuadas (ex: <i>política</i>, <i>açúcar</i>)</li>
    <li>Palavras hifenizadas como unidade lexical</li>
    <li>Siglas formadas por letras (ex: <i>ONU</i>, <i>FMI</i>, <i>SUS</i>, <i>PIB</i>)</li>
    <li>Abreviações com letras</li>
</ul>

<h3>Não contam</h3>
<ul>
    <li>Números isolados (<i>2024</i>, <i>15</i>)</li>
    <li>Algarismos romanos como marcadores de capítulo (<i>III</i>, <i>IV</i>, <i>XIV</i>)</li>
    <li>Pontuação e símbolos</li>
    <li>Marcadores de página</li>
    <li>Caracteres soltos de erro de OCR</li>
</ul>

<h2>Corpus analítico</h2>

<p>O software realiza duas contagens distintas:</p>
<ul>
    <li><b>PDF Completo</b> — Todo o texto extraído, incluindo capa, ficha catalográfica, sumário, etc.</li>
    <li><b>Corpus Analítico</b> — Apenas o conteúdo substantivo da Mensagem.</li>
</ul>

<h3>Páginas excluídas automaticamente</h3>
<ul>
    <li>Capa e folha de rosto</li>
    <li>Ficha catalográfica (ISBN, CDD, CDU, Biblioteca da Presidência)</li>
    <li>Sumário / Índice (detectado por padrão de linhas pontilhadas)</li>
    <li>Expediente</li>
    <li>Lista de ministros e autoridades</li>
    <li>Páginas em branco</li>
</ul>

<div class="warn">
    A detecção é baseada em palavras-chave e heurísticas. Pode haver falsos positivos em layouts atípicos. Confira o resumo de páginas excluídas na aba <i>Páginas Excluídas</i> do arquivo XLSX exportado.
</div>

<h2>OCR (PDFs escaneados)</h2>

<p>PDFs sem texto pesquisável (apenas imagem) requerem OCR para extrair conteúdo. O software usa <b>Tesseract</b> com idioma português.</p>

<ul>
    <li>O OCR é aplicado automaticamente em páginas com pouco ou nenhum texto extraível.</li>
    <li>Marque a checkbox <i>Aplicar OCR</i> antes de processar.</li>
    <li>Se o Tesseract não for detectado, a checkbox fica desabilitada. Instale-o e reinicie o programa.</li>
</ul>

<h3>Instalação do Tesseract</h3>
<ol>
    <li>Baixe em: <code>github.com/UB-Mannheim/tesseract/wiki</code></li>
    <li>Durante a instalação, marque o pacote de idioma <b>português</b>.</li>
    <li>Mantenha o caminho padrão (<code>C:\\Program Files\\Tesseract-OCR</code>) para detecção automática.</li>
</ol>

<h2>Grau de confiança</h2>

<p>Cada documento recebe uma classificação:</p>
<ul>
    <li><b style="color:#15803d;">Alto</b> — Extração limpa, ≥95% das páginas com texto, pouco ou nenhum OCR.</li>
    <li><b style="color:#b5670a;">Médio</b> — 80–95% das páginas com texto, ou uso intensivo de OCR.</li>
    <li><b style="color:#b4413c;">Baixo</b> — Menos de 80% das páginas com texto extraído.</li>
</ul>

<h2>Metodologias das análises</h2>

<p>Cada análise do Lupa segue um método publicado e auditável. Esta seção explica
o que cada uma mede, como funciona internamente e qual referência citar.</p>

<h3>Análise de sentimento (LeIA / VADER-PT) — como funciona tecnicamente</h3>

<p>O Lupa usa o modelo <b>VADER</b> (<i>Valence Aware Dictionary and sEntiment
Reasoner</i>; Hutto &amp; Gilbert, 2014) na adaptação <b>LeIA</b> para o
português do Brasil (Almeida). É um método <b>léxico + regras</b>, não uma rede
neural — cada escore pode ser rastreado até palavras e regras específicas.</p>

<p><b>Passo a passo do cálculo:</b></p>
<ul>
    <li><b>1. Segmentação:</b> o texto do corpus analítico é dividido em
    sentenças (com proteção a abreviações como "Sr.", "art.", e enumerações),
    pois a sentença é a unidade de registro da análise.</li>
    <li><b>2. Léxico de valência:</b> cada palavra da sentença é procurada em um
    dicionário PT-BR em que cada entrada tem uma valência de <b>−4</b> (muito
    negativa) a <b>+4</b> (muito positiva), atribuída e validada por avaliadores
    humanos no projeto VADER original.</li>
    <li><b>3. Regras contextuais:</b> a valência de cada palavra é ajustada por
    heurísticas gramaticais: <b>negação</b> em janela de até 3 palavras
    ("não foi bom" inverte parcialmente o escore, fator −0,74),
    <b>intensificadores</b> ("muito", "extremamente": ±0,293),
    <b>CAIXA ALTA</b> enfática (+0,733) e pontuação exclamativa.</li>
    <li><b>4. Escore composto:</b> as valências ajustadas são somadas (x) e
    normalizadas para o intervalo [−1, +1] pela função
    <code>composto = x / √(x² + 15)</code>.</li>
    <li><b>5. Classificação:</b> composto ≥ <b>+0,05</b> → Positivo;
    composto ≤ <b>−0,05</b> → Negativo; entre os dois → Neutro
    (limiares padrão de Hutto &amp; Gilbert, 2014).</li>
    <li><b>6. Agregação:</b> o sentimento do documento é a média dos compostos
    das sentenças, com os percentuais de sentenças positivas/negativas/neutras.</li>
</ul>

<div class="tip"><b>Segurança metodológica:</b> diferentemente de modelos
"caixa-preta", todo escore é auditável — a aba <i>Sentimento (Sentenças)</i> do
XLSX e a tela de detalhes (duplo clique na linha de resultado) mostram cada
sentença com seu escore, permitindo conferência manual e uso das sentenças como
pré-indicadores afetivos para núcleos de significação (Aguiar &amp; Ozella).</div>

<div class="warn"><b>Limitações conhecidas:</b> métodos léxicos não capturam
ironia/sarcasmo nem vocabulário ausente do dicionário (o léxico VADER tem origem
em mídias sociais; em textos formais a cobertura tende a ser menor, aproximando
escores do neutro). Recomenda-se usar a classificação como <b>triagem</b> e
validar pela leitura das sentenças — não como veredito automático.</div>

<p><b>Citar:</b> Hutto, C.J. &amp; Gilbert, E.E. (2014). <i>VADER: A Parsimonious
Rule-based Model for Sentiment Analysis of Social Media Text</i>. ICWSM-14;
LeIA — Almeida, R.J.A., github.com/rafjaa/LeIA.</p>

<h3>Legibilidade (Flesch adaptado ao português)</h3>
<p><b>O que mede:</b> facilidade de leitura do texto.
<b>Como:</b> <code>ILF = 248,835 − 1,015×(palavras/frases) − 84,6×(sílabas/palavras)</code>.
Classes: Muito fácil (≥75), Fácil (50–75), Difícil (25–50), Muito difícil (&lt;25).
A contagem de sílabas usa heurística de grupos vocálicos (aproximação documentada).
<b>Citar:</b> Martins et al. (1996), Notas do ICMC-USP, n. 28.</p>

<h3>Diversidade lexical (TTR e Guiraud)</h3>
<p><b>O que mede:</b> riqueza de vocabulário.
<b>Como:</b> TTR = tipos ÷ tokens (Templin, 1957); como o TTR cai com o tamanho
do texto, reporta-se também o Índice de Guiraud = tipos ÷ √tokens (Guiraud, 1954),
mais estável para comparar documentos de tamanhos diferentes.</p>

<h3>Frequência de palavras-chave</h3>
<p><b>O que mede:</b> as palavras de conteúdo mais recorrentes — base quantitativa
da análise de conteúdo (Bardin, 2011). <b>Como:</b> remoção de <i>stopwords</i>
(lista editável em <code>data/stopwords_pt.txt</code>), contagem sem distinção de
acentos, ranking por frequência. Top 10 na tabela; top 30 na aba e na tela de detalhes.</p>

<h3>Concordância (KWIC)</h3>
<p><b>O que mede:</b> nada — é a saída <b>qualitativa</b>: para cada ocorrência de
cada termo de busca, registra o contexto à esquerda e à direita. Corresponde à
<i>unidade de contexto</i> de Bardin: permite ler cada ocorrência em situação, e
não apenas contá-la. <b>Como:</b> mesma correspondência da busca de termos
(sem distinção de acentos; frases compostas suportadas), janela de 15 palavras
de cada lado.</p>

<h3>N-gramas (expressões recorrentes)</h3>
<p><b>O que mede:</b> as sequências de 2 e 3 palavras mais frequentes do corpus
analítico — expressões como "desenvolvimento sustentável" que a frequência de
palavras isoladas não captura; candidatas naturais a unidades de significação.
<b>Como:</b> contagem sem distinção de acentos; o n-grama só é mantido se a
primeira e a última palavra forem palavras de conteúdo (stopwords internas são
permitidas, preservando "mudança <i>do</i> clima"); frequência mínima 2;
top 30 na aba "N-gramas" e na tela de detalhes.</p>

<h3>Categorias de codificação</h3>
<p><b>O que mede:</b> a frequência de cada <i>categoria</i> definida pelo
pesquisador (sintaxe <code>NOME: termo1, termo2</code>) — a soma das ocorrências
dos termos membros. Operacionaliza a etapa de codificação da análise de conteúdo
(Bardin, 2011): em vez de 20 colunas de termos, um número por categoria.
<b>Como:</b> usa o mesmo mecanismo da busca de termos (mesmos números); o
detalhamento por termo membro fica na aba "Categorias".</p>

<h3>Co-ocorrência de termos</h3>
<p><b>O que mede:</b> pares de termos de busca que aparecem na mesma sentença.
<b>Como:</b> cada sentença do corpus analítico é testada com o mesmo mecanismo da
busca de termos; pares com ao menos uma ocorrência aparecem na aba
"Co-ocorrência". Co-ocorrência é descritiva e não implica causalidade.</p>

<h3>Emoções discretas (NRC EmoLex)</h3>
<p><b>O que mede:</b> associações lexicais com alegria, tristeza, raiva, medo,
confiança, repulsa, surpresa e antecipação. <b>Como:</b> usa o arquivo editável
<code>data/nrc_emolex_pt.txt</code> no formato <code>palavra TAB emocao</code>.
O arquivo é distribuído vazio por padrão por causa dos termos do NRC; quando
preenchido pelo pesquisador, a aba "Emoções (Palavras)" mostra a trilha de
auditoria. <b>Citar:</b> Mohammad &amp; Turney (2013).</p>

<h3>Menções territoriais</h3>
<p><b>O que mede:</b> estados, regiões e biomas brasileiros mencionados no corpus
analítico. <b>Como:</b> casamento por sequência de tokens contra o gazetteer
editável <code>data/gazetteer_br.json</code>; variantes longas vencem sobre
variantes curtas para evitar dupla contagem.</p>

<h3>Síntese por ano</h3>
<p>Quando há dois ou mais anos distintos no lote, o XLSX cria a aba "Síntese por
Ano" com métricas descritivas por ano. A janela principal também habilita o
botão "Gráficos". Não há inferência estatística: são somas e médias
simples entre documentos do mesmo ano.</p>

<h3>Gráficos interativos</h3>
<p>O botão <b>Gráficos</b> reúne seis visualizações: série temporal, comparação
entre documentos, sentimento empilhado, dispersão legibilidade × diversidade
lexical, matriz de coocorrência e perfil territorial. É possível filtrar ano e
documento, normalizar contagens por mil palavras, ocultar séries, usar a roda do
mouse para zoom, copiar os dados exibidos e exportar PNG.</p>
<p>O tamanho dos pontos da dispersão representa palavras do corpus; a cor indica
sentimento. No heatmap, a intensidade representa sentenças em que o par de termos
coocorre. Clicar em barras ou pontos associados a documentos abre os detalhes.
Todas as visualizações são descritivas e não implicam causalidade ou inferência
estatística.</p>

<h3>TF-IDF (termos distintivos)</h3>
<p><b>O que mede:</b> as palavras <i>distintivas</i> de cada documento — não as
mais frequentes, mas as que diferenciam um documento dos demais do lote.
<b>Como:</b> <code>tf-idf(palavra, doc) = frequência × ln(N / nº de docs com a
palavra)</code>. Palavras presentes em todos os documentos pontuam zero
("desenvolvimento" em todo discurso oficial não distingue nada); palavras
concentradas em um documento pontuam alto. Requer ao menos 2 documentos no lote;
top 15 por documento na aba "TF-IDF (Termos Distintivos)".
<b>Citar:</b> Salton, G. &amp; Buckley, C. (1988). <i>Term-weighting approaches
in automatic text retrieval</i>. Information Processing &amp; Management, 24(5).</p>

<h3>Detecção do tipo de documento</h3>
<p><b>Como:</b> classificador por regras com pontuação: padrões de conteúdo das
primeiras páginas (2 pontos por acerto) e do nome do arquivo (1 ponto) para cada
tipo configurado (mensagem ao Congresso, artigo científico, tese, dissertação,
relatório, nota técnica/comunicação, legislação, plano, discurso, edital, ata,
livro). Vence o tipo com maior pontuação; sem acertos, o documento é rotulado
<i>Não identificado</i> — o Lupa não "chuta". A lista de tipos e padrões é
editável em <code>data/document_types.json</code>.</p>

<h3>Contagem de palavras e corpus analítico</h3>
<p>Regras determinísticas descritas nas seções acima ("Regras de contagem" e
"Corpus analítico"). <b>Citar (análise de conteúdo):</b> Bardin, L. (2011).
<i>Análise de Conteúdo</i>. São Paulo: Edições 70.</p>

<h2>Exportação (XLSX, CSV, JSON)</h2>

<p>O Lupa exporta os resultados em três formatos. O <b>XLSX</b> é a planilha
formatada para leitura e auditoria manual e inclui a aba "Metodologia". O
<b>CSV</b> cria uma pasta com <code>resultados.csv</code>,
<code>metodologia.txt</code> e arquivos de detalhe separados, usando separador
<code>;</code> e codificação <code>utf-8-sig</code> para melhor compatibilidade com
Excel em português. O <b>JSON</b> preserva a metodologia e os dicionários públicos
completos de cada documento, útil para arquivamento reprodutível e integração com
R/Python.</p>

<h3>Aba 1: Contagem de Palavras</h3>
<p>Linha por documento. Colunas: identificação, metadados detectados, contagens,
métricas textuais, sentimento, grau de confiança, observações. Se termos de busca
foram definidos, duas colunas por termo (PDF Completo / Corpus Analítico).</p>

<h3>Aba 2: Páginas Excluídas</h3>
<p>Lista detalhada de cada página excluída do corpus analítico, com motivo da exclusão e número de palavras na página.</p>

<h3>Aba 3: Sentimento (Sentenças)</h3>
<p>Cada sentença analisada, com página, escore composto e classe — a trilha de auditoria da análise de sentimento.</p>

<h3>Aba 4: Frequência de Palavras</h3>
<p>Ranking das palavras de conteúdo mais frequentes por documento (até 30), após remoção de stopwords.</p>

<h3>Aba 5: N-gramas</h3>
<p>Expressões de 2–3 palavras mais frequentes por documento, com a quantidade de palavras (N) e a frequência.</p>

<h3>Aba 6: Categorias</h3>
<p>Por documento e categoria: total da categoria e detalhamento por termo membro (presente apenas quando categorias são definidas).</p>

<h3>Aba 7: TF-IDF (Termos Distintivos)</h3>
<p>As 15 palavras mais distintivas de cada documento (presente apenas com 2+ documentos no lote).</p>

<h3>Aba 8: Concordância (KWIC)</h3>
<p>Cada ocorrência dos termos de busca com contexto à esquerda e à direita, página e termo.</p>

<h3>Abas adicionais</h3>
<p>O XLSX sempre inclui "Metodologia", com data, arquivos, flags, termos,
configurações e critérios metodológicos. Quando há dados, também pode incluir:
"Emoções (Palavras)", "Menções Territoriais", "Co-ocorrência" e "Síntese por
Ano". Essas abas mantêm a trilha de auditoria dos agregados exibidos na tabela
principal.</p>

<h3>Arquivos CSV</h3>
<p>Ao escolher CSV, o Lupa cria uma pasta com o nome selecionado. O arquivo
<code>resultados.csv</code> contém as mesmas colunas da primeira aba do XLSX.
Arquivos de detalhe são criados apenas quando há dados: <code>sentencas.csv</code>,
<code>palavras.csv</code>, <code>ngramas.csv</code>, <code>categorias.csv</code>,
<code>kwic.csv</code> e <code>paginas_excluidas.csv</code>.</p>

<h3>Arquivo JSON</h3>
<p>O JSON contém <code>gerado_por</code>, <code>metodologia</code> e
<code>documentos</code>, com os resultados completos de cada documento. Chaves
internas iniciadas por sublinhado são omitidas para expor apenas dados públicos
da análise.</p>

<h2>Atalhos</h2>
<ul>
    <li><span class="key">Ctrl+O</span> — Adicionar arquivos</li>
    <li><span class="key">Ctrl+S</span> — Salvar projeto</li>
    <li><span class="key">Ctrl+Shift+O</span> — Abrir projeto</li>
    <li><span class="key">Ctrl+E</span> — Exportar resultados</li>
    <li><span class="key">Ctrl+Q</span> — Sair</li>
    <li><span class="key">F1</span> — Esta tela de ajuda</li>
</ul>

<h2>Reprodutibilidade</h2>
<p>Toda a contagem segue regras determinísticas. Processar os mesmos PDFs nas mesmas condições produz exatamente os mesmos resultados. Diferenças entre execuções só ocorrem se houver OCR sobre páginas marginais (qualidade de imagem pode variar a saída).</p>
"""


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Como usar — Lupa")
        self.resize(900, 740)
        self.setStyleSheet("QDialog { background-color: #f4f1ea; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(HELP_HTML)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #1f2933;
                border: 1px solid #e4ddcf;
                border-radius: 10px;
                padding: 16px;
                font-size: 11pt;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cdc4b0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #0f766e; }
        """)
        layout.addWidget(browser)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #0f766e;
                color: #ffffff;
                border: none;
                border-radius: 9px;
                padding: 10px 24px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #0d9488; }
        """)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
