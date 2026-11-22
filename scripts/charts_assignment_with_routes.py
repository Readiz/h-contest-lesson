"""assignment-with-routes 강의의 그림 설정. m = lesson-assets/measurements.json(= taxiassign-benchmark.json 링크)."""
from __future__ import annotations

import charts as ch


def _contract_figure(lower: int, base: int, final: int) -> str:
    """위: 한 기사의 부하를 이루는 두 종류의 구간. 아래: 점수가 하한 위에 얼마나 얹혀 있는지(측정값)."""
    title = "기사 한 명의 부하와 점수의 하한"
    c = ch.Canvas()
    y0 = ch._header(c, title, "탑승 거리는 순서와 무관한 상수이고, 빈 차 구간은 앞 승객이 누구인지에 따라 달라집니다")
    c.text(28, y0 + 8, 19, "한 기사의 이동 순서 (예시)", ch.INK, weight="700")
    ny = y0 + 90
    xs = [72, 214, 356, 498, 640]
    names = ["처음 위치", "승객 0 출발", "승객 0 도착", "승객 1 출발", "승객 1 도착"]
    kinds = ["hop", "ride", "hop", "ride"]
    for i, kind in enumerate(kinds):
        if kind == "ride":
            c.line(xs[i], ny, xs[i + 1], ny, ch.BLUE, 6)
            c.text((xs[i] + xs[i + 1]) / 2, ny - 14, 18, "탑승 (상수)", ch.BLUE, anchor="middle", weight="700")
        else:
            c.line(xs[i], ny, xs[i + 1], ny, ch.ORANGE, 4, "10 7")
            c.text((xs[i] + xs[i + 1]) / 2, ny - 14, 18, "빈 차 (순서에 따름)", ch.ORANGE, anchor="middle", weight="700")
    for x, nm in zip(xs, names):
        c.circle(x, ny, 9, ch.INK, ring=True)
        c.text(x, ny + 34, 17, nm, ch.INK, anchor="middle")
    y = ny + 76
    c.text(28, y, 19, "TC 5개 합으로 본 점수의 구성", ch.INK, weight="700")
    rows = [("탑승 거리 합 ÷ 기사 수 (하한)", lower, None), ("번호 순서 기준선", base, lower), ("결합 탐욕 + 이웃 탐색", final, lower)]
    lw = 250
    x0, x1 = 28 + lw + 14, 720 - 28 - 120
    y += 14
    for label, v, low in rows:
        c.text(28, y + 25, 19, label, ch.INK)
        wlow = (x1 - x0) * (low or v) / base
        c.rect(x0, y + 5, wlow, 26, ch.BLUE)
        if low:
            c.rect(x0 + wlow, y + 5, (x1 - x0) * (v - low) / base, 26, ch.ORANGE)
        c.text(x0 + (x1 - x0) * v / base + 8, y + 25, 17, ch.comma(v), ch.INK, halo=True)
        y += 40
    c.text(28, y + 22, 17, "파랑: 하한, 주황: 하한 위의 빈 차 구간과 기사 간 불균형", ch.MUTED)
    desc = (f"위에는 한 기사가 처음 위치에서 승객 0의 출발지, 도착지, 승객 1의 출발지, 도착지로 움직이는 순서를 보입니다. 탑승 구간은 순서와 무관한 상수이고 빈 차 구간은 앞 승객에 따라 달라집니다. "
            f"아래에는 TC 5개 합으로 하한 {ch.comma(lower)}, 번호 순서 기준선 {ch.comma(base)}, 결합 탐욕과 이웃 탐색 {ch.comma(final)}을 비교합니다. 점수는 낮을수록 좋고 하한을 넘는 부분이 빈 차 구간과 불균형입니다.")
    return ch._finish(c, title, desc, y + 36)


def charts(m: dict) -> dict[str, str]:
    st = {s["key"]: s for s in m["stages"]}
    lower = sum(st["climb"]["rides_per_driver"])
    out: dict[str, str] = {"contract-bound.svg": _contract_figure(lower, st["baseline"]["total"], st["climb"]["total"])}
    seeds = len(m["seeds"])

    # 1. 단계별 합
    order = [("baseline", "번호 % 기사 수", "mute"), ("balance", "배정만", "light"), ("route", "+ 경로만", "light"), ("alternate", "+ 번갈아", "light"),
             ("greedy", "결합 탐욕", "base"), ("alt-climb", "번갈아 + 이웃 탐색", "light"), ("climb", "결합 탐욕 + 탐색", "hi")]
    rows = [{"label": lab, "value": st[k]["total"], "color": col} for k, lab, col in order]
    rows.append({"label": "하한 (참고)", "value": lower, "color": "mute"})
    desc = ("TC 5개 점수 합을 단계별로 비교한 그림입니다. " + ", ".join(f"{lab} {ch.comma(r['value'])}" for (k, lab, _), r in zip(order, rows))
            + f", 하한 {ch.comma(lower)}입니다. 경로만 고쳐도 크게 줄고 결합 탐욕이 가장 큰 한 번의 개선이며 결합 탐욕에서 시작한 이웃 탐색이 통과 기준 {ch.comma(m['pass_line'])}보다 낮은 합을 냅니다.")
    out["stage-totals.svg"] = ch.bar_chart(
        "단계별 TC 5개 합", f"낮을수록 좋습니다. 통과 기준은 {ch.comma(m['pass_line'])}이고, 탐색이 있는 행은 TC마다 제안 400,000개입니다",
        desc, rows, "TC 5개 합 ↓ (작을수록 좋음)")

    # 2. 설정별 시드 분포
    labels = {"본문 설정": "본문 설정", "교환 없이 이동만": "교환 없이 이동만", "승객을 무작위로만 고름(집중 0%)": "무작위로만 고름",
              "평균 부하 항 가중치 0": "가중치 0", "가중치 16": "가중치 16", "대상 기사 후보 1명": "기사 후보 1명",
              "제안 100,000개": "제안 100,000개", "제안 2,000,000개": "제안 2,000,000개"}
    rows = [{"label": labels[e["label"]], "values": e["totals"], "color": "hi" if e["label"] == "본문 설정" else "base"} for e in m["experiments"]]
    meds = [ch.median(r["values"]) for r in rows]
    desc = (f"결합 탐욕에서 시작한 탐색의 설정별 TC 5개 합을 solver seed {seeds}개의 점과 중앙값 눈금으로 보인 그림입니다. 중앙값은 "
            + ", ".join(f"{r['label']} {ch.comma(v)}" for r, v in zip(rows, meds))
            + "입니다. 가중치 0이 가장 나쁘고 무작위로만 고르는 설정이 그다음이며 교환을 빼거나 가중치를 16으로 바꾼 설정은 본문과 시드 폭 안에서 겹칩니다.")
    out["setup-seeds.svg"] = ch.strip_chart(
        "설정별 합의 분포", f"결합 탐욕에서 시작, solver seed {seeds}개. 점은 시드 하나, 눈금은 중앙값이며 본문 설정을 강조했습니다. 제안 수만 다른 행은 시간도 다릅니다",
        desc, rows, "TC 5개 합 ↓ (작을수록 좋음)")
    return out
