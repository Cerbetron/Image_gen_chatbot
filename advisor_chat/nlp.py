"""Robust date-range extractor for the Advisor chatbot.

Public function::

    parse_request(user_text) -> {"start": date, "end": date} | None
"""

import re
import json
from datetime import date, timedelta
import dateparser
from . import data_source as ds
from .ollama_fallback import chat as chat_with_ollama
from .config import OLLAMA_MODEL, OLLAMA_URL

__all__ = ["parse_request"]

# ────────────────────────── helpers ───────────────────────────
def _detect_lang(text: str) -> str:
    if re.search(r"[àèìòù]", text, re.I):
        return "it"
    if re.search(r"[áéíóúñ]", text, re.I):
        return "es"
    return "en"

def _to_date(x):
    if isinstance(x, date):
        return x
    if hasattr(x, "date"):  # datetime
        return x.date()
    return None

def _today():
    if ds is not None:
        try:
            return ds.get_last_date()
        except Exception:
            pass
    return date.today()

def _last_n_days(n):
    today = _today()
    return today - timedelta(days=n - 1), today

def _months_ago(n: int) -> date:
    y = _today().year
    m = _today().month - n
    while m <= 0:
        m += 12
        y -= 1
    d = min(_today().day, [31,29 if y%4==0 and (y%100!=0 or y%400==0) else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date(y, m, d)

def _last_n_months(n: int):
    start = _months_ago(n) + timedelta(days=1 - _today().day)
    return start, _today()

def _weekend(offset=0):
    today = _today()
    saturday = today + timedelta((5 - today.weekday()) % 7 + 7*offset)
    return saturday, saturday + timedelta(days=1)

def _this_week():
    today = _today()
    monday = today - timedelta(days=today.weekday())
    return monday, today

def _last_week():
    monday = _this_week()[0] - timedelta(days=7)
    return monday, monday + timedelta(days=6)

def _this_month():
    today = _today()
    return today.replace(day=1), today

def _last_month():
    today = _today()
    first_prev = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_prev = today.replace(day=1) - timedelta(days=1)
    return first_prev, last_prev

# ─────────────────────── rule-based pass ──────────────────────
RELATIVE_PATTERNS = [
    (re.compile(r"\bpast (\d{1,2}) days\b"), lambda m: _last_n_days(int(m[1]))),
    (re.compile(r"\blast (\d{1,2}) days\b"), lambda m: _last_n_days(int(m[1]))),
    (re.compile(r"\blast (\d{1,2}) weeks\b"), lambda m: _last_n_days(int(m[1]) * 7)),
    (re.compile(r"\blast (\d{1,2}) months\b"), lambda m: _last_n_months(int(m[1]))),
]

def _rule_parse(txt: str):
    t = txt.lower()

    # fixed phrases
    if any(k in t for k in ("this week", "current week", "past week")):
        return _this_week()
    if "last week" in t or "previous week" in t:
        return _last_week()
    if "this month" in t or "current month" in t:
        return _this_month()
    if "last month" in t or "previous month" in t:
        return _last_month()
    if "yesterday" in t:
        d = _today() - timedelta(days=1)
        return d, d
    if "today" in t:
        d = _today()
        return d, d
    if "tomorrow" in t:
        d = _today() + timedelta(days=1)
        return d, d
    if "fortnight" in t:
        return _last_n_days(14)
    if "weekend" in t:
        if "last" in t or "past" in t:
            return _weekend(-1)
        return _weekend(0)

    # numeric “last/past N days/weeks”
    for patt, fn in RELATIVE_PATTERNS:
        m = patt.search(t)
        if m:
            return fn(m)

    # explicit ISO “YYYY-MM-DD … YYYY-MM-DD”
    m = re.search(r"(\d{4}-\d{2}-\d{2})\s*[\s–\-tountil]+\s*(\d{4}-\d{2}-\d{2})", t)
    if m:
        return date.fromisoformat(m[1]), date.fromisoformat(m[2])

    return None

# ───────────────────── dateparser fallback ────────────────────
def _dateparser_parse(txt: str):
    """
    Tries to parse expressions like:
      “from 3 Jun to 17 Jun”, “since last Monday”, “until yesterday”.
    """
    lang = _detect_lang(txt)

    # from X to Y
    m = re.search(r"from (.+?) (?:to|until|till) (.+)", txt, re.I)
    if m:
        d1 = _to_date(dateparser.parse(m[1], languages=[lang]))
        d2 = _to_date(dateparser.parse(m[2], languages=[lang]))
        if d1 and d2:
            return d1, d2

    # since X  →  X .. today
    m = re.search(r"since (.+)", txt, re.I)
    if m:
        d1 = _to_date(dateparser.parse(m[1], languages=[lang]))
        if d1:
            return d1, _today()

    # until / till X  →  ??? .. X  (default 7 days back)
    m = re.search(r"(?:until|till) (.+)", txt, re.I)
    if m:
        d2 = _to_date(dateparser.parse(m[1], languages=[lang]))
        if d2:
            return d2 - timedelta(days=6), d2

    # single “yesterday”, “today” etc.  →  that day only
    single = dateparser.parse(txt, languages=[lang])
    if single:
        d = _to_date(single)
        return d, d

    return None

# ───────────────────── llama3.2 fallback ───────────────────────
def _llama_parse(txt: str):
    pl = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Return JSON only: {\"start\":\"YYYY-MM-DD\",\"end\":\"YYYY-MM-DD\"}",
            },
            {"role": "user", "content": txt},
        ],
    }
    try:
        import requests
        r = requests.post(OLLAMA_URL, json=pl, timeout=20).json()
        obj = json.loads(r["message"]["content"])
        return date.fromisoformat(obj["start"]), date.fromisoformat(obj["end"])
    except Exception:
        return None

# ───────────────────────── public API ─────────────────────────
def parse_request(user_text: str):
    """
    Returns dict {'start': date, 'end': date} or None.
    Order of attempts: rules ➜ dateparser ➜ llama.
    """
    for strategy in (_rule_parse, _dateparser_parse, _llama_parse):
        res = strategy(user_text)
        if res:
            s, e = res
            if s and e and s <= e:
                return {"start": s, "end": e}
    return None
