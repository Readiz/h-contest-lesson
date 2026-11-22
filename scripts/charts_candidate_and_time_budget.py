"""candidate-and-time-budget 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch

KS = [0, 2, 4, 8, 16, 32]
KLABELS = ["없이", "2", "4", "8", "16", "32"]


def pct(permille: int) -> str:
    return f"{permille / 10:.1f}%"


def k_chart(m: dict, tight: str, ample: str, n: int, tight_budget: int, ample_budget: int, ylo: int, yhi: int, ystep: int, height: int) -> str:
    a = {e["k"]: e["median"] for e in m["lists"][tight]}
    b = {e["k"]: e["median"] for e in m["lists"][ample]}
    series = [
        {"name": f"예산 {ch.comma(tight_budget)} (빠듯)", "color": "hi", "points": [(i, a[k]) for i, k in enumerate(KS)], "labels": "none", "label_idx": [0, 2, 5], "pos": "up"},
        {"name": f"예산 {ch.comma(ample_budget)} (넉넉)", "color": "base", "points": [(i, b[k]) for i, k in enumerate(KS)], "labels": "none", "label_idx": [0, 3, 5], "pos": "down"},
    ]
    best_a = min(KS[1:], key=lambda k: a[k])
    best_b = min(KS[1:], key=lambda k: b[k])
    desc = (f"순서 틀 N = {ch.comma(n)}에서 후보 수 k를 바꿀 때 시드 20개 중앙값 비용입니다. 예산 {ch.comma(tight_budget)}(빠듯)에서는 "
            + ", ".join(ch.comma(a[k]) for k in KS) + f"로 k = {best_a}에서 가장 낮고 k가 커지면 다시 올라갑니다. 예산 {ch.comma(ample_budget)}(넉넉)에서는 "
            + ", ".join(ch.comma(b[k]) for k in KS) + f"로 k = {best_b}에서 가장 낮습니다. 후보 없이 무작위로 고르면 두 예산 모두 가장 높은 쪽입니다.")
    return ch.line_chart(
        f"후보 수에 따른 비용 (N = {ch.comma(n)})", "순서 틀, 시드 20개의 중앙값. 예산이 빠듯하면 작은 k가, 넉넉하면 큰 k가 낫습니다",
        desc, series,
        xticks=[(i, lab) for i, lab in enumerate(KLABELS)],
        yticks=[(v, ch.comma(v)) for v in range(ylo, yhi + 1, ystep)],
        xlog=False, ylog=False, xlabel="후보 수 k (없이 = 후보 목록 없이 무작위)", ylabel="최종 비용 중앙값 ↓ (작을수록 좋음)", height=height)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}

    out["k-vs-cost-2000.svg"] = k_chart(m, "route2000@400000", "route2000@2000000", 2000, 400_000, 2_000_000, 40_000, 70_000, 10_000, 280)
    out["k-vs-cost-10000.svg"] = k_chart(m, "route10000@3000000", "route10000@12000000", 10_000, 3_000_000, 12_000_000, 90_000, 150_000, 15_000, 280)

    # 놓치는 이동: 시작 상태에서 후보 안 최선 개선량의 비율
    start = {fr: {e["k"]: e["permille"] for e in m["miss"][fr][0]["perK"]} for fr in ("route", "assign")}
    ks = [2, 4, 8, 16, 32]
    groups = [{"label": f"후보 {k}개", "values": [start["route"][k] / 10, start["assign"][k] / 10],
               "texts": [pct(start["route"][k]), pct(start["assign"][k])]} for k in ks]
    desc = ("시작 상태에서 전체 근방의 최선 개선량 가운데 후보 안에서 얻는 몫입니다. 순서 틀은 후보 2, 4, 8, 16, 32개에서 "
            + ", ".join(pct(start["route"][k]) for k in ks) + "이고, 배정 틀은 " + ", ".join(pct(start["assign"][k]) for k in ks)
            + "입니다. 배정 틀의 싼 후보 목록은 후보 수가 같아도 최선 이동을 더 자주 놓칩니다.")
    out["miss-share.svg"] = ch.grouped_hbar(
        "후보 안에 든 개선량의 비율", "시작 상태, 전체 근방의 최선 개선량 중 후보 안에서 얻는 몫(시드 합)입니다. 100%면 놓치는 개선이 없습니다",
        desc, groups, [("순서 틀", "base"), ("배정 틀", "hi")], "후보 안의 최선 개선량 / 전체 근방의 최선 개선량 (%)")

    # 시계를 읽는 간격
    rt = {e["every"]: e for e in m["clock"]["route"]}
    asg = {e["every"]: e for e in m["clock"]["assign"]}
    evs = [e["every"] for e in m["clock"]["route"]]
    groups = [{"label": f"{ch.comma(v)}번마다", "values": [rt[v]["share"] / 10, asg[v]["share"] / 10],
               "texts": [pct(rt[v]["share"]), pct(asg[v]["share"])]} for v in evs]
    desc = ("시계를 한 번 읽는 비용을 연산 40으로 가정했을 때 예산 2,000,000 중 시계 읽기가 차지하는 비율입니다. 읽는 간격이 "
            + ", ".join(ch.comma(v) for v in evs) + "일 때 순서 틀은 " + ", ".join(pct(rt[v]["share"]) for v in evs)
            + ", 배정 틀은 " + ", ".join(pct(asg[v]["share"]) for v in evs) + "입니다. 매 제안 읽으면 예산의 절반 가까이를 시계가 씁니다.")
    out["clock-share.svg"] = ch.grouped_hbar(
        "시계 읽기가 예산에서 차지하는 비율", "읽기 비용 40을 연산으로 센 모형, 예산 2,000,000. 제안 몇 번마다 읽는지에 따른 비율입니다",
        desc, groups, [("순서 틀", "base"), ("배정 틀", "hi")], "예산 중 시계 읽기에 쓴 비율 (%) ↓ (작을수록 좋음)")
    return out
