"""
charts.py
~~~~~~~~~
Creates an embeddable Highcharts column chart (HTML string) for the
Advisor card.  Designed for Streamlit's `components.v1.html`.

Public API
----------
build_chart(scores: dict[str, int]) -> str
    `scores` is an **ordered** mapping
        label → score   (0-100)
    Returns a fully-self-contained <script> + <div> snippet.
"""

from __future__ import annotations
import json
import pathlib
import uuid
from .config import (
    BAR_COLOR,
    BG_COLOR,
    HIGHCHARTS_CDN,
    HIGHCHARTS_INTEGRITY,
)

__all__ = ["build_chart", "load_highcharts_script"]

# ───────────────────────── settings ────────────────────────────
LOCAL_JS = pathlib.Path(__file__).parent / "static" / "highcharts" / "highcharts.js"


def load_highcharts_script() -> str:
    """Return a script tag for Highcharts, preferring the local copy."""
    if LOCAL_JS.exists():
        src = LOCAL_JS.as_posix()
        return f'<script src="{src}"></script>'
    return (
        f'<script src="{HIGHCHARTS_CDN}" '
        f'integrity="{HIGHCHARTS_INTEGRITY}" crossorigin="anonymous"></script>'
    )


# ───────────────────────── builder ─────────────────────────────
def build_chart(scores: dict[str, int]) -> str:
    """
    Parameters
    ----------
    scores : dict
        Ordered mapping of x-axis labels ➜ 0-100 integers.

    Returns
    -------
    str
        HTML block ready for `st.components.v1.html`.
    """
    if not scores:
        return "<div style='height:200px'></div>"

    opts = {
        "chart": {
            "type": "column",
            "backgroundColor": BG_COLOR,
            "style": {"fontFamily": "Inter, sans-serif"},
        },
        "title": {"text": None},
        "xAxis": {
            "categories": list(scores.keys()),
            "lineColor": "#ffffff66",
            "labels": {"style": {"color": "#ffffffaa", "fontSize": "10px"}},
        },
        "yAxis": {
            "min": 0,
            "max": 100,
            "gridLineColor": "#33475b",
            "title": {"text": None},
            "labels": {"style": {"color": "#ffffffaa", "fontSize": "10px"}},
        },
        "plotOptions": {
            "column": {
                "pointPadding": 0.1,
                "borderWidth": 0,
                "borderRadius": 3,
            }
        },
        "series": [
            {"name": "Score", "data": list(scores.values()), "color": BAR_COLOR}
        ],
        "legend": {"enabled": False},
        "credits": {"enabled": False},
    }

    div_id = f"chart-{uuid.uuid4().hex[:8]}"

    script = load_highcharts_script()
    return (
        f"<div id='{div_id}' style='width:100%;height:220px;'></div>"
        f"{script}"
        f"<script>Highcharts.chart('{div_id}', {json.dumps(opts)});</script>"
    )


# ────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":
    # quick CLI preview:  python charts.py
    demo = {f"Day {i+1}": v for i, v in enumerate([78, 82, 75, 90, 85, 88, 80])}
    html = build_chart(demo)
    pathlib.Path("_demo.html").write_text(html, encoding="utf8")
    print("Wrote _demo.html – open in browser to preview.")
