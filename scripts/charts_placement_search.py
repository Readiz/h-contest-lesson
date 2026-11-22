"""placement-search 강의의 그림 설정. m = lesson-assets/measurements.json(= landingx-benchmark.json 링크)."""
from __future__ import annotations

import charts as ch


def _contract_figure(m: dict) -> str:
    """후보는 서로 겹친다: 작은 격자 예시와, 겹침을 무시한 상한 대 통과 기준(측정값)."""
    title = "후보는 겹치고, 그래서 상한에 못 미친다"
    st = {s["key"]: s["total"] for s in m["stages"]}
    bound, ps = m["bound_total"], m["pass_score"]
    c = ch.Canvas()
    y0 = ch._header(c, title, "점수는 놓은 우주선 크기의 합이므로 겹치는 후보 중 하나만 고릅니다 (위쪽은 예시 격자)")
    cell, gx, gy = 34, 28, y0 + 14
    cols, rows = 8, 5
    for r in range(rows):
        for q in range(cols):
            c.rect(gx + q * cell, gy + r * cell, cell - 2, cell - 2, "#e7edf7")
    # (행, 열, 높이, 너비, 색, 이름)
    cands = [(0, 0, 3, 3, "#9db6e0", "A"), (1, 2, 3, 3, "#e1a56f", "B"), (3, 5, 2, 3, "#9db6e0", "C")]
    for r, q, h, w, col, nm in cands:
        c.rect(gx + q * cell, gy + r * cell, w * cell - 2, h * cell - 2, col)
    for r, q, h, w, col, nm in cands:
        c.text(gx + q * cell + 8, gy + r * cell + 25, 19, nm, ch.INK, weight="700")
    c.rect(gx + 2 * cell, gy + 1 * cell, cell * 1 - 2, cell * 2 - 2, "#8a3b0b")
    c.text(gx + 8 * cell + 22, gy + 30, 18, "A와 B는 겹치는 후보", ch.INK, weight="700")
    c.text(gx + 8 * cell + 22, gy + 58, 18, "(진한 칸이 겹침)", ch.MUTED)
    c.text(gx + 8 * cell + 22, gy + 94, 18, "A, C 또는 B, C처럼", ch.INK)
    c.text(gx + 8 * cell + 22, gy + 120, 18, "겹치지 않게 골라야 합니다", ch.INK)
    y = gy + rows * cell + 34
    c.text(28, y, 19, "10개 TC 합 (클수록 좋음)", ch.INK, weight="700")
    items = [("겹침을 무시한 상한", bound, "mute"), ("통과 기준", ps, "hi"), ("점수 큰 순 탐욕", st["weight"], "base"), ("후보 번호 순 기준선", st["first-fit"], "light")]
    lw = 250
    x0, x1 = 28 + lw + 14, 720 - 28 - 96
    y += 12
    for label, v, col in items:
        c.text(28, y + 25, 19, label, ch.INK, weight="700" if col == "hi" else "")
        c.rect(x0, y + 5, (x1 - x0) * v / bound, 26, ch.COLORS[col])
        c.text(x0 + (x1 - x0) * v / bound + 8, y + 25, 17, ch.comma(v), ch.INK, halo=True)
        y += 40
    desc = ("위쪽의 예시 격자에는 후보 A, B, C가 있고 A와 B는 일부 칸이 겹쳐 둘 중 하나만 고를 수 있습니다. 아래에는 10개 TC 합으로 겹침을 무시한 상한 "
            f"{ch.comma(bound)}, 통과 기준 {ch.comma(ps)}, 점수 큰 순 탐욕 {ch.comma(st['weight'])}, 후보 번호 순 기준선 {ch.comma(st['first-fit'])}을 비교합니다. 점수는 클수록 좋고 상한과 통과 기준의 차이가 겹침에서 나옵니다.")
    return ch._finish(c, title, desc, y + 8)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {"contract-overlap.svg": _contract_figure(m)}
    seeds = len(m["seeds"])
    ps = m["pass_score"]
    st = {s["key"]: s["total"] for s in m["stages"]}

    # 1. 단계별: 통과 기준까지 모자란 점수
    order = [("weight", "점수 큰 순 탐욕", "base"), ("hill", "국소 이동", "light"), ("dr", "destroy/repair", "hi")]
    rows = [{"label": lab, "value": ps - st[k], "color": col,
             "text": "0 (통과 기준 도달)" if ps - st[k] == 0 else ch.comma(ps - st[k])} for k, lab, col in order]
    desc = (f"통과 기준 {ch.comma(ps)}에서 각 방식의 합을 뺀 모자란 점수입니다. " + ", ".join(f"{lab} {r['text']}" for (k, lab, _), r in zip(order, rows))
            + f"이고 destroy/repair가 기준에 닿습니다. 후보 번호 순 기준선은 {ch.comma(ps - st['first-fit'])} 모자라 눈금 밖이라 뺐습니다.")
    out["stage-gap.svg"] = ch.bar_chart(
        "통과 기준까지 모자란 점수", f"10개 TC 합, 후보 검사 {ch.comma(m['stage_budget'])}회로 맞춘 비교입니다. 후보 번호 순 기준선({ch.comma(ps - st['first-fit'])} 모자람)은 눈금 밖이라 뺐습니다",
        desc, rows, "통과 기준 대비 모자란 점수 ↓ (작을수록 좋음)")

    # 2. destroy 방식·크기별 시드 분포
    kinds = {0: "한 영역, 여백 {}칸", 1: "무작위 {}개", 2: "낮은 점수 {}개"}
    rows = [{"label": kinds[d["mode"]].format(d["size"]), "values": d["totals"], "color": "base"} for d in m["destroy"]]
    best = max(range(len(rows)), key=lambda i: m["destroy"][i]["median"])
    rows[best]["color"] = "hi"
    meds = [ch.median(r["values"]) for r in rows]
    desc = (f"후보 검사 {ch.comma(m['table_budget'])}회로 고정해 destroy 방식과 크기를 바꿨을 때 solver seed {seeds}개의 합을 점으로, 중앙값을 눈금으로 보인 그림입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds))
            + "입니다. 낮은 점수의 후보를 빼는 방식은 다른 방식보다 눈에 띄게 낮고 나머지는 분포가 많이 겹칩니다.")
    out["destroy-seeds.svg"] = ch.strip_chart(
        "destroy 방식과 크기별 합의 분포", f"후보 검사 {ch.comma(m['table_budget'])}회, solver seed {seeds}개. 점은 시드 하나, 눈금은 중앙값이며 중앙값이 가장 높은 행을 강조했습니다",
        desc, rows, "10개 TC 합 ↑ (클수록 좋음)")

    # 3. 다시 채울 때의 무작위 배율별 시드 분포
    rows = []
    for n in m["noise"]:
        lab = "없음 (점수 순서 그대로)" if n["noise"] == 0 else f"1배 ~ {1 + n['noise'] / 100:g}배"
        rows.append({"label": lab, "values": n["totals"], "color": "hi" if n["noise"] == 200 else "base"})
    meds = [ch.median(r["values"]) for r in rows]
    desc = (f"다시 채울 때 점수에 곱하는 무작위 배율을 바꿨을 때 solver seed {seeds}개의 합과 중앙값입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds))
            + "이며 배율이 없으면 탐욕과 같은 값이고, 넓힐수록 오르다가 3배와 5배는 분포가 겹칩니다.")
    out["noise-seeds.svg"] = ch.strip_chart(
        "다시 채울 때의 무작위 배율별 합의 분포", f"후보 검사 {ch.comma(m['table_budget'])}회, solver seed {seeds}개. 점은 시드 하나, 눈금은 중앙값이며 본문이 쓰는 3배를 강조했습니다",
        desc, rows, "10개 TC 합 ↑ (클수록 좋음)")
    return out
