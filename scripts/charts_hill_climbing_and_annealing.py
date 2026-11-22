"""hill-climbing-and-annealing 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch


def pct(v: float) -> str:
    return f"{v:.1f}%"


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["seeds"])

    # 1. 같은 평가 횟수에서: 언덕 오르기 한 번 / 재시작 / 담금질
    rows_ = m["methods"]["main"]["route"]
    xs = [e["budget"] for e in rows_]
    series = [
        {"name": "언덕 오르기 한 번", "color": "light", "points": [(e["budget"], e["first"]) for e in rows_], "labels": "last", "pos": "up"},
        {"name": "재시작", "color": "hi", "points": [(e["budget"], e["restarts"]) for e in rows_], "labels": "last", "pos": "up"},
        {"name": "담금질", "color": "base", "points": [(e["budget"], e["anneal"]) for e in rows_], "labels": "last", "pos": "down"},
    ]
    last = rows_[-1]
    desc = ("순서 틀에서 평가 횟수(로그 눈금)를 늘릴 때 시드 20개 중앙값 비용입니다. 언덕 오르기 한 번은 모든 예산에서 14,500 근처에서 멈추고, 재시작은 "
            + ", ".join(ch.comma(e["restarts"]) for e in rows_) + "로 천천히 줄며, 담금질은 " + ", ".join(ch.comma(e["anneal"]) for e in rows_)
            + "로 가장 많이 줄어 평가 " + ch.comma(last["budget"]) + "번에서 " + ch.comma(last["anneal"]) + "입니다.")
    out["budget-curve.svg"] = ch.line_chart(
        "평가 횟수를 늘릴 때의 비용", f"순서 틀(점 200개), 시드 {seeds}개의 중앙값. 평가 횟수가 같을 때 세 방법을 비교합니다",
        desc, series,
        xticks=[(x, ch.comma(x)) for x in xs],
        yticks=[(v, ch.comma(v)) for v in range(13_000, 15_001, 500)],
        xlog=True, ylog=False, xlabel="평가 횟수 (로그 눈금)", ylabel="최종 비용 중앙값 ↓ (작을수록 좋음)", height=280)

    # 2. 끝 온도를 바꾸면
    sw = m["sweeps"]["route"]
    ordered = sw["t1"]
    assert [r["tag"] for r in ordered] == ["t1x6", "t1x25", "exp", "t1x400", "t1x1600"]
    labels = ["6%", "25%", "100%", "400%", "1600%"]
    rows = [{"label": lab, "value": r["median"], "color": "hi" if r["tag"] == "exp" else "base"} for lab, r in zip(labels, ordered)]
    desc = ("순서 틀에서 끝 온도를 기본값의 6%, 25%, 100%, 400%, 1600%로 바꿨을 때 시드 20개 중앙값 비용입니다. "
            + ", ".join(ch.comma(r["median"]) for r in ordered) + "이며 기본값(100%)이 가장 낮고 1600%에서는 끝 온도가 너무 높아 크게 나빠집니다.")
    out["end-temperature.svg"] = ch.bar_chart(
        "끝 온도를 바꾸면", f"순서 틀, 시작 온도와 예산({ch.comma(sw['budget'])}번)은 그대로, 시드 {seeds}개의 중앙값입니다. 기본값을 강조했습니다",
        desc, rows, "끝 온도 (기본값 대비), 막대 높이는 최종 비용 ↓", orient="v")

    # 3. 구간별 나쁜 이동 수락률
    tr = m["trace"]

    def rate(frame: str) -> list[tuple[float, float]]:
        return [(i + 1, 100.0 * t / u) for i, (u, t) in enumerate(zip(tr[frame]["up"], tr[frame]["taken"]))]

    series = [
        {"name": "순서 틀", "color": "base", "points": rate("route"), "labels": "none", "label_idx": [0, 3], "pos": "up", "fmt": pct},
        {"name": "배정 틀", "color": "hi", "points": rate("assign"), "labels": "none", "label_idx": [0, 3], "pos": "up", "fmt": pct},
    ]
    r0, r3 = rate("route"), rate("assign")
    desc = ("예산을 10등분한 구간마다 나쁜 이동을 제안했을 때 받은 비율입니다. 순서 틀은 첫 구간 " + pct(r0[0][1]) + "에서 마지막 구간 " + pct(r0[-1][1])
            + "로, 배정 틀은 " + pct(r3[0][1]) + "에서 " + pct(r3[-1][1]) + "로 온도가 내려가며 단조롭게 줄어듭니다.")
    out["acceptance-rate.svg"] = ch.line_chart(
        "구간별로 받은 나쁜 이동의 비율", "예산을 10등분해 구간마다 (받은 수 / 제안한 수)를 셌습니다. 온도가 내려가며 줄어야 합니다",
        desc, series,
        xticks=[(i, str(i)) for i in range(1, 11)],
        yticks=[(v, f"{v}%") for v in (0, 2, 4, 6, 8, 10)],
        xlog=False, ylog=False, xlabel="예산의 구간 (1 = 처음, 10 = 끝)", ylabel="나쁜 이동을 받은 비율", height=260)
    return out
