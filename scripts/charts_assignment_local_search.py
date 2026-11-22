"""assignment-local-search 강의의 그림 설정. m = lesson-assets/measurements.json(= schedulx-benchmark.json 링크)."""
from __future__ import annotations

import charts as ch


SOURCE = "schedulx-benchmark.json"

def _contract_figure() -> str:
    """상태(assignment[]) -> 보조 값(기계별 부하) -> 점수(부하의 최댓값). 개념 그림이라 숫자는 예시다."""
    times = [4, 3, 5, 6, 4, 3]       # 작업 j를 배정된 기계에서 처리하는 시간
    machine = [0, 1, 0, 2, 1, 0]     # assignment[j]
    loads = [0, 0, 0]
    for t, k in zip(times, machine):
        loads[k] += t
    top = max(loads)
    title = "배정 한 줄에서 점수까지"
    c = ch.Canvas()
    y0 = ch._header(c, title, "상태는 assignment[] 하나뿐이고, 부하와 최댓값은 거기서 다시 계산되는 보조 값입니다 (예시 숫자)")
    c.text(28, y0 + 8, 19, "상태 assignment[j] (제출하는 값)", ch.INK, weight="700")
    cw, x0, y = 98, 28, y0 + 22
    for j, k in enumerate(machine):
        x = x0 + j * (cw + 4)
        c.rect(x, y, cw, 62, "#dbe6f7")
        c.text(x + cw / 2, y + 24, 17, f"작업 {j}", ch.MUTED, anchor="middle")
        c.text(x + cw / 2, y + 50, 19, f"기계 {k}", ch.INK, anchor="middle", weight="700")
    y += 62 + 40
    c.text(28, y, 19, "보조 값 load[k] (작업 시간을 기계별로 쌓은 부하)", ch.INK, weight="700")
    unit = 26
    base_y = y + 40 + top * unit
    colx = [150, 330, 510]
    stack = [0, 0, 0]
    for j, (t, k) in enumerate(zip(times, machine)):
        top_y = base_y - (stack[k] + t) * unit
        hot = loads[k] == top
        c.rect(colx[k], top_y + 2, 110, t * unit - 2, "#e1a56f" if hot else "#9db6e0")
        c.text(colx[k] + 55, top_y + t * unit / 2 + 7, 17, f"작업 {j}: {t}", ch.INK, anchor="middle")
        stack[k] += t
    c.line(40, base_y, 690, base_y, ch.MUTED, 1.5)
    for k, x in enumerate(colx):
        hot = loads[k] == top
        c.text(x + 55, base_y + 24, 18, f"기계 {k}: {loads[k]}", ch.ORANGE if hot else ch.INK, anchor="middle", weight="700" if hot else "")
    ty = base_y - top * unit
    c.line(40, ty, 690, ty, ch.ORANGE, 2.5, "8 6")
    c.text(40, ty - 8, 18, f"점수 = 가장 높은 부하 = {top} (작을수록 좋음)", ch.ORANGE, weight="700", halo=True)
    desc = ("작업 6개를 기계 3개에 배정한 예입니다. 상태는 작업마다 기계 번호를 적은 배열 assignment이고, 기계별 부하는 배정된 작업 시간의 합으로 "
            + ", ".join(f"기계 {k} {v}" for k, v in enumerate(loads)) + f"입니다. 점수는 부하의 최댓값 {top}이며 낮을수록 좋습니다.")
    return ch._finish(c, title, desc, base_y + 44)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {"contract-score.svg": _contract_figure()}
    seeds = len(m["seeds"])

    # 1. 단계별: 탐욕 초기해 대비 낮아진 비율
    stg = {s["key"]: s for s in m["stages"]}
    greedy = stg["greedy"]["total"]
    order = [("hill-0", "HC, 점수만", "light"), ("hill-2", "HC + 평균 항", "base"),
             ("sa-0", "SA, 점수만", "light"), ("sa-2", "SA + 평균 항", "hi")]
    rows = [{"label": lab, "value": (greedy - stg[k]["total"]) / greedy * 100, "color": col,
             "text": f"{(greedy - stg[k]['total']) / greedy * 100:.1f}% (합 {ch.comma(stg[k]['total'])})"} for k, lab, col in order]
    desc = (f"탐욕 초기해의 6개 TC 합 {ch.comma(greedy)}보다 각 방식이 얼마나 낮아졌는지 보인 그림입니다. 후보 수는 모두 {ch.comma(m['attempts'])}개입니다. "
            + ", ".join(f"{lab} {r['text']}" for (k, lab, _), r in zip(order, rows))
            + "이고, 실제 점수만 쓴 SA는 hill climbing보다 적게 줄어듭니다.")
    out["stage-gain.svg"] = ch.bar_chart(
        "탐욕 초기해보다 얼마나 낮아졌나", f"TC 6개 합 기준, 후보 수 {ch.comma(m['attempts'])}개로 같게 맞춘 비교입니다. 기준은 탐욕 초기해 합 {ch.comma(greedy)}입니다. HC는 hill climbing, 평균 항은 평균 부하 항입니다",
        desc, rows, "탐욕 대비 합의 감소율 (%) ↑ (클수록 좋음)", value_digits=1)

    # 2. 시작 온도별 합의 시드 분포
    rows = []
    for t in m["temperatures"]:
        f = t["factor"]
        lab = "0 (나쁜 이동 거절)" if f == 0 else f"중앙 손해의 {f:g}배"
        rows.append({"label": lab, "values": [r["total"] for r in t["runs"]], "color": "hi" if f == m["start_factor"] else "base"})
    meds = [ch.median(r["values"]) for r in rows]
    desc = (f"시작 온도를 바꿨을 때 solver seed {seeds}개의 6개 TC 합을 점으로, 중앙값을 세로 눈금으로 보인 그림입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds)) + "입니다. 0.03배에서 0.3배까지는 235,000대로 겹치고 1배 이상에서 나빠집니다.")
    out["temperature-seeds.svg"] = ch.strip_chart(
        "시작 온도별 합의 분포", f"SA, solver seed {seeds}개. 점은 시드 하나, 눈금은 중앙값이며 본문이 쓰는 0.1배를 강조했습니다",
        desc, rows, "TC 6개 합 ↓ (작을수록 좋음)")

    # 3. 평균 부하 항 가중치별 합의 시드 분포
    rows = [{"label": f"가중치 {w['weight']:g}", "values": w["totals"], "color": "hi" if w["weight"] == m["weight"] else "base"} for w in m["weights"]]
    meds = [ch.median(r["values"]) for r in rows]
    desc = (f"평균 부하 항의 가중치를 바꿨을 때 solver seed {seeds}개의 합과 중앙값입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds)) + "이며 가중치 2에서 가장 낮고 0과 8에서 크게 높아집니다.")
    out["weight-seeds.svg"] = ch.strip_chart(
        "평균 부하 항 가중치별 합의 분포", f"SA 시작 온도 0.1배, solver seed {seeds}개. 점은 시드 하나, 눈금은 중앙값입니다. 본문이 쓰는 가중치 2를 강조했습니다",
        desc, rows, "TC 6개 합 ↓ (작을수록 좋음)")
    return out
