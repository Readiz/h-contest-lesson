"""beam-search 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch

WIDTH_TICKS = [1, 2, 4, 8, 16, 64, 256, 1024]


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["seeds"])
    g = m["grid"]["est"]
    r = m["route"]["est"]

    def med(rows: list[dict], w: int) -> int:
        return next(x["median"] for x in rows if x["width"] == w)

    # 1. 격자 수집: 폭에 따른 점수
    gs = [("추정 없음", "light", g["0"]["rows"]), ("가까운 값의 합", "base", g["1"]["rows"]), ("거리 벌점", "hi", g["2"]["rows"])]
    series = [{"name": n, "color": c, "points": [(x["width"], x["median"]) for x in rows], "labels": "none",
               "label_idx": {"추정 없음": [0], "가까운 값의 합": [0, len(rows) - 1], "거리 벌점": [0]}[n], "pos": "up"} for n, c, rows in gs]
    desc = (f"격자 수집에서 폭(로그 눈금)을 늘릴 때 시드 {seeds}개 중 10번째로 작은 점수입니다. 폭 1에서 추정 없음 " + ch.comma(med(g["0"]["rows"], 1))
            + ", 가까운 값의 합 " + ch.comma(med(g["1"]["rows"], 1)) + ", 거리 벌점 " + ch.comma(med(g["2"]["rows"], 1)) + "이고, 폭 1,024에서 각각 "
            + ch.comma(med(g["0"]["rows"], 1024)) + ", " + ch.comma(med(g["1"]["rows"], 1024)) + ", " + ch.comma(med(g["2"]["rows"], 1024))
            + "입니다. 추정이 있으면 좁은 폭에서 크게 앞서고, 폭이 커지면 세 곡선이 가까워지며, 곡선은 중간에 오르내립니다.")
    out["grid-width.svg"] = ch.line_chart(
        "폭을 늘릴 때의 점수 (격자 수집)", f"20×20, T=60, 시드 {seeds}개 중 10번째로 작은 점수. 클수록 좋습니다",
        desc, series, xticks=[(w, ch.comma(w)) for w in WIDTH_TICKS], yticks=[(v, str(v)) for v in (100, 150, 200, 250, 300)],
        xlog=True, ylog=False, xlabel="빔 폭 (로그 눈금)", ylabel="점수 ↑ (클수록 좋음)", height=280)

    # 2. 격자 수집: 같은 연산 수에서 비교
    series = [{"name": n, "color": c, "points": [(x["ops"], x["median"]) for x in rows], "labels": "none",
               "label_idx": [0, len(rows) - 1] if n == "추정 없음" else [], "pos": "up"} for n, c, rows in gs]
    eq = m["grid"]["equalOps"][0]
    desc = (f"격자 수집에서 연산 수(평가 횟수와 추정이 살핀 칸의 합, 로그 눈금)를 가로로, 시드 {seeds}개 중 10번째로 작은 점수를 세로로 둔 그림입니다. "
            "점은 폭 1, 2, 4, 8, 16, 64, 256, 1,024 순서입니다. 같은 연산 수에서는 추정 없음 곡선이 추정 있는 곡선보다 위에 있습니다. 예를 들어 "
            f"가까운 값의 합 폭 1(연산 {ch.comma(eq['with']['ops'])}, 점수 {eq['with']['median']})보다 추정 없음 폭 16(연산 {ch.comma(eq['without']['ops'])}, 점수 {eq['without']['median']})이 "
            f"더 적은 연산으로 더 높습니다.")
    out["grid-ops.svg"] = ch.line_chart(
        "같은 연산 수에서의 점수 (격자 수집)", "같은 실험을 평가 + 살핀 칸 수로 다시 그렸습니다. 점 하나가 폭 하나",
        desc, series, xticks=[(10 ** k, ch.comma(10 ** k)) for k in range(2, 8)], yticks=[(v, str(v)) for v in (100, 150, 200, 250, 300)],
        xlog=True, ylog=False, xlabel="연산 수 (로그 눈금)", ylabel="점수 ↑ (클수록 좋음)", height=280)

    # 3. 순서 문제: 폭에 따른 비용
    rs = [("추정 없음", "light", r["0"]["rows"]), ("낙관적 합", "base", r["1"]["rows"]), ("탐욕 완성", "hi", r["2"]["rows"])]
    series = [{"name": n, "color": c, "points": [(x["width"], x["median"]) for x in rows], "labels": "none",
               "label_idx": [0, len(rows) - 1] if n == "탐욕 완성" else [len(rows) - 1], "pos": "up"} for n, c, rows in rs]
    desc = (f"순서 문제에서 폭(로그 눈금)을 늘릴 때 시드 {seeds}개 중 10번째로 작은 비용입니다. 추정 없음은 폭 1의 " + ch.comma(med(r["0"]["rows"], 1))
            + "에서 폭 256의 " + ch.comma(med(r["0"]["rows"], 256)) + "으로, 낙관적 합은 " + ch.comma(med(r["1"]["rows"], 1)) + "에서 " + ch.comma(med(r["1"]["rows"], 256))
            + "으로 오르내리다 조금 줄고, 탐욕 완성은 폭 1에서 8까지 " + ch.comma(med(r["2"]["rows"], 1)) + "에서 " + ch.comma(med(r["2"]["rows"], 8))
            + "로 줄어 모든 폭에서 가장 낮습니다.")
    out["route-width.svg"] = ch.line_chart(
        "폭을 늘릴 때의 비용 (순서 문제)", f"N=200, 시드 {seeds}개 중 10번째로 작은 비용. 작을수록 좋습니다. 탐욕 완성은 폭 8까지",
        desc, series, xticks=[(w, ch.comma(w)) for w in (1, 2, 4, 8, 16, 64, 256)], yticks=[(v, ch.comma(v)) for v in (14_000, 15_000, 16_000, 17_000, 18_000)],
        xlog=True, ylog=False, xlabel="빔 폭 (로그 눈금)", ylabel="비용 ↓ (작을수록 좋음)", height=280)

    # 4. 작은 입력에서 최적에 닿은 시드 수
    sr = m["smallRoute"]
    series = [
        {"name": "추정 없음, 합침", "color": "light", "points": [(e["width"], e["est0"]["optimal"]) for e in sr], "labels": "none", "label_idx": [3], "pos": "down"},
        {"name": "낙관적 합, 합침", "color": "base", "points": [(e["width"], e["est1"]["optimal"]) for e in sr], "labels": "none", "label_idx": [3, 4], "pos": "up"},
        {"name": "낙관적 합, 합치지 않음", "color": "hi", "points": [(e["width"], e["est1nomerge"]["optimal"]) for e in sr], "labels": "none", "label_idx": [4], "pos": "down", "dash": "8 6"},
    ]
    at = {e["width"]: e for e in sr}
    desc = ("점 10개의 순서 입력(시드 20개)에서 폭(로그 눈금)별로 최적에 닿은 시드의 수입니다. 폭 16에서 추정 없음은 " + str(at[16]["est0"]["optimal"])
            + "개, 낙관적 합(합침)은 " + str(at[16]["est1"]["optimal"]) + "개, 낙관적 합(합치지 않음)은 " + str(at[16]["est1nomerge"]["optimal"])
            + "개입니다. 폭 256부터 모두 20개이고, 같은 폭에서 낙관적 합이 추정 없음보다 자주 최적에 닿습니다.")
    out["small-optimal.svg"] = ch.line_chart(
        "작은 입력에서 최적에 닿은 시드 수", f"점 10개 순서 입력, 시드 {seeds}개. 최적은 부분집합 DP로 따로 구했습니다. 폭 1,536은 합칠 때 버리는 후보가 없습니다",
        desc, series, xticks=[(w, ch.comma(w)) for w in (1, 2, 4, 8, 16, 64, 256, 1536)], yticks=[(v, str(v)) for v in (0, 5, 10, 15, 20)],
        xlog=True, ylog=False, xlabel="빔 폭 (로그 눈금)", ylabel="최적에 닿은 시드 수 ↑ (20개 중)", height=260)
    return out
