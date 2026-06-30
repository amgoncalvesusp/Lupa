"""Bibliographic metadata extraction and provenance tests."""

import pytest

from src.core.bibliographic_metadata import detect_bibliographic_metadata

pytestmark = pytest.mark.unit


def test_structured_metadata_has_precedence_and_keeps_evidence():
    result = detect_bibliographic_metadata(
        ["Titulo inferido\nPor Autor Errado\nPublicado em 2019"],
        "arquivo_2018.pdf",
        {
            "title": "Politicas Climaticas no Brasil",
            "author": "Ana Souza; Bruno Lima",
            "creationDate": "D:20230314120000",
        },
    )

    assert result["title"] == "Politicas Climaticas no Brasil"
    assert result["publication_year"] == "2023"
    assert [item["name"] for item in result["authors"]] == ["Ana Souza", "Bruno Lima"]
    assert result["metadata_evidence"]["title"]["source"] == "embedded_metadata"


def test_first_page_detects_authors_affiliations_identifiers_and_type():
    result = detect_bibliographic_metadata(
        [
            "TRANSICAO ENERGETICA JUSTA\n"
            "Autores: Ana Souza; Bruno Lima\n"
            "Universidade Federal de Minas Gerais\n"
            "Publicado em 12 de maio de 2022\n"
            "DOI: 10.1234/lupa.2022.15\n"
            "Resumo: Este artigo analisa politicas publicas.\n"
            "Palavras-chave: energia; trabalho"
        ],
        "estudo.pdf",
    )

    assert result["title"] == "TRANSICAO ENERGETICA JUSTA"
    assert result["publication_year"] == "2022"
    assert result["document_type"] == "Artigo científico"
    assert result["authors_display"] == "Ana Souza; Bruno Lima"
    assert result["affiliations_display"] == "Universidade Federal de Minas Gerais"
    assert result["identifiers"]["doi"] == ["10.1234/lupa.2022.15"]


def test_publication_year_prefers_explicit_header_over_reference_frequency():
    result = detect_bibliographic_metadata(
        [
            "Relatorio anual\nPublicado em 2024\n"
            "Referencias: Silva (2019). Souza (2019). Lima (2019)."
        ],
        "relatorio.pdf",
    )

    assert result["publication_year"] == "2024"


def test_unknown_values_are_explicit_and_do_not_fabricate_people():
    result = detect_bibliographic_metadata(["Texto sem cabecalho bibliografico."], "x.txt")

    assert result["authors"] == []
    assert result["affiliations"] == []
    assert result["metadata_status"] == "incompleto"
