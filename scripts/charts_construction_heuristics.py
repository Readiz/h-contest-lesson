"""construction-heuristics 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["meta"]["inputSeeds"])

    # 1. 순서 틀: 구성 직후 길이의 시드별 분포
    order = [("strip8", "세로 띠 8개"), ("nn", "가장 가까운 점(NN)"), ("cheapest", "가장 싼 삽입"),
             ("farthest", "가장 먼 점 삽입"), ("regret", "후회 삽입")]
    rows = [{"label": lab, "values": m["path"][k]["init"], "color": "hi" if k == "regret" else "base"} for k, lab in order]
    meds = {k: ch.median(m["path"][k]["init"]) for k, _ in order}
    desc = (f"순서 틀에서 구성법마다 입력 시드 {seeds}개의 구성 직후 경로 길이를 점으로 찍고 중앙값을 세로 눈금으로 보인 그림입니다. "
            + ", ".join(f"{lab} {ch.comma(meds[k])}" for k, lab in order)
            + "이며 후회 삽입이 가장 짧고 분포도 다른 구성법과 거의 겹치지 않습니다. 번호 순서(중앙값 "
            + ch.comma(ch.median(m["path"]["identity"]["init"])) + ")는 눈금 밖이라 그리지 않았습니다.")
    out["construction-cost.svg"] = ch.strip_chart(
        "구성법별 구성 직후 경로 길이", f"순서 틀(점 200개), 시드 {seeds}개. 점은 시드 하나, 눈금은 중앙값입니다. 짧을수록 좋습니다. 번호 순서는 눈금 밖이라 뺐습니다",
        desc, rows, "구성 직후 경로 길이 ↓ (작을수록 좋음)")

    # 2. 세로 띠 수에 따른 비용
    keys = sorted(m["strips"], key=int)
    med = {k: ch.median(m["strips"][k]) for k in keys}
    best = min(keys, key=lambda k: med[k])
    rows = [{"label": k, "value": med[k], "color": "hi" if k == best else "base"} for k in keys]
    desc = (f"세로 띠 수 {', '.join(keys)}개에서 경로 길이의 중앙값입니다. 값은 "
            + ", ".join(ch.comma(med[k]) for k in keys) + f"이고 띠 {best}개에서 가장 짧습니다. 띠가 너무 적거나 많으면 길어집니다.")
    out["strip-count.svg"] = ch.bar_chart(
        "세로 띠 수에 따른 경로 길이", f"띠 수를 바꾼 정렬 기준 구성, 시드 {seeds}개의 중앙값. 가장 짧은 띠 수를 강조했습니다",
        desc, rows, "세로 띠 수 (개), 막대 높이는 경로 길이 중앙값 ↓", orient="v")

    # 3. 여러 번 만들기: 평가 횟수 대 길이
    rp = m["randomPath"]

    def point(k: str) -> tuple[float, float]:
        return (rp[k]["evals"][0], ch.median(rp[k]["cost"]))

    nn = [point(k) for k in ("nn1", "nn4", "nn16", "nn64")]
    series = [
        {"name": "NN, 첫 점 무작위 가장 좋은 것 (1·4·16·64번)", "color": "base", "points": nn, "labels": "all", "pos": "down"},
        {"name": "NN 64번, 10% 흔들기", "color": "light", "points": [point("nnShake64")], "marker_only": True, "labels": "all", "pos": "up"},
        {"name": "후회 삽입 1번", "color": "hi", "points": [point("regret1")], "marker_only": True, "labels": "all", "pos": "down"},
        {"name": "후회 삽입 + 25% 흔들기 5번", "color": "lhi", "points": [point("regretShake5")], "marker_only": True, "labels": "all", "pos": "up"},
    ]
    desc = ("순서 틀에서 구성에 쓴 평가 횟수(로그 눈금)와 경로 길이 중앙값의 관계입니다. NN을 첫 점 무작위로 1, 4, 16, 64번 만들면 "
            + ", ".join(ch.comma(p[1]) for p in nn) + "로 줄지만 NN 64번(평가 "
            + ch.comma(nn[-1][0]) + "번)도 후회 삽입 한 번(" + ch.comma(point("regret1")[1]) + ", 평가 " + ch.comma(point("regret1")[0])
            + "번)보다 깁니다. 후회 삽입에 25% 흔들기를 5번 하면 " + ch.comma(point("regretShake5")[1]) + "입니다.")
    out["restart-budget.svg"] = ch.line_chart(
        "평가를 더 쓰면 얼마나 짧아지나", f"순서 틀, 시드 {seeds}개의 중앙값. 가로는 구성에 쓴 평가 횟수(로그 눈금)입니다",
        desc, series,
        xticks=[(10_000, "10,000"), (100_000, "100,000"), (1_000_000, "1,000,000"), (10_000_000, "10,000,000")],
        yticks=[(v, ch.comma(v)) for v in range(13_500, 16_501, 500)],
        xlog=True, ylog=False, xlabel="평가 횟수 (로그 눈금)", ylabel="경로 길이 중앙값 ↓ (작을수록 좋음)", height=300)
    return out
