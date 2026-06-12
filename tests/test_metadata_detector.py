"""Unit tests for metadata detection (year, president, document type)."""

import pytest

from src.core.metadata_detector import PRESIDENTS, detect_metadata

pytestmark = pytest.mark.unit


def test_presidents_loaded_from_json():
    assert len(PRESIDENTS) > 0
    canonical, start, end, variants = PRESIDENTS[0]
    assert isinstance(canonical, str)
    assert isinstance(start, int) and isinstance(end, int)
    assert isinstance(variants, list) and variants


def test_detects_year_from_content():
    md = detect_metadata(["Relatório referente ao ano de 2020."], "doc.pdf")
    assert md["year"] == "2020"


def test_detects_year_from_filename_when_absent_in_text():
    md = detect_metadata(["sem ano aqui"], "mensagem_2015.pdf")
    assert md["year"] == "2015"


def test_president_detected_when_enabled():
    md = detect_metadata(
        ["Mensagem 2020 - Presidente Jair Bolsonaro"], "msg.pdf", detect_president=True
    )
    assert md["president"] == "Jair Bolsonaro"


def test_president_blank_when_disabled():
    md = detect_metadata(
        ["Mensagem 2020 - Presidente Jair Bolsonaro"], "msg.pdf", detect_president=False
    )
    assert md["president"] == ""


def test_president_disambiguated_by_year():
    # Lula appears in two mandates; the year picks the right window.
    md = detect_metadata(["Mensagem de 2005 - Lula da Silva"], "msg.pdf")
    assert md["president"] == "Luiz Inácio Lula da Silva"


def test_document_type_default():
    md = detect_metadata(["mensagem ao congresso nacional"], "msg.pdf")
    assert md["document"] == "Mensagem ao Congresso Nacional"


def test_document_type_unidentified_when_no_signal():
    md = detect_metadata(["texto qualquer sem pista nenhuma"], "doc.pdf")
    assert md["document"] == "Não identificado"


def test_document_type_artigo_cientifico():
    pages = [
        "Revista Brasileira de Ecologia ISSN 1234-5678. "
        "Resumo: x. Abstract: y. Palavras-chave: clima."
    ]
    assert detect_metadata(pages, "estudo.pdf")["document"] == "Artigo científico"


def test_document_type_comunicacao_nota_tecnica():
    md = detect_metadata(["Nota Técnica n. 5 sobre saneamento"], "nota_tecnica_5.pdf")
    assert md["document"] == "Comunicação / Nota técnica"


def test_document_type_dissertacao():
    pages = ["Dissertação de mestrado apresentada ao Programa de Pós-Graduação"]
    assert detect_metadata(pages, "d.pdf")["document"] == "Dissertação (mestrado)"


def test_document_type_legislacao():
    pages = ["LEI Nº 14.026, DE 15 DE JULHO DE 2020. O PRESIDENTE DA REPÚBLICA"]
    assert (
        detect_metadata(pages, "lei.pdf")["document"]
        == "Legislação (lei, decreto, portaria)"
    )


def test_document_type_accent_insensitive():
    # OCR often drops accents; "relatorio" without accent must still match.
    pages = ["relatorio anual de gestao do orgao"]
    assert detect_metadata(pages, "x.pdf")["document"] == "Relatório"
