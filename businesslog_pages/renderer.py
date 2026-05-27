"""Renderer — produces text, markdown, or HTML from a Report."""

from __future__ import annotations

import enum
from typing import Any

from .report import Report
from .section import (
    BreakdownItem,
    Metric,
    Recommendation,
    Section,
    SectionType,
    TimelineEntry,
)


class Format(enum.Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


class Renderer:
    """Render a Report into various output formats."""

    def __init__(self, fmt: Format = Format.MARKDOWN):
        self.fmt = fmt

    def render(self, report: Report) -> str:
        dispatch = {
            Format.TEXT: self._render_text,
            Format.MARKDOWN: self._render_markdown,
            Format.HTML: self._render_html,
        }
        return dispatch[self.fmt](report)

    # ── Text ────────────────────────────────────────────────

    def _render_text(self, report: Report) -> str:
        lines: list[str] = []
        lines.append(report.title)
        lines.append("=" * len(report.title))
        if report.author:
            lines.append(f"Author: {report.author}")
        lines.append(f"Date: {report.date}")
        lines.append("")
        if report.executive_summary:
            lines.append("EXECUTIVE SUMMARY")
            lines.append("-" * 17)
            lines.append(report.executive_summary)
            lines.append("")
        for section in report.sections:
            lines.extend(self._section_text(section))
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _section_text(self, s: Section) -> list[str]:
        lines = [s.title, "-" * len(s.title)]
        if s.section_type == SectionType.METRICS:
            for m in s.metrics:
                line = f"  {m.label}: {m.formatted_value}"
                if m.change_indicator:
                    line += f"  {m.change_indicator}"
                lines.append(line)
        elif s.section_type == SectionType.TIMELINE:
            for t in s.timeline:
                lines.append(f"  [{t.date}] {t.title}")
                if t.description:
                    lines.append(f"    {t.description}")
        elif s.section_type == SectionType.BREAKDOWN:
            for b in s.breakdown:
                pct = f" ({b.percentage:.1f}%)" if b.percentage is not None else ""
                lines.append(f"  {b.label}: {b.value:,}{pct}")
        elif s.section_type == SectionType.RECOMMENDATIONS:
            sorted_recs = sorted(s.recommendations, key=lambda r: r.priority_rank)
            for r in sorted_recs:
                lines.append(f"  [{r.priority.upper()}] {r.title}")
                lines.append(f"    {r.description}")
        elif s.body:
            for bl in s.body.splitlines():
                lines.append(f"  {bl}")
        return lines

    # ── Markdown ────────────────────────────────────────────

    def _render_markdown(self, report: Report) -> str:
        lines: list[str] = []
        lines.append(f"# {report.title}")
        lines.append("")
        meta_parts = []
        if report.author:
            meta_parts.append(f"**Author:** {report.author}")
        meta_parts.append(f"**Date:** {report.date}")
        lines.append(" | ".join(meta_parts))
        lines.append("")
        if report.executive_summary:
            lines.append("## Executive Summary")
            lines.append("")
            lines.append(report.executive_summary)
            lines.append("")
        for section in report.sections:
            lines.extend(self._section_markdown(section))
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _section_markdown(self, s: Section) -> list[str]:
        lines = [f"## {s.title}", ""]
        if s.section_type == SectionType.METRICS:
            lines.append("| Metric | Value | Change |")
            lines.append("|--------|-------|--------|")
            for m in s.metrics:
                change = m.change_indicator or "—"
                lines.append(f"| {m.label} | {m.formatted_value} | {change} |")
            lines.append("")
        elif s.section_type == SectionType.TIMELINE:
            for t in s.timeline:
                tag_str = " ".join(f"`{tg}`" for tg in t.tags) if t.tags else ""
                lines.append(f"- **{t.date}** — {t.title} {tag_str}")
                if t.description:
                    lines.append(f"  > {t.description}")
        elif s.section_type == SectionType.BREAKDOWN:
            lines.append("| Category | Value | Share |")
            lines.append("|----------|-------|-------|")
            for b in s.breakdown:
                pct = f"{b.percentage:.1f}%" if b.percentage is not None else "—"
                lines.append(f"| {b.label} | {b.value:,} | {pct} |")
            lines.append("")
        elif s.section_type == SectionType.RECOMMENDATIONS:
            sorted_recs = sorted(s.recommendations, key=lambda r: r.priority_rank)
            for r in sorted_recs:
                lines.append(f"### {r.title} (`{r.priority}`)")
                lines.append(f"- Effort: {r.effort} | Impact: {r.impact}")
                lines.append(f"- {r.description}")
                lines.append("")
        elif s.body:
            lines.append(s.body)
        return lines

    # ── HTML ────────────────────────────────────────────────

    def _render_html(self, report: Report) -> str:
        parts: list[str] = [
            "<!DOCTYPE html>",
            '<html lang="en"><head>',
            '<meta charset="UTF-8">',
            f"<title>{_esc(report.title)}</title>",
            "<style>",
            "body{font-family:system-ui,sans-serif;max-width:800px;margin:2em auto;color:#222;line-height:1.6;}",
            "h1{border-bottom:2px solid #3d7fff;padding-bottom:.3em;}",
            "h2{color:#3d7fff;margin-top:1.5em;}",
            "table{border-collapse:collapse;width:100%;margin:.5em 0;}",
            "th,td{border:1px solid #ddd;padding:.4em .8em;text-align:left;}",
            "th{background:#f5f5f5;}",
            ".summary{background:#f0f4ff;padding:1em;border-radius:6px;}",
            ".rec-critical{border-left:4px solid #e53e3e;padding-left:.5em;}",
            ".rec-high{border-left:4px solid #ed8936;padding-left:.5em;}",
            ".rec-medium{border-left:4px solid #ecc94b;padding-left:.5em;}",
            ".rec-low{border-left:4px solid #38a169;padding-left:.5em;}",
            "</style></head><body>",
            f"<h1>{_esc(report.title)}</h1>",
        ]
        meta = []
        if report.author:
            meta.append(f"Author: {_esc(report.author)}")
        meta.append(f"Date: {report.date}")
        parts.append(f"<p><small>{' | '.join(meta)}</small></p>")
        if report.executive_summary:
            parts.append('<div class="summary">')
            parts.append(f"<h2>Executive Summary</h2>")
            parts.append(f"<p>{_esc(report.executive_summary)}</p>")
            parts.append("</div>")
        for section in report.sections:
            parts.extend(self._section_html(section))
        parts.append("</body></html>")
        return "\n".join(parts)

    def _section_html(self, s: Section) -> list[str]:
        parts = [f"<h2>{_esc(s.title)}</h2>"]
        if s.section_type == SectionType.METRICS:
            parts.append("<table><tr><th>Metric</th><th>Value</th><th>Change</th></tr>")
            for m in s.metrics:
                change = m.change_indicator or "—"
                parts.append(f"<tr><td>{_esc(m.label)}</td><td>{_esc(m.formatted_value)}</td><td>{_esc(change)}</td></tr>")
            parts.append("</table>")
        elif s.section_type == SectionType.TIMELINE:
            parts.append("<ul>")
            for t in s.timeline:
                tags = " ".join(f"<code>{_esc(tg)}</code>" for tg in t.tags)
                parts.append(f"<li><strong>{t.date}</strong> — {_esc(t.title)} {tags}")
                if t.description:
                    parts.append(f"<br><em>{_esc(t.description)}</em>")
                parts.append("</li>")
            parts.append("</ul>")
        elif s.section_type == SectionType.BREAKDOWN:
            parts.append("<table><tr><th>Category</th><th>Value</th><th>Share</th></tr>")
            for b in s.breakdown:
                pct = f"{b.percentage:.1f}%" if b.percentage is not None else "—"
                parts.append(f"<tr><td>{_esc(b.label)}</td><td>{b.value:,}</td><td>{pct}</td></tr>")
            parts.append("</table>")
        elif s.section_type == SectionType.RECOMMENDATIONS:
            for r in sorted(s.recommendations, key=lambda r: r.priority_rank):
                parts.append(f'<div class="rec-{r.priority}">')
                parts.append(f"<h3>{_esc(r.title)} <small>({r.priority})</small></h3>")
                parts.append(f"<p>Effort: {r.effort} | Impact: {r.impact}</p>")
                parts.append(f"<p>{_esc(r.description)}</p>")
                parts.append("</div>")
        elif s.body:
            parts.append(f"<p>{_esc(s.body)}</p>")
        return parts


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
