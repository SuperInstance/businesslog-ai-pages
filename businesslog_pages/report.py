"""Report — top-level container for business log reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from .section import Section


@dataclass
class Report:
    """A complete business report with sections and metadata."""

    title: str
    date: str = field(default_factory=lambda: date.today().isoformat())
    author: str = ""
    executive_summary: str = ""
    sections: list[Section] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_section(self, section: Section) -> "Report":
        self.sections.append(section)
        return self

    @property
    def section_count(self) -> int:
        return len(self.sections)

    def get_section(self, title: str) -> Optional[Section]:
        for s in self.sections:
            if s.title == title:
                return s
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "date": self.date,
            "author": self.author,
            "executive_summary": self.executive_summary,
            "sections": [self._section_dict(s) for s in self.sections],
            "metadata": self.metadata,
        }

    @staticmethod
    def _section_dict(s: Section) -> dict[str, Any]:
        d: dict[str, Any] = {
            "title": s.title,
            "type": s.section_type.value,
            "metadata": s.metadata,
        }
        if s.metrics:
            d["metrics"] = [
                {"label": m.label, "value": m.value, "change": m.change, "unit": m.unit}
                for m in s.metrics
            ]
        if s.timeline:
            d["timeline"] = [
                {"date": t.date, "title": t.title, "description": t.description, "tags": t.tags}
                for t in s.timeline
            ]
        if s.breakdown:
            d["breakdown"] = [
                {"label": b.label, "value": b.value, "percentage": b.percentage}
                for b in s.breakdown
            ]
        if s.recommendations:
            d["recommendations"] = [
                {"title": r.title, "description": r.description, "priority": r.priority}
                for r in s.recommendations
            ]
        if s.body:
            d["body"] = s.body
        return d
