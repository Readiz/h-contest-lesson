"""problem-modeling 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch


def gaps(opt: list[int], other: list[int]) -> list[float]:
    """|other - opt| / opt 의 백분율(본문 표의 정의)."""
    return [abs(o - p) * 100.0 / p for p, o in zip(opt, other)]


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["seeds"])

    # 1. 기본 크기에서 기준선과 한계의 비
    d = m["default"]
    names = [("route", "순서: 기준선 ÷ 하한"), ("assign", "배정: 기준선 ÷ 하한"), ("grid", "격자 수집: 상한 ÷ 기준선")]
    rows = [{"label": lab, "values": [v / 1000.0 for v in d[k]["ratio1000"]], "color": "hi" if k == "grid" else "base"} for k, lab in names]
    lo_hi = {k: (min(d[k]["ratio1000"]) / 1000.0, max(d[k]["ratio1000"]) / 1000.0) for k, _ in names}
    desc = (f"기본 크기에서 시드 {seeds}개마다 기준선과 한계의 비입니다. " + " ".join(
        f"{lab}는 {lo_hi[k][0]:.2f}배에서 {lo_hi[k][1]:.2f}배까지였고" for k, lab in names)
        + " 순서와 배정은 시드마다 비슷하고 격자 수집은 시드마다 크게 흔들립니다.")
    out["baseline-ratio.svg"] = ch.strip_chart(
        "기준선과 한계의 비 (기본 크기)", f"시드 {seeds}개. 점은 시드 하나, 눈금은 중앙값(가운데 두 값의 평균)입니다. 최적은 모르므로 이 비는 여지의 최대치입니다",
        desc, rows, "한계와 기준선의 비 (배)", tick_digits=0)

    # 2. 작은 입력에서 한계와 최적의 간격
    t = m["tiny"]
    kinds = [("route7", "순서 N=7"), ("assign633", "배정 N=6, M=3, K=3"), ("grid446", "격자 4×4, T=6"), ("grid2020x5", "격자 20×20, T=5")]
    bound_gap = {k: gaps(t[k]["opt"], t[k]["bound"]) for k, _ in kinds}
    rows = [{"label": lab, "values": bound_gap[k], "color": "hi" if k.startswith("grid") else "base"} for k, lab in kinds]
    desc = (f"작은 입력에서 시드 {seeds}개마다 한계가 전수 탐색한 최적과 몇 퍼센트 다른지 점으로 찍은 그림입니다. " + " ".join(
        f"{lab}는 {min(bound_gap[k]):.1f}%에서 {max(bound_gap[k]):.1f}%이고" for k, lab in kinds)
        + " 순서의 하한은 최적에 가깝고 격자 수집의 상한은 20×20에서 크게 느슨합니다.")
    out["bound-gap-tiny.svg"] = ch.strip_chart(
        "한계는 최적에서 얼마나 떨어져 있나", f"작은 입력 4종, 시드 {seeds}개. 점은 시드 하나, 눈금은 중앙값입니다. 0%이면 한계가 최적과 같습니다",
        desc, rows, "한계와 최적의 간격 (%) ↓ (작을수록 한계가 정확함)", tick_digits=0)

    # 3. 같은 입력에서 기준선과 최적의 간격
    base_gap = {k: gaps(t[k]["opt"], t[k]["baseline"]) for k, _ in kinds}
    rows = [{"label": lab, "values": base_gap[k], "color": "hi" if k.startswith("grid") else "base"} for k, lab in kinds]
    desc = (f"같은 작은 입력에서 시드 {seeds}개마다 기준선이 최적과 몇 퍼센트 다른지 점으로 찍은 그림입니다. " + " ".join(
        f"{lab}는 {min(base_gap[k]):.1f}%에서 {max(base_gap[k]):.1f}%이고" for k, lab in kinds)
        + " 기준선은 대부분의 시드에서 최적과 멀어 개선할 여지가 큽니다.")
    out["baseline-gap-tiny.svg"] = ch.strip_chart(
        "기준선은 최적에서 얼마나 떨어져 있나", f"작은 입력 4종, 시드 {seeds}개. 점은 시드 하나, 눈금은 중앙값입니다. 한계의 간격(앞 그림)보다 대체로 훨씬 큽니다",
        desc, rows, "기준선과 최적의 간격 (%)", tick_digits=0)
    return out
