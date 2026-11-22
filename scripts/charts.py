"""강의 실험 차트용 순수 Python SVG 생성기 (외부 패키지 없음, 같은 입력이면 바이트까지 같은 결과).

모든 차트 함수는 완성된 SVG 문자열을 돌려준다. 규격: viewBox 폭 720, 글자 16~28(제목 27), 정수 글자 크기,
role="img", <title>, <desc>, 천 단위 쉼표 눈금, 색은 파랑(강조 아닌 기본) / 연한 파랑 / 주황(강조) 계열.
강의별로 어떤 measurements 키를 어떤 차트로 그릴지는 scripts/generate_charts.py 에 적는다.

    bar_chart      가로(orient="h")·세로("v") 막대. 항상 0에서 시작한다.
    grouped_hbar   묶음 가로 막대(같은 항목의 두 측정을 나란히).
    line_chart     꺾은선. 가로·세로 축 모두 로그 눈금 지원.
    strip_chart    점 분포: 항목마다 시드별 점과 중앙값 눈금.
    winloss_chart  시드 n개를 나음 / 결정 못 함 / 못함으로 나눈 누적 막대.
"""
from __future__ import annotations

import math
from typing import Sequence

W = 720
INK = "#172b45"
MUTED = "#53657d"
GRID = "#d8e1ed"
BG = "#f6f8fc"
BLUE = "#2664ce"
LBLUE = "#9db6e0"
ORANGE = "#ae5515"
GRAY = "#c3cddb"
LORANGE = "#e1a56f"
COLORS = {"base": BLUE, "light": LBLUE, "hi": ORANGE, "lhi": LORANGE, "mute": GRAY}


# ------------------------------------------------------------------ helpers
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def comma(v: float, digits: int | None = None) -> str:
    """천 단위 쉼표. 정수면 정수로, 아니면 소수 첫째 자리까지(digits로 고정 가능)."""
    if digits is not None:
        return f"{v:,.{digits}f}"
    if abs(v - round(v)) < 1e-9:
        return f"{int(round(v)):,}"
    return f"{v:,.1f}"


def median(xs: Sequence[float]) -> float:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def tw(body: str, size: int) -> float:
    """글자 폭 추정(검사 스크립트와 같은 규칙: 한글 등 1.0em, 그 밖 0.55em)."""
    return sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in body)


def wrap(text: str, size: int, maxw: float) -> list[str]:
    lines: list[str] = []
    cur = ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if tw(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def nice_ticks(lo: float, hi: float, target: int = 5) -> list[float]:
    """lo..hi를 덮는 보기 좋은 눈금(1·2·5 단위)."""
    span = hi - lo
    raw = span / max(target, 1)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    start = math.floor(lo / step + 1e-9) * step
    out = []
    v = start
    while v < hi + step * 0.999:
        out.append(round(v, 10))
        if v >= hi - 1e-9:
            break
        v += step
    return out


def thin(ticks: Sequence[float], x0: float, x1: float, lo: float, hi: float, size: int = 16, digits: int | None = None) -> list[float]:
    """가로 눈금 라벨이 서로 겹치면 하나씩 건너뛰어 남긴다."""
    step = 1
    while step <= len(ticks):
        keep = list(ticks[::step])
        xs = [x0 + (x1 - x0) * (t - lo) / (hi - lo) for t in keep]
        ok = all(xs[i + 1] - xs[i] >= (tw(comma(keep[i], digits), size) + tw(comma(keep[i + 1], digits), size)) / 2 + 14 for i in range(len(keep) - 1))
        if ok:
            return keep
        step += 1
    return [ticks[0]]


class Canvas:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.grid: list[str] = []  # 눈금선은 맨 아래 층에 그려 막대와 값 글자를 가리지 않게 한다

    def text(self, x: float, y: float, size: int, body: str, fill: str = INK, anchor: str = "start",
             weight: str = "", halo: bool = False) -> None:
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        w = f' font-weight="{weight}"' if weight else ""
        h = f' stroke="{BG}" stroke-width="4" paint-order="stroke" stroke-linejoin="round"' if halo else ""
        self.parts.append(f'<text x="{num(x)}" y="{num(y)}" font-size="{size}" fill="{fill}"{a}{w}{h}>{esc(body)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, fill: str, rx: float = 0) -> None:
        r = f' rx="{num(rx)}"' if rx else ""
        self.parts.append(f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}"{r} fill="{fill}"/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str = GRID, width: float = 1.5, dash: str = "") -> None:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        target = self.grid if stroke == GRID and not dash else self.parts
        target.append(f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}" stroke="{stroke}" stroke-width="{num(width)}"{d}/>')

    def circle(self, x: float, y: float, r: float, fill: str, opacity: float = 1.0, ring: bool = False) -> None:
        o = f' fill-opacity="{num(opacity)}"' if opacity != 1.0 else ""
        rg = f' stroke="{BG}" stroke-width="2"' if ring else ""
        self.parts.append(f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{fill}"{o}{rg}/>')

    def polyline(self, pts: Sequence[tuple[float, float]], stroke: str, width: float = 3, dash: str = "") -> None:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{num(x)},{num(y)}" for x, y in pts)
        self.parts.append(f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{num(width)}" stroke-linejoin="round" stroke-linecap="round"{d}/>')

    def raw(self, s: str) -> None:
        self.parts.append(s)


def _header(c: Canvas, title: str, subtitle: str, legend: Sequence[tuple[str, str, str]] = ()) -> float:
    """제목·부제·범례를 그리고 본문이 시작할 y를 돌려준다. legend: (kind, color, label), kind는 box|line|dot."""
    c.rect(28, 29, 6, 29, BLUE, rx=3)
    c.text(47, 53, 27, title, INK, weight="750")
    y = 84.0
    for ln in wrap(subtitle, 19, W - 56):
        c.text(28, y, 19, ln, MUTED)
        y += 25
    y -= 25
    if legend:
        y += 28
        x = 28.0
        for kind, color, label in legend:
            w = tw(label, 18) + 34 + 22
            if x + w > W - 24:
                x = 28.0
                y += 28
            if kind == "box":
                c.rect(x, y - 12, 14, 14, color)
            elif kind == "line":
                c.line(x, y - 5, x + 20, y - 5, color, 3.5)
                c.circle(x + 10, y - 5, 4.5, color)
            else:
                c.circle(x + 7, y - 5, 6, color)
            c.text(x + (28 if kind == "line" else 22), y, 18, label, INK)
            x += w + (6 if kind == "line" else 0)
    return y + 22


def _finish(c: Canvas, title: str, desc: str, height: float) -> str:
    h = int(math.ceil(height))
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{esc(title)}</title>\n<desc id="desc">{esc(desc)}</desc>\n'
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}*{box-sizing:border-box}</style>\n'
            f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="20" fill="{BG}" stroke="{GRID}" stroke-width="1.5"/>\n')
    return head + "\n".join(c.grid + c.parts) + "\n</svg>\n"


def _axis_title(c: Canvas, y: float, text: str) -> None:
    c.text(W / 2, y, 17, text, MUTED, anchor="middle")


# ------------------------------------------------------------------ bars
def bar_chart(title: str, subtitle: str, desc: str, rows: Sequence[dict], axis_label: str, orient: str = "h",
              value_digits: int | None = None, legend: Sequence[tuple[str, str, str]] = ()) -> str:
    """rows: {label, value, color('base'|'light'|'hi'|'mute'), text(선택: 막대 끝 라벨)}. 막대는 0에서 시작한다."""
    c = Canvas()
    y0 = _header(c, title, subtitle, legend)
    vmax = max(r["value"] for r in rows)
    ticks = nice_ticks(0, vmax, 4)
    top = ticks[-1]
    labels = [r.get("text") or comma(r["value"], value_digits) for r in rows]
    if orient == "h":
        lw = max(tw(r["label"], 19) for r in rows)
        assert lw <= 250, f"label column too wide: {lw}"
        vw = max(tw(t, 17) for t in labels) + 10
        x0 = 28 + lw + 14
        x1 = W - 28 - vw
        assert x1 - x0 >= 220, "bars too narrow"
        row_h = 40
        y = y0 + 8
        top_y = y
        for r, lab in zip(rows, labels):
            col = COLORS[r.get("color", "base")]
            bw = (x1 - x0) * r["value"] / top
            c.text(28, y + 26, 19, r["label"], INK, weight="700" if r.get("color") == "hi" else "")
            c.rect(x0, y + 6, bw, 26, col)
            c.text(x0 + bw + 8, y + 26, 17, lab, INK, weight="700" if r.get("color") == "hi" else "", halo=True)
            y += row_h
        bottom = y
        shown = thin(ticks, x0, x1, 0, top)
        for t in ticks:
            gx = x0 + (x1 - x0) * t / top
            c.line(gx, top_y, gx, bottom, GRID, 1.5)
            if t in shown:
                c.text(gx, bottom + 22, 16, comma(t), MUTED, anchor="middle")
        c.line(x0, top_y, x0, bottom, MUTED, 1.5)
        _axis_title(c, bottom + 50, axis_label)
        return _finish(c, title, desc, bottom + 66)
    # vertical
    plot_h = 280
    lab_w = max(tw(comma(t), 16) for t in ticks)
    x0 = 28 + lab_w + 12
    x1 = W - 28
    y_top = y0 + 30
    y_bot = y_top + plot_h
    slot = (x1 - x0) / len(rows)
    for t in ticks:
        gy = y_bot - plot_h * t / top
        c.line(x0, gy, x1, gy, GRID, 1.5)
        c.text(x0 - 8, gy + 5, 16, comma(t), MUTED, anchor="end")
    for i, (r, lab) in enumerate(zip(rows, labels)):
        col = COLORS[r.get("color", "base")]
        bw = min(56, slot * 0.62)
        cx = x0 + slot * (i + 0.5)
        bh = plot_h * r["value"] / top
        c.rect(cx - bw / 2, y_bot - bh, bw, bh, col)
        c.text(cx, y_bot - bh - 8, 17, lab, INK, anchor="middle", weight="700" if r.get("color") == "hi" else "", halo=True)
        c.text(cx, y_bot + 24, 18, r["label"], INK, anchor="middle", weight="700" if r.get("color") == "hi" else "")
    c.line(x0, y_bot, x1, y_bot, MUTED, 1.5)
    _axis_title(c, y_bot + 54, axis_label)
    return _finish(c, title, desc, y_bot + 70)


def grouped_hbar(title: str, subtitle: str, desc: str, groups: Sequence[dict], series: Sequence[tuple[str, str]],
                 axis_label: str) -> str:
    """groups: {label, values:[v1, v2, ...], texts:[선택]}. series: [(이름, color)]. 막대 끝에 값 라벨."""
    c = Canvas()
    y0 = _header(c, title, subtitle, [("box", COLORS[col], name) for name, col in series])
    vmax = max(v for g in groups for v in g["values"])
    ticks = nice_ticks(0, vmax, 4)
    top = ticks[-1]
    lw = max(tw(g["label"], 19) for g in groups)
    assert lw <= 250, f"label column too wide: {lw}"
    texts = [[(g.get("texts") or [None] * len(g["values"]))[i] or comma(v) for i, v in enumerate(g["values"])] for g in groups]
    vw = max(tw(t, 17) for row in texts for t in row) + 10
    x0 = 28 + lw + 14
    x1 = W - 28 - vw
    y = y0 + 6
    top_y = y
    bh = 24
    for g, txt in zip(groups, texts):
        c.text(28, y + 6 + bh + 6, 19, g["label"], INK, weight="700")
        yy = y + 6
        for (name, col), v, t in zip(series, g["values"], txt):
            bw = max((x1 - x0) * v / top, 1.5)
            c.rect(x0, yy, bw, bh, COLORS[col])
            c.text(x0 + bw + 8, yy + 19, 17, t, INK, halo=True)
            yy += bh + 4
        y += 12 + len(series) * (bh + 4) + 10
    bottom = y
    shown = thin(ticks, x0, x1, 0, top)
    for t in ticks:
        gx = x0 + (x1 - x0) * t / top
        c.line(gx, top_y, gx, bottom, GRID, 1.5)
        if t in shown:
            c.text(gx, bottom + 22, 16, comma(t), MUTED, anchor="middle")
    c.line(x0, top_y, x0, bottom, MUTED, 1.5)
    _axis_title(c, bottom + 50, axis_label)
    return _finish(c, title, desc, bottom + 66)


# ------------------------------------------------------------------ lines
def line_chart(title: str, subtitle: str, desc: str, series: Sequence[dict], xticks: Sequence[tuple[float, str]],
               yticks: Sequence[tuple[float, str]], xlog: bool, ylog: bool, xlabel: str, ylabel: str,
               hlines: Sequence[dict] = (), height: int = 300) -> str:
    """series: {name, color, points:[(x,y)], labels:'all'|'last'|'none', label_idx:[...](선택), fmt:함수(선택), pos:'up'|'down', dash(선택), marker_only(선택)}.
    hlines: {y, label, color} 기준선. xticks·yticks는 (값, 라벨). 축 범위는 눈금의 첫·끝 값."""
    c = Canvas()
    legend = [("dot" if s.get("marker_only") else "line", COLORS[s["color"]], s["name"]) for s in series]
    y0 = _header(c, title, subtitle, legend)
    lab_w = max(tw(t, 16) for _, t in yticks)
    x0 = 28 + lab_w + 12
    x1 = W - 40
    c.text(28, y0 + 4, 17, ylabel, MUTED)
    y_top = y0 + 18
    y_bot = y_top + height

    pad = 38  # 첫·끝 점의 라벨이 축과 가장자리에 걸리지 않게 안쪽으로 들인다

    def fx(v: float) -> float:
        lo, hi = xticks[0][0], xticks[-1][0]
        t = (math.log(v / lo) / math.log(hi / lo)) if xlog else (v - lo) / (hi - lo)
        return x0 + pad + (x1 - x0 - 2 * pad) * t

    def fy(v: float) -> float:
        lo, hi = yticks[0][0], yticks[-1][0]
        t = (math.log(v / lo) / math.log(hi / lo)) if ylog else (v - lo) / (hi - lo)
        return y_bot - (y_bot - y_top) * t

    for v, lab in yticks:
        c.line(x0, fy(v), x1, fy(v), GRID, 1.5)
        c.text(x0 - 8, fy(v) + 5, 16, lab, MUTED, anchor="end")
    for v, lab in xticks:
        c.line(fx(v), y_top, fx(v), y_bot, GRID, 1.0)
        c.text(fx(v), y_bot + 24, 16, lab, MUTED, anchor="middle")
    c.line(x0, y_bot, x1, y_bot, MUTED, 1.5)
    c.line(x0, y_top, x0, y_bot, MUTED, 1.5)
    for h in hlines:
        c.line(x0, fy(h["y"]), x1, fy(h["y"]), COLORS[h["color"]], 2.5, dash="8 6")
        c.text(x1, fy(h["y"]) - 8, 17, h["label"], INK, anchor="end", halo=True)
    for s in series:
        col = COLORS[s["color"]]
        pts = [(fx(x), fy(y)) for x, y in s["points"]]
        if not s.get("marker_only") and len(pts) > 1:
            c.polyline(pts, col, 3.5, s.get("dash", ""))
        for (px, py) in pts:
            c.circle(px, py, 6 if s.get("marker_only") else 5, col, ring=True)
        mode = s.get("labels", "all")
        if "label_idx" in s:
            idx = list(s["label_idx"])
        else:
            idx = list(range(len(pts))) if mode == "all" else ([len(pts) - 1] if mode == "last" else [])
        fmt = s.get("fmt", comma)
        for i in idx:
            px, py = pts[i]
            lab = fmt(s["points"][i][1])
            dy = -13 if s.get("pos", "up") == "up" else 26
            ax = "middle"
            lx = px
            if px + tw(lab, 17) / 2 > W - 12:
                ax, lx = "end", px + 8
            elif px - tw(lab, 17) / 2 < x0 + 2:
                ax, lx = "start", px - 8
            c.text(lx, py + dy, 17, lab, INK, anchor=ax, halo=True, weight="700" if s.get("marker_only") else "")
    _axis_title(c, y_bot + 54, xlabel)
    return _finish(c, title, desc, y_bot + 70)


# ------------------------------------------------------------------ strip
def strip_chart(title: str, subtitle: str, desc: str, rows: Sequence[dict], axis_label: str, tick_digits: int | None = None,
                median_label: str = "중앙값") -> str:
    """rows: {label, values:[시드별 값], color}. 점은 시드, 세로 눈금은 중앙값(오른쪽에 숫자)."""
    c = Canvas()
    y0 = _header(c, title, subtitle, [("dot", BLUE, "시드 하나"), ("line", INK, median_label)])
    lo = min(v for r in rows for v in r["values"])
    hi = max(v for r in rows for v in r["values"])
    ticks = nice_ticks(lo, hi, 4)
    a, b = ticks[0], ticks[-1]
    lw = max(tw(r["label"], 19) for r in rows)
    assert lw <= 250, f"label column too wide: {lw}"
    meds = [median(r["values"]) for r in rows]
    mtexts = [comma(m) for m in meds]
    mw = max(tw(t, 17) for t in mtexts) + 12
    x0 = 28 + lw + 14
    x1 = W - 28 - mw
    assert x1 - x0 >= 220, "plot too narrow"
    row_h = 44
    y = y0 + 8
    top_y = y
    bottom = y + row_h * len(rows)
    shown = thin(ticks, x0, x1, a, b, 16, tick_digits)
    for t in ticks:
        gx = x0 + (x1 - x0) * (t - a) / (b - a)
        c.line(gx, top_y, gx, bottom, GRID, 1.5)
        if t in shown:
            c.text(gx, bottom + 22, 16, comma(t, tick_digits), MUTED, anchor="middle")
    for r, m, mt in zip(rows, meds, mtexts):
        cy = y + row_h / 2
        c.text(28, cy + 6, 19, r["label"], INK)
        for v in r["values"]:
            c.circle(x0 + (x1 - x0) * (v - a) / (b - a), cy, 5.5, COLORS[r.get("color", "base")], opacity=0.55)
        mx = x0 + (x1 - x0) * (m - a) / (b - a)
        c.line(mx, cy - 15, mx, cy + 15, INK, 3.5)
        c.text(x1 + 12, cy + 6, 17, mt, INK)
        y += row_h
    c.line(x0, top_y, x0, bottom, MUTED, 1.5)
    _axis_title(c, bottom + 50, axis_label)
    return _finish(c, title, desc, bottom + 66)


# ------------------------------------------------------------------ win / loss
def winloss_chart(title: str, subtitle: str, desc: str, rows: Sequence[dict], n: int, axis_label: str,
                  names: tuple[str, str | None, str] = ("기준보다 나음", None, "기준보다 못함")) -> str:
    """rows: {label, better, worse, text(오른쪽 열), ref(True면 기준 행: 막대 없이 '기준' 표시)}. 시드 n개를 누적 막대로."""
    c = Canvas()
    y0 = _header(c, title, subtitle, [("box", BLUE, names[0])] + ([("box", GRAY, names[1])] if names[1] else []) + [("box", ORANGE, names[2])])
    lw = max(tw(r["label"], 19) for r in rows)
    assert lw <= 250, f"label column too wide: {lw}"
    tw_right = max(tw(r["text"], 17) for r in rows) + 10
    x0 = 28 + lw + 14
    x1 = W - 28 - tw_right
    assert x1 - x0 >= 200, "bars too narrow"
    unit = (x1 - x0) / n
    row_h = 38
    y = y0 + 8
    for r in rows:
        c.text(28, y + 26, 19, r["label"], INK)
        if r.get("ref"):
            c.rect(x0, y + 7, x1 - x0, 24, GRID)
            c.text(x0 + (x1 - x0) / 2, y + 26, 17, "기준", MUTED, anchor="middle")
        else:
            better, worse = r["better"], r["worse"]
            tie = n - better - worse
            x = x0
            for cnt, col in ((better, BLUE), (tie, GRAY), (worse, ORANGE)):
                if cnt:
                    c.rect(x, y + 7, unit * cnt, 24, col)
                    if unit * cnt >= 34:
                        c.text(x + unit * cnt / 2, y + 26, 17, str(cnt), "#ffffff", anchor="middle", weight="700")
                    x += unit * cnt
            # 조각 사이 2px 간격
            x = x0
            for cnt in (better, tie):
                x += unit * cnt
                if 0 < x - x0 < x1 - x0:
                    c.line(x, y + 7, x, y + 31, BG, 2)
        c.text(x1 + 12, y + 26, 17, r["text"], INK)
        y += row_h
    bottom = y
    c.line(x0, y0 + 8, x0, bottom, MUTED, 1.5)
    _axis_title(c, bottom + 28, axis_label)
    return _finish(c, title, desc, bottom + 44)
