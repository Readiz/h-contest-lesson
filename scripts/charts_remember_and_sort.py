"""remember-and-sort 강의의 그림 설정. m = lesson-assets/measurements.json."""
from __future__ import annotations

import charts as ch

PASS_LINE = 250_000_000  # 본문 계약 표의 통과 기준


def _contract_figure(lower: int) -> str:
    """상자 하나를 옮기는 호출의 구성: 하한에 드는 호출과 그 위에 더 쌓이는 호출(모식도, 길이는 비율이 아님)."""
    title = "상자 하나를 옮기는 데 드는 호출"
    c = ch.Canvas()
    y0 = ch._header(c, title, "하한은 pick, drop, 상자를 든 수평 이동만 센 값이고, 빈 손 이동과 수직 이동이 그 위에 쌓입니다 (길이는 모식도)")
    segs = [("빈 손 이동", 90, "lhi", False), ("수직", 70, "lhi", False), ("pick", 34, "base", True), ("든 채 수평 이동", 200, "base", True),
            ("수직", 70, "lhi", False), ("drop", 34, "base", True)]
    total = sum(w for _, w, _, _ in segs)
    x0, x1 = 28, 692
    scale = (x1 - x0 - 3 * (len(segs) - 1)) / total
    y = y0 + 40
    x = x0
    bars = []
    for name, w, col, low in segs:
        ww = w * scale
        c.rect(x, y, ww, 56, ch.COLORS[col])
        bars.append((x, ww, name, low))
        x += ww + 3
    # 칸 안의 글자: 좁은 칸은 위아래로 나눠 쓴다
    for i, (bx, bw, name, low) in enumerate(bars):
        if bw >= 100:
            c.text(bx + bw / 2, y + 34, 17, name, ch.INK, anchor="middle", weight="700")
        else:
            c.text(bx + bw / 2, y + 80 + (24 if i % 2 else 0), 17, name, ch.INK, anchor="middle", weight="700")
            c.line(bx + bw / 2, y + 56, bx + bw / 2, y + 60 + (24 if i % 2 else 0) - 2, ch.MUTED, 1.5)
    # 하한 구간 표시(파랑 세 칸: pick 시작부터 drop 끝까지)
    lx0, lx1 = bars[2][0], bars[5][0] + bars[5][1]
    c.line(lx0, y - 12, lx1, y - 12, ch.BLUE, 3)
    c.text((lx0 + lx1) / 2, y - 20, 18, "하한: 거리 + 2", ch.BLUE, anchor="middle", weight="700")
    ex0, ex1 = bars[0][0], bars[1][0] + bars[1][1]
    c.line(ex0, y - 12, ex1, y - 12, ch.ORANGE, 3)
    c.text((ex0 + ex1) / 2, y - 20, 18, "더 쌓이는 호출", ch.ORANGE, anchor="middle", weight="700")
    c.line(bars[4][0], y - 12, bars[4][0] + bars[4][1], y - 12, ch.ORANGE, 3)
    y += 150
    c.text(28, y, 19, "10개 TC 합으로 본 하한과 통과 기준", ch.INK, weight="700")
    y += 12
    items = [("하한 (거리 + 2의 합)", lower, "base"), ("통과 기준", PASS_LINE, "hi")]
    xb0, xb1 = 28 + 220 + 14, 720 - 28 - 96
    for label, v, col in items:
        c.text(28, y + 25, 19, label, ch.INK, weight="700" if col == "hi" else "")
        c.rect(xb0, y + 5, (xb1 - xb0) * v / PASS_LINE, 26, ch.COLORS[col])
        c.text(xb0 + (xb1 - xb0) * v / PASS_LINE + 8, y + 25, 17, ch.comma(v), ch.INK, halo=True)
        y += 40
    c.text(28, y + 20, 17, f"통과 기준은 하한의 {PASS_LINE / lower:.1f}배입니다", ch.MUTED)
    desc = ("상자 하나를 옮길 때의 호출을 순서대로 나눈 모식도입니다. 빈 손 이동과 수직 이동, pick, 상자를 든 채 수평 이동, 수직 이동, drop 순이고, pick과 drop과 든 채 수평 이동만 센 값이 하한(거리 + 2)이며 "
            f"빈 손 이동과 수직 이동은 그 위에 더 쌓입니다. 아래는 10개 TC 합으로 하한 {ch.comma(lower)}와 통과 기준 {ch.comma(PASS_LINE)}를 비교하고 통과 기준은 하한의 {PASS_LINE / lower:.1f}배입니다.")
    return ch._finish(c, title, desc, y + 36)


def charts(m: dict) -> dict[str, str]:
    st = {s["label"]: s for s in m["stages"]}
    out: dict[str, str] = {"call-parts.svg": _contract_figure(st["기준선"]["lb_total"])}

    # 1. 1단계 대 2단계: 구간별 호출 합(기준선은 정렬·비우기 비중이 달라 눈금 밖)
    names = ["높이 재기", "비우기", "정렬"]
    groups = [{"label": nm, "values": [sum(st["1단계"]["phase"][i]), sum(st["2단계"]["phase"][i])]} for i, nm in enumerate(names)]
    desc = ("1단계와 2단계의 구간별 호출 합(10개 TC)입니다. " + " ".join(f"{g['label']}은 1단계 {ch.comma(g['values'][0])}, 2단계 {ch.comma(g['values'][1])}이고." for g in groups)
            + " 비우기 구간은 두 단계가 같고 2단계는 정렬 구간만 줄입니다. 기준선은 정렬 구간이 " + ch.comma(sum(st["기준선"]["phase"][2])) + "이라 눈금 밖이라 뺐습니다.")
    out["phase-calls.svg"] = ch.grouped_hbar(
        "구간별 호출 합, 1단계와 2단계", "10개 TC 합입니다. 두 단계는 높이 재기와 비우기가 같고 정렬 구간만 다릅니다. 기준선은 눈금 밖이라 뺐습니다",
        desc, groups, [("1단계", "light"), ("2단계", "hi")], "호출 수 ↓ (적을수록 좋음)")

    # 2. 정렬 구간의 호출 종류
    kinds = [("수평 이동", lambda p: p[0]), ("수직 이동", lambda p: p[1]), ("pick + drop", lambda p: p[2] + p[3])]
    groups = [{"label": k, "values": [f(st["1단계"]["phase"][2]), f(st["2단계"]["phase"][2])]} for k, f in kinds]
    desc = ("정렬 구간의 호출을 종류별로 나눈 그림입니다(10개 TC 합). " + " ".join(f"{g['label']}은 1단계 {ch.comma(g['values'][0])}, 2단계 {ch.comma(g['values'][1])}이고." for g in groups)
            + " 2단계의 인내 정렬은 상자를 두 번만 옮겨 모든 종류가 줄고 특히 수직 이동이 크게 줄어듭니다.")
    out["sort-calls.svg"] = ch.grouped_hbar(
        "정렬 구간의 호출 종류", "10개 TC 합입니다. 2단계는 정렬에서 상자를 두 번만 옮겨 호출이 줄어듭니다",
        desc, groups, [("1단계", "light"), ("2단계", "hi")], "호출 수 ↓ (적을수록 좋음)")

    # 3. 경로 선택과 임시 칸 수: 입력 5개의 점수 합
    by: dict[str, list[int]] = {}
    for e in m["experiments"]:
        by.setdefault(e["label"], []).append(e["total"])
    order = [("2단계", "2단계 (본문)", "hi"), ("x 먼저만", "경로: x 먼저만", "base"), ("임시 칸 4개", "임시 칸 4개", "base")]
    rows = [{"label": lab, "values": by[k], "color": col} for k, lab, col in order]
    meds = [ch.median(r["values"]) for r in rows]
    desc = ("생성기 seed를 5, 101, 202, 303, 404로 바꾼 입력 5개에서 설정별 10개 TC 점수 합을 점으로, 중앙값을 눈금으로 보인 그림입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds))
            + "이고 세 설정의 분포가 겹치지 않으며 임시 칸을 4개로 줄이면 가장 많이 나빠집니다.")
    out["choice-seeds.svg"] = ch.strip_chart(
        "경로 선택과 임시 칸 수별 점수", "입력 5개(생성기 seed 5, 101, 202, 303, 404), 10개 TC 점수 합입니다. 점은 입력 하나, 눈금은 5개 중 3번째로 작은 값(중앙값)입니다",
        desc, rows, "10개 TC 점수 합 ↓ (작을수록 좋음)")
    return out
