"""Researcher review dialog for detected bibliographic metadata."""

import json
from typing import Dict

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)

from src.gui import i18n


class MetadataEditorDialog(QDialog):
    def __init__(self, result: Dict, parent=None, language: str = i18n.DEFAULT_LANGUAGE):
        super().__init__(parent)
        self.language = i18n.normalize_language(language)
        self.setWindowTitle(
            "Review bibliographic metadata" if self.language == "en" else "Revisar metadados bibliográficos"
        )
        self.resize(720, 620)
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Manual corrections take precedence over automatic detection and are recorded in the project."
            if self.language == "en"
            else "Correções manuais têm precedência sobre a detecção automática e ficam registradas no projeto."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        form = QFormLayout()
        self.title = QLineEdit(str(result.get("title", "")))
        self.year = QLineEdit(str(result.get("publication_year") or result.get("year", "")))
        self.document_type = QLineEdit(str(result.get("document_type") or result.get("document", "")))
        self.authors = QLineEdit(
            str(result.get("authors_display", ""))
            or "; ".join(item.get("name", "") for item in result.get("authors", []))
        )
        self.affiliations = QLineEdit(
            str(result.get("affiliations_display", ""))
            or "; ".join(item.get("name", "") for item in result.get("affiliations", []))
        )
        self.authors.setPlaceholderText(
            "Separate multiple authors with semicolons"
            if self.language == "en"
            else "Separe múltiplos autores por ponto e vírgula"
        )
        self.affiliations.setPlaceholderText(
            "Separate multiple institutions with semicolons"
            if self.language == "en"
            else "Separe múltiplas instituições por ponto e vírgula"
        )
        for label, widget in (
            ("Title" if self.language == "en" else "Título", self.title),
            ("Publication year" if self.language == "en" else "Ano de publicação", self.year),
            ("Document type" if self.language == "en" else "Tipo documental", self.document_type),
            ("Authors" if self.language == "en" else "Autores", self.authors),
            ("Affiliations" if self.language == "en" else "Afiliações", self.affiliations),
        ):
            form.addRow(label, widget)
        layout.addLayout(form)
        evidence_label = QLabel("Detection evidence" if self.language == "en" else "Evidências da detecção")
        evidence_label.setStyleSheet("font-weight: 700;")
        layout.addWidget(evidence_label)
        self.evidence = QPlainTextEdit()
        self.evidence.setReadOnly(True)
        self.evidence.setPlainText(
            json.dumps(result.get("metadata_evidence", {}), ensure_ascii=False, indent=2)
        )
        layout.addWidget(self.evidence, stretch=1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def override(self) -> Dict[str, object]:
        return {
            "title": self.title.text().strip(),
            "publication_year": self.year.text().strip(),
            "document_type": self.document_type.text().strip(),
            "authors": [part.strip() for part in self.authors.text().split(";") if part.strip()],
            "affiliations": [part.strip() for part in self.affiliations.text().split(";") if part.strip()],
        }
