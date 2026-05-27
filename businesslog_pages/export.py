"""Exporter — produce PDF-ready text layout from a Report."""

from __future__ import annotations

import textwrap
from typing import Any

from .chart import ChartGenerator
from .report import Report
from .section import BreakdownItem, Metric, Recommendation, Section, SectionType


class Exporter:
    """Export a Report to a structured text layout suitable for PDF conversion."""

    PAGE_WIDTH = 80
    MARGIN = 2

    def __init__(self, page_width: int = 80, include_charts: bool = True):
        self.page_width = page_width
        self.include_charts = include_charts
        self._chart = ChartGenerator()

    def export(self, report: Report) -> str:
        """Produce a paginated, structured text document."""
        w = self.page_width
        content_width = w - 2 * self.MARGIN
        pages: list[str] = []
        current_page: list[str] = []

        def flush():
            if current_page:
                pages.append("\n".join(current_page))
                current_page.clear()

        def add(text: str) -> None:
            for line in text.splitlines():
                wrapped = textwrap.wrap(line, width=content_width) or [""]
                for wl in wrapped:
                    current_page.append(" " * self.MARGIN + wl)
            # Rough page break
            if len(current_page) > 50:
                flush()

        def separator(char: str = "─") -> None:
            add(char * content_width)

        # Title page
        add("")
        add("")
        add(report.title.center(content_width))
        add("")
        if report.author:
            add(f"Prepared by: {report.author}".center(content_width))
        add(f"Date: {report.date}".center(content_width))
        add("")
        add("")

        if report.executive_summary:
            separator("═")
            add("EXECUTIVE SUMMARY")
            separator("═")
            add("")
            for para in report.executive_summary.split("\n\n"):
                add(para.strip())
                add("")

        for section in report.sections:
            separator()
            add(section.title.upper())
            separator()
            add("")

            if section.section_type == SectionType.METRICS:
                self._export_metrics(section, add)
            elif section.section_type == SectionType.TIMELINE:
                self._export_timeline(section, add)
            elif section.section_type == SectionType.BREAKDOWN:
                self._export_breakdown(section, add)
            elif section.section_type == SectionType.RECOMMENDATIONS:
                self._export_recommendations(section, add)
            else:
                for para in section.body.split("\n\n"):
                    add(para.strip())
                add("")

        flush()

        # Join pages with form feed
        document = ""
        for i, page in enumerate(pages):
            if i > 0:
                document += "\n\n--- PAGE BREAK ---\n\n"
            document += page
        return document

    def _export_metrics(self, section: Section, add) -> None:
        for m in section.metrics:
            line = f"  {m.label:<30} {m.formatted_value:>15}"
            if m.change is not None:
                line += f"  {m.change_indicator}"
            add(line)
        add("")

    def _export_timeline(self, section: Section, add) -> None:
        for t in section.timeline:
            tags = f"  [{', '.join(t.tags)}]" if t.tags else ""
            add(f"  [{t.date}]  {t.title}{tags}")
            if t.description:
                add(f"             {t.description}")
        add("")

    def _export_breakdown(self, section: Section, add) -> None:
        labels = [b.label for b in section.breakdown]
        values = [float(b.value) for b in section.breakdown]
        if self.include_charts:
            chart = self._chart.bar_chart(labels, values, width=40, title=section.title)
            add(chart)
            add("")
        for b in section.breakdown:
            pct = f" ({b.percentage:.1f}%)" if b.percentage is not None else ""
            add(f"  {b.label:<30} {b.value:>12,}{pct}")
        add("")

    def _export_recommendations(self, section: Section, add) -> None:
        sorted_recs = sorted(section.recommendations, key=lambda r: r.priority_rank)
        for r in sorted_recs:
            add(f"  [{r.priority.upper():8}]  {r.title}")
            add(f"               Effort: {r.effort}  |  Impact: {r.impact}")
            add(f"               {r.description}")
            add("")
