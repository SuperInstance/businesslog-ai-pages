"""Section types for business log reports."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Optional


class SectionType(enum.Enum):
    """Kinds of report sections."""

    METRICS = "metrics"
    TIMELINE = "timeline"
    BREAKDOWN = "breakdown"
    RECOMMENDATIONS = "recommendations"
    NARRATIVE = "narrative"
    CUSTOM = "custom"


@dataclass
class Metric:
    """A single numeric metric with optional change indicator."""

    label: str
    value: float | int | str
    change: Optional[float] = None  # percentage change, e.g. +12.5
    unit: str = ""
    lower_is_better: bool = False

    @property
    def formatted_value(self) -> str:
        if isinstance(self.value, float):
            return f"{self.value:,.2f}{self.unit}"
        return f"{self.value:,}{self.unit}"

    @property
    def change_indicator(self) -> str:
        if self.change is None:
            return ""
        arrow = "↑" if self.change > 0 else "↓" if self.change < 0 else "→"
        good = (self.change > 0) != self.lower_is_better
        color_hint = "green" if good else "red" if self.change != 0 else "neutral"
        return f"{arrow} {abs(self.change):+.1f}% ({color_hint})"


@dataclass
class TimelineEntry:
    """An event on a timeline."""

    date: str
    title: str
    description: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class BreakdownItem:
    """A named slice of a breakdown (e.g. category revenue)."""

    label: str
    value: float | int
    percentage: Optional[float] = None
    color: Optional[str] = None


@dataclass
class Recommendation:
    """An actionable recommendation."""

    title: str
    description: str
    priority: str = "medium"  # low / medium / high / critical
    effort: str = "medium"  # low / medium / high
    impact: str = "medium"  # low / medium / high

    @property
    def priority_rank(self) -> int:
        return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(self.priority, 2)


@dataclass
class Section:
    """A section within a report."""

    title: str
    section_type: SectionType
    # Content varies by type
    metrics: list[Metric] = field(default_factory=list)
    timeline: list[TimelineEntry] = field(default_factory=list)
    breakdown: list[BreakdownItem] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    body: str = ""  # for narrative / custom text
    metadata: dict[str, Any] = field(default_factory=dict)
