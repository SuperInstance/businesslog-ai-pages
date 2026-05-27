"""ChartGenerator — ASCII charts for terminal reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


# Block characters for bar fills
_BAR_CHARS = "▁▂▃▄▅▆▇█"
_HALF_BLOCK = "▌"


class ChartGenerator:
    """Generate ASCII-based charts for inline reporting."""

    @staticmethod
    def bar_chart(
        labels: Sequence[str],
        values: Sequence[float],
        width: int = 40,
        title: str = "",
    ) -> str:
        """Horizontal bar chart."""
        if not values:
            return ""
        max_val = max(values) or 1
        lines: list[str] = []
        if title:
            lines.append(title)
            lines.append("=" * len(title))
        max_label_len = max(len(l) for l in labels) if labels else 0
        for label, val in zip(labels, values):
            bar_len = int(val / max_val * width)
            bar = "█" * bar_len
            lines.append(f"{label:>{max_label_len}} │{bar} {val:,.1f}")
        return "\n".join(lines)

    @staticmethod
    def line_chart(
        values: Sequence[float],
        width: int = 60,
        height: int = 10,
        title: str = "",
        labels: Sequence[str] | None = None,
    ) -> str:
        """ASCII line chart using a grid of characters."""
        if len(values) < 2:
            return ""
        min_val = min(values)
        max_val = max(values) or 1
        val_range = max_val - min_val or 1
        lines: list[str] = []
        if title:
            lines.append(title)
            lines.append("=" * len(title))

        grid: list[list[str]] = [
            [" " for _ in range(width)] for _ in range(height)
        ]

        # Plot points
        for i, v in enumerate(values):
            x = int(i / (len(values) - 1) * (width - 1)) if len(values) > 1 else 0
            y = int((max_val - v) / val_range * (height - 1))
            y = max(0, min(height - 1, y))
            grid[y][x] = "●"

        # Draw connecting lines (simple horizontal between consecutive points)
        for i in range(len(values) - 1):
            x1 = int(i / (len(values) - 1) * (width - 1))
            x2 = int((i + 1) / (len(values) - 1) * (width - 1))
            y1 = int((max_val - values[i]) / val_range * (height - 1))
            y2 = int((max_val - values[i + 1]) / val_range * (height - 1))
            y1 = max(0, min(height - 1, y1))
            y2 = max(0, min(height - 1, y2))
            for x in range(x1 + 1, x2):
                y_approx = int(y1 + (y2 - y1) * (x - x1) / max(x2 - x1, 1))
                y_approx = max(0, min(height - 1, y_approx))
                if grid[y_approx][x] == " ":
                    grid[y_approx][x] = "─"

        for row in grid:
            lines.append("".join(row))

        # Axis labels
        if labels and len(labels) >= 2:
            lines.append(labels[0].ljust(width - len(labels[-1])) + labels[-1])
        else:
            lines.append(f"{min_val:.1f}" + " " * (width - 14) + f"{max_val:.1f}")

        return "\n".join(lines)

    @staticmethod
    def pie_chart(
        labels: Sequence[str],
        values: Sequence[float],
        width: int = 30,
        title: str = "",
    ) -> str:
        """ASCII pie chart (horizontal stacked bar + legend)."""
        if not values:
            return ""
        total = sum(values) or 1
        lines: list[str] = []
        if title:
            lines.append(title)
            lines.append("=" * len(title))

        # Stacked bar
        chars = ["█", "▓", "▒", "░", "■", "▪"]
        bar = ""
        for i, v in enumerate(values):
            segment_len = max(1, int(v / total * width))
            bar += chars[i % len(chars)] * segment_len
        bar = bar[:width]
        lines.append(bar)
        lines.append("")

        # Legend
        for i, (label, v) in enumerate(zip(labels, values)):
            pct = v / total * 100
            c = chars[i % len(chars)]
            lines.append(f"  {c} {label}: {v:,.1f} ({pct:.1f}%)")

        return "\n".join(lines)

    @staticmethod
    def sparkline(values: Sequence[float]) -> str:
        """Compact sparkline using Unicode block elements."""
        if not values:
            return ""
        min_v = min(values)
        max_v = max(values)
        rng = max_v - min_v or 1
        return "".join(
            _BAR_CHARS[min(int((v - min_v) / rng * (len(_BAR_CHARS) - 1)), len(_BAR_CHARS) - 1)]
            for v in values
        )
