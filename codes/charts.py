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

__all__ = ["build_chart"]

# ───────────────────────── settings ────────────────────────────
# 1.  Use CDN by default; if you copy highcharts.js into
#     ./static/highcharts/highcharts.js  it will load locally.
LOCAL_JS = pathlib.Path(__file__).parent / "static" / "highcharts" / "highcharts.js"
HCHARTS_SRC = (
    LOCAL_JS.as_posix()
    if LOCAL_JS.exists()
    else "https://code.highcharts.com/highcharts.js"
)

# 2.  Styling
BAR_COLOR = "#00c2ff"       # cyan
BG_COLOR  = "#0c2144"       # same as advisor card


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

    return f"""
    <div id="{div_id}" style="width:100%;height:220px;"></div>
    <script src="{HCHARTS_SRC}"></script>
    <script>
      Highcharts.chart("{div_id}", {json.dumps(opts)});
    </script>
    """


# ────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":
    # quick CLI preview:  python charts.py
    demo = {f"Day {i+1}": v for i, v in enumerate([78, 82, 75, 90, 85, 88, 80])}
    html = build_chart(demo)
    pathlib.Path("_demo.html").write_text(html, encoding="utf8")
    print("Wrote _demo.html – open in browser to preview.")
