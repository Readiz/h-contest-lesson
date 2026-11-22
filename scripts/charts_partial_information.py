"""partial-information 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json).

표의 값은 시드 20개의 점수 중 10번째로 작은 값이다(measurements.json의 median이 이미 그 값이다).
"""
from __future__ import annotations

import charts as ch

MED = "10번째로 작은 값"


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    g = m["grid"]

    # 1. 모르는 칸을 얼마로 칠할까
    short = {0: "비관 (칸 = 0)", 100: "칸 = 1", -1: "평균 (기준)", 300: "칸 = 3", 500: "칸 = 5", 900: "낙관 (칸 = 9)"}
    plain = {0: "비관(0)", 100: "1", -1: "평균", 300: "3", 500: "5", 900: "낙관(9)"}
    est = g["estimate"]
    base = next(e for e in est if e["est"] == -1)
    rows = [{"label": short[e["est"]], "value": e["median"], "color": "hi" if e["est"] == -1 else "base",
             "text": f"{e['median']} (아는 칸 {e['known']})"} for e in est]
    desc = ("격자 수집에서 모르는 칸의 값을 얼마로 칠하느냐에 따른 점수(" + MED + ")입니다. "
            + ", ".join(f"{plain[e['est']]} {e['median']}" for e in est)
            + f"이고 평균 추정이 {base['median']}로 가장 높습니다. 끝난 뒤 아는 칸은 비관 {est[0]['known']}칸에서 낙관 {est[-1]['known']}칸으로 늘지만 점수는 오르지 않습니다.")
    out["estimate-score.svg"] = ch.bar_chart(
        "모르는 칸을 얼마로 칠하나", f"격자 수집, 보이는 거리 2, 시드 {len(m['seeds'])}개 점수의 {MED}. 칸 = 모르는 칸의 값, 괄호는 끝난 뒤 아는 칸의 수입니다",
        desc, rows, "점수 ↑ (클수록 좋음)", orient="h")

    # 2. 보이는 거리
    rad = g["radius"]
    labels = [("전체" if e["rad"] == 99 else str(e["rad"])) for e in rad]
    series = [{"name": "점수", "color": "base", "points": [(i, e["median"]) for i, e in enumerate(rad)], "labels": "all", "pos": "up"}]
    desc = ("보이는 거리를 0, 1, 2, 3, 4, 5, 전체로 늘릴 때 점수(" + MED + ")입니다. "
            + ", ".join(f"{lab} {e['median']}" for lab, e in zip(labels, rad))
            + "으로 거리 0에서 1, 2로 갈 때 크게 오르고 그 뒤는 완만합니다.")
    out["radius-score.svg"] = ch.line_chart(
        "보이는 거리와 점수", f"격자 수집, 모르는 칸 = 평균, 시드 {len(m['seeds'])}개 점수의 {MED}. 전체는 처음부터 모든 칸이 보이는 경우입니다",
        desc, series,
        xticks=[(i, lab) for i, lab in enumerate(labels)],
        yticks=[(v, str(v)) for v in range(100, 301, 50)],
        xlog=False, ylog=False, xlabel="보이는 거리 (맨해튼)", ylabel="점수 ↑ (클수록 좋음)", height=250)

    # 3. 재계획 주기
    per = g["period"]
    rows = [{"label": f"{e['period']}걸음마다", "value": e["median"], "color": "hi" if e["period"] == 1 else "base",
             "text": f"{e['median']} ({ch.comma(e['evals'])}번 평가)"} for e in per]
    desc = ("재계획 주기를 " + ", ".join(str(e["period"]) for e in per) + "걸음으로 늘릴 때 점수(" + MED + ")입니다. "
            + ", ".join(str(e["median"]) for e in per) + f"로 걸음마다 다시 계획하는 기준이 가장 높고, 주기 {per[-1]['period']}에서는 {per[-1]['median']}까지 내려갑니다. 평가 횟수는 "
            + ch.comma(per[0]["evals"]) + "에서 " + ch.comma(per[-1]["evals"]) + "으로 줄어듭니다.")
    out["period-score.svg"] = ch.bar_chart(
        "재계획 주기를 늘리면", f"격자 수집, 시드 {len(m['seeds'])}개 점수의 {MED}. 괄호는 한 판에서 평가한 후보 수입니다. 기준(1걸음마다)을 강조했습니다",
        desc, rows, "점수 ↑ (클수록 좋음)", orient="h")

    # 4. 온라인 배정: 하한을 넘는 비용
    names = [("-2", "탐욕: 앞일 안 봄"), ("0", "앞 작업 길이 0"), ("1", "앞 작업 길이 1"), ("-1", "평균 (기준)"), ("100", "앞 작업 길이 100")]
    other_names = {"라운드 로빈(아무것도 보지 않음)": "라운드 로빈", "전체 정보: 총 길이를 알고 도착 순서대로": "전체: 도착 순서",
                   "전체 정보: 총 길이를 알고 긴 작업부터": "전체: 긴 작업부터"}

    def excess(key: str) -> dict[str, int]:
        o = m["online"][key]
        bound = next(e["median"] for e in o["others"] if e["name"] == "하한")
        vals = {str(e["fut"]): e["median"] - bound for e in o["policies"]}
        for e in o["others"]:
            if e["name"] in other_names:
                vals[other_names[e["name"]]] = e["median"] - bound
        return vals

    wide, narrow = excess("100"), excess("20")
    order = [(k, lab) for k, lab in names] + [(v, v) for v in other_names.values()]
    groups = [{"label": lab, "values": [wide[k], narrow[k]], "texts": [ch.comma(wide[k]), ch.comma(narrow[k])]} for k, lab in order]
    desc = ("온라인 배정에서 비용 중앙값이 하한을 얼마나 넘는지입니다. 작업 길이 1에서 100일 때 평균 추정은 "
            + ch.comma(wide["-1"]) + "로 탐욕 " + ch.comma(wide["-2"]) + "보다 작고, 작업 길이 1에서 20으로 바꾼 입력에서는 평균 추정 "
            + ch.comma(narrow["-1"]) + "보다 탐욕 " + ch.comma(narrow["-2"]) + "이 작아 순위가 뒤집힙니다. 라운드 로빈은 두 입력에서 각각 "
            + ch.comma(wide["라운드 로빈"]) + "과 " + ch.comma(narrow["라운드 로빈"]) + "로 가장 큽니다.")
    out["online-excess.svg"] = ch.grouped_hbar(
        "하한을 넘는 비용", "온라인 배정, 시드 20개의 비용 중앙값에서 하한의 중앙값을 뺀 값입니다. 작을수록 좋고 하한은 달성할 수 없는 값입니다",
        desc, groups, [("작업 길이 1..100", "base"), ("작업 길이 1..20", "hi")], "하한을 넘는 비용 ↓ (작을수록 좋음)")
    return out
