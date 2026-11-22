"""experiments-and-tuning 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json).

표의 값은 시드 20개의 최고 비용 중 10번째로 작은 값이다. curve 행의 hot·c0·c1 = [아래 사분위, 중앙값, 위 사분위]이고
hot = 거의 0도, c0 = 일정 온도, c1 = 고른 설정이다.
"""
from __future__ import annotations

import charts as ch

MED = "10번째로 작은 값"


def verdict(better: int, worse: int) -> str:
    """강의의 판정 규칙: 20개 중 15개 이상이면 차이가 있다고 본다."""
    if better >= 15:
        return "더 좋음"
    if worse >= 15:
        return "더 나쁨"
    return "결정 못 함"


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    rows = m["curve"]["rows"]
    target = m["curve"]["failTarget"]
    n = 20

    # 1. 예산을 늘릴 때의 곡선
    def pts(key: str) -> list[tuple[float, float]]:
        return [(r["budget"], r[key][1]) for r in rows]

    series = [
        {"name": "거의 0도", "color": "light", "points": pts("hot"), "labels": "none", "label_idx": [2, 3], "pos": "up"},
        {"name": "일정 온도", "color": "base", "points": pts("c0"), "labels": "none", "label_idx": [3], "pos": "up"},
        {"name": "고른 설정", "color": "hi", "points": pts("c1"), "labels": "none", "label_idx": [2, 3], "pos": "down"},
    ]
    last = rows[-1]
    desc = ("순서 틀에서 평가 횟수(로그 눈금) " + ", ".join(ch.comma(r["budget"]) for r in rows) + f"번일 때 시드 {n}개의 최고 비용 중앙값입니다. 거의 0도는 "
            + ", ".join(ch.comma(r["hot"][1]) for r in rows) + "로 300,000번 뒤 멈추고, 일정 온도는 "
            + ", ".join(ch.comma(r["c0"][1]) for r in rows) + ", 고른 설정은 "
            + ", ".join(ch.comma(r["c1"][1]) for r in rows) + f"로 예산이 늘수록 계속 내려가 {ch.comma(last['budget'])}번에서 가장 낮습니다.")
    out["budget-curve.svg"] = ch.line_chart(
        "예산을 늘릴 때의 최고 비용", f"순서 틀, 시드 {n}개 중 {MED}(중앙값). 한 예산의 순위가 곡선 전체의 순위가 아닙니다",
        desc, series,
        xticks=[(r["budget"], ch.comma(r["budget"])) for r in rows],
        yticks=[(v, ch.comma(v)) for v in range(12_500, 18_501, 1_500)],
        xlog=True, ylog=False, xlabel="평가 횟수 (로그 눈금)", ylabel="최고 비용 중앙값 ↓ (작을수록 좋음)", height=280)

    # 2. 중앙값은 같아 보여도 꼬리는 다르다: 목표 미달 시드 수
    groups = [{"label": f"평가 {ch.comma(r['budget'])}번", "values": list(r["fail"]), "texts": [f"{v} / {n}" for v in r["fail"]]} for r in rows]
    desc = (f"순서 틀에서 최고 비용이 {ch.comma(target)} 이하 목표에 닿지 못한 시드의 수입니다(시드 {n}개 중). 거의 0도, 일정 온도, 고른 설정 순으로 "
            + ", ".join(f"평가 {ch.comma(r['budget'])}번에서 {r['fail'][0]}, {r['fail'][1]}, {r['fail'][2]}개" for r in rows)
            + "입니다. 300,000번에서 중앙값은 모두 14,000 근처인데 미달 시드는 15, 8, 4개로 갈립니다.")
    out["tail-miss.svg"] = ch.grouped_hbar(
        "목표에 못 닿은 시드 수", f"순서 틀, 최고 비용 {ch.comma(target)} 이하를 목표로 했을 때 못 닿은 시드 수(시드 {n}개 중)입니다",
        desc, groups, [("거의 0도", "light"), ("일정 온도", "base"), ("고른 설정", "hi")], f"목표 미달 시드 수 ↓ (작을수록 좋음, 최대 {n})")

    # 3. 짝지은 비교와 짝짓지 않은 비교
    pr = m["pairing"]
    wl = []
    wl.append(("순서: 짝지음", pr["paired"][0], pr["paired"][1]))
    for s in pr["shifts"]:
        wl.append((f"순서: 시드 {s['offset'] + 1}~{s['offset'] + 20}", s["cmp"][0], s["cmp"][1]))
    wl.append(("배정: 짝지음", pr["assign"]["paired"][0], pr["assign"]["paired"][1]))
    for s in pr["assign"]["shifts"]:
        wl.append((f"배정: {s['k']}칸 밀기", s["cmp"][0], s["cmp"][1]))
    wrows = [{"label": lab, "better": b, "worse": w, "text": f"{b} / {w} {verdict(b, w)}"} for lab, b, w in wl]
    desc = ("같은 입력끼리 짝지어 비교하면 순서 틀은 " + f"{pr['paired'][0]} 대 {pr['paired'][1]}로 차이가 잡히지만 입력을 어긋나게 하면 "
            + ", ".join(f"{b} 대 {w}" for _, b, w in wl[1:5]) + "로 결정 못 함입니다. 배정 틀은 짝지으면 "
            + f"{pr['assign']['paired'][0]} 대 {pr['assign']['paired'][1]}로 고른 설정이 모두 못하는데 입력을 밀면 "
            + ", ".join(f"{b} 대 {w}" for _, b, w in wl[6:]) + "로 결정 못 함으로 사라집니다.")
    out["pairing-wins.svg"] = ch.winloss_chart(
        "짝짓지 않으면 차이가 사라진다", f"고른 설정이 나은 시드와 못한 시드의 수(시드 {n}개). 순서 틀은 일정 온도와, 배정 틀은 거의 0도와 비교했습니다",
        desc, wrows, n, f"시드 {n}개 중 고른 설정이 나은 / 못한 시드 수 (15개 이상이면 차이 있음)",
        names=("고른 설정이 나은 시드", None, "고른 설정이 못한 시드"))

    # 4. 다른 입력에서의 일반화: 고른 설정 대 일정 온도
    short = {"확인 시드 21~40 (같은 입력 가족)": "확인 시드 21~40", "점 100개": "점 100개", "점 400개": "점 400개", "점이 8개 뭉치에 모인 분포": "8개 뭉치 분포",
             "배정 틀 (예산 100,000)": "배정 틀", "예산 100,000": "예산 100,000", "예산 1,000,000": "예산 1,000,000"}
    tr = m["transfer"]
    trows = []
    for e in tr:
        b, w = e["c1VsC0"][0], e["c1VsC0"][1]
        trows.append({"label": short[e["case"]], "better": b, "worse": w, "text": f"{b} / {w} {verdict(b, w)}"})
    desc = ("고른 설정을 일정 온도와 같은 시드끼리 비교한 결과입니다. " + ", ".join(f"{r['label']} {r['better']} 대 {r['worse']}" for r in trows)
            + "입니다. 점 400개, 뭉친 분포, 배정 틀, 두 예산에서는 고른 설정이 낫고 확인 시드와 점 100개에서는 결정 못 함입니다.")
    out["transfer-wins.svg"] = ch.winloss_chart(
        "고른 설정은 어디서 이기나", f"일정 온도와 같은 시드끼리 비교(시드 {n}개). 확인 시드 외의 행은 시드 1~20에서 입력 가족이나 예산을 바꾼 것입니다",
        desc, trows, n, f"시드 {n}개 중 고른 설정이 나은 / 못한 시드 수 (15개 이상이면 차이 있음)",
        names=("고른 설정이 나은 시드", None, "고른 설정이 못한 시드"))
    return out
