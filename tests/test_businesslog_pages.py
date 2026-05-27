"""Tests for businesslog_pages."""

import pytest

from businesslog_pages import (
    BreakdownItem,
    ChartGenerator,
    Exporter,
    Format,
    Metric,
    Recommendation,
    Report,
    Renderer,
    Section,
    SectionType,
    TimelineEntry,
)


# ── Helpers ──────────────────────────────────────────────

def _sample_report() -> Report:
    return (
        Report(
            title="Q1 Business Review",
            author="Jane Doe",
            date="2026-01-15",
            executive_summary="Strong quarter with 23% revenue growth.",
        )
        .add_section(Section(
            title="Key Metrics",
            section_type=SectionType.METRICS,
            metrics=[
                Metric("Revenue", 1_250_000, change=23.0, unit="$"),
                Metric("Churn Rate", 4.2, change=-1.5, unit="%", lower_is_better=True),
                Metric("Active Users", 8400, change=12.0),
            ],
        ))
        .add_section(Section(
            title="Timeline",
            section_type=SectionType.TIMELINE,
            timeline=[
                TimelineEntry("2026-01-05", "Product Launch", "Shipped v2.0", tags=["product"]),
                TimelineEntry("2026-01-12", "Partnership Signed", "Acme Corp", tags=["sales"]),
            ],
        ))
        .add_section(Section(
            title="Revenue Breakdown",
            section_type=SectionType.BREAKDOWN,
            breakdown=[
                BreakdownItem("SaaS", 750000, percentage=60.0),
                BreakdownItem("Consulting", 300000, percentage=24.0),
                BreakdownItem("Training", 200000, percentage=16.0),
            ],
        ))
        .add_section(Section(
            title="Recommendations",
            section_type=SectionType.RECOMMENDATIONS,
            recommendations=[
                Recommendation("Expand sales team", "Hire 3 AEs for EMEA", priority="high", effort="high", impact="high"),
                Recommendation("Reduce onboarding friction", "Simplify signup flow", priority="critical", effort="low", impact="medium"),
                Recommendation("Blog more", "Weekly posts", priority="low", effort="medium", impact="low"),
            ],
        ))
        .add_section(Section(
            title="Notes",
            section_type=SectionType.NARRATIVE,
            body="This quarter showed promising growth across all segments.",
        ))
    )


# ── Metric tests ─────────────────────────────────────────

class TestMetric:
    def test_formatted_value_int(self):
        m = Metric("Users", 8400)
        assert m.formatted_value == "8,400"

    def test_formatted_value_float_with_unit(self):
        m = Metric("Rate", 4.2, unit="%")
        assert m.formatted_value == "4.20%"

    def test_change_indicator_positive(self):
        m = Metric("Rev", 100, change=12.5)
        ind = m.change_indicator
        assert "↑" in ind
        assert "12.5" in ind

    def test_change_indicator_negative_lower_better(self):
        m = Metric("Churn", 4.2, change=-1.5, lower_is_better=True)
        ind = m.change_indicator
        assert "↓" in ind
        assert "green" in ind

    def test_change_indicator_none(self):
        m = Metric("X", 1)
        assert m.change_indicator == ""


# ── Recommendation tests ─────────────────────────────────

class TestRecommendation:
    def test_priority_rank(self):
        r1 = Recommendation("A", "desc", priority="critical")
        r2 = Recommendation("B", "desc", priority="high")
        r3 = Recommendation("C", "desc", priority="medium")
        r4 = Recommendation("D", "desc", priority="low")
        assert r1.priority_rank < r2.priority_rank < r3.priority_rank < r4.priority_rank


# ── Report tests ─────────────────────────────────────────

class TestReport:
    def test_add_section(self):
        r = Report(title="Test")
        s = Section(title="S1", section_type=SectionType.NARRATIVE, body="hello")
        r.add_section(s)
        assert r.section_count == 1
        assert r.get_section("S1") is s

    def test_get_section_missing(self):
        r = Report(title="Test")
        assert r.get_section("nope") is None

    def test_to_dict(self):
        r = _sample_report()
        d = r.to_dict()
        assert d["title"] == "Q1 Business Review"
        assert len(d["sections"]) == 5
        assert d["sections"][0]["type"] == "metrics"
        assert len(d["sections"][0]["metrics"]) == 3


# ── Renderer tests ───────────────────────────────────────

class TestRenderer:
    def test_text_render(self):
        r = _sample_report()
        text = Renderer(Format.TEXT).render(r)
        assert "Q1 Business Review" in text
        assert "EXECUTIVE SUMMARY" in text
        assert "Revenue" in text
        assert "Product Launch" in text
        assert "CRITICAL" in text  # recommendation sorted

    def test_markdown_render(self):
        r = _sample_report()
        md = Renderer(Format.MARKDOWN).render(r)
        assert "# Q1 Business Review" in md
        assert "## Executive Summary" in md
        assert "| Metric | Value | Change |" in md
        assert "`product`" in md

    def test_html_render(self):
        r = _sample_report()
        html = Renderer(Format.HTML).render(r)
        assert "<!DOCTYPE html>" in html
        assert "<h1>Q1 Business Review</h1>" in html
        assert "<table>" in html
        assert "Executive Summary" in html

    def test_html_escaping(self):
        r = Report(title="Test <script>", executive_summary="A & B")
        r.add_section(Section(title="S", section_type=SectionType.NARRATIVE, body="<b>bold</b>"))
        html = Renderer(Format.HTML).render(r)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "A &amp; B" in html


# ── Chart tests ──────────────────────────────────────────

class TestChartGenerator:
    def test_bar_chart(self):
        chart = ChartGenerator.bar_chart(
            ["A", "B", "C"], [10, 20, 15], title="Test"
        )
        assert "Test" in chart
        assert "A" in chart
        assert "█" in chart

    def test_bar_chart_empty(self):
        assert ChartGenerator.bar_chart([], []) == ""

    def test_line_chart(self):
        chart = ChartGenerator.line_chart([1, 3, 2, 5, 4], title="Trend")
        assert "Trend" in chart
        assert "●" in chart

    def test_line_chart_single_value(self):
        assert ChartGenerator.line_chart([5]) == ""

    def test_pie_chart(self):
        chart = ChartGenerator.pie_chart(
            ["SaaS", "Consult"], [60, 40], title="Split"
        )
        assert "Split" in chart
        assert "SaaS" in chart
        assert "60.0%" in chart

    def test_sparkline(self):
        sp = ChartGenerator.sparkline([1, 3, 5, 7, 9])
        assert len(sp) == 5
        assert sp[-1] == "█"

    def test_sparkline_empty(self):
        assert ChartGenerator.sparkline([]) == ""


# ── Exporter tests ───────────────────────────────────────

class TestExporter:
    def test_export(self):
        r = _sample_report()
        doc = Exporter(page_width=60, include_charts=False).export(r)
        assert "Q1 BUSINESS REVIEW" in doc or "Q1 Business Review" in doc
        assert "EXECUTIVE SUMMARY" in doc
        assert "Recommendations" in doc.upper() or "RECOMMENDATIONS" in doc

    def test_export_with_charts(self):
        r = _sample_report()
        doc = Exporter(page_width=80, include_charts=True).export(r)
        assert "█" in doc  # chart chars

    def test_export_wrapping(self):
        r = Report(title="Test")
        long_text = "word " * 100
        r.add_section(Section(
            title="Long",
            section_type=SectionType.NARRATIVE,
            body=long_text,
        ))
        doc = Exporter(page_width=40).export(r)
        # No line should exceed page width by much
        for line in doc.splitlines():
            assert len(line) <= 50  # some margin


# ── Section type coverage ────────────────────────────────

class TestSectionTypes:
    def test_custom_section(self):
        r = Report(title="T")
        r.add_section(Section(title="Custom", section_type=SectionType.CUSTOM, body="custom body"))
        text = Renderer(Format.TEXT).render(r)
        assert "custom body" in text

    def test_empty_section(self):
        r = Report(title="T")
        r.add_section(Section(title="Empty", section_type=SectionType.METRICS))
        md = Renderer(Format.MARKDOWN).render(r)
        assert "Empty" in md


# ── Package-level imports ───────────────────────────────

class TestImports:
    def test_all_exports(self):
        import businesslog_pages
        for name in businesslog_pages.__all__:
            assert hasattr(businesslog_pages, name)

    def test_version(self):
        import businesslog_pages
        assert businesslog_pages.__version__.startswith("0.")
