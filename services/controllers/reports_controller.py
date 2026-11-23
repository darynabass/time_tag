"""Контролер сторінки «Звіти»: з'єднує інтерфейс із логікою формування звіту."""

from __future__ import annotations

from pathlib import Path

from reports.report import ReportError, export_to_excel, get_report_rows


class ReportsController:
    """Завантажує записи відвідувань і зберігає їх у файл Excel."""

    def __init__(self, db_path: str | Path | None = None):
        self._db_path = db_path
        self.rows: list[dict] = []

    def load(self) -> list[dict]:
        """Читає з бази актуальні записи (відсортовані за датою й часом)."""
        self.rows = get_report_rows(self._db_path)
        return self.rows

    def export(self, file_path: str | Path) -> str:
        """Зберігає записи, що зараз відображаються, у файл Excel.

        Raises:
            ReportError: якщо немає даних або файл не вдалося зберегти.
        """
        if not self.rows:
            raise ReportError("Немає даних для експорту.")
        return export_to_excel(self.rows, file_path)
