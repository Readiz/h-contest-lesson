"""destroy-and-repair 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["seeds"])

    # 1. 같은 예산에서 세 방식 (순서 틀)
    b = m["budget"]["route"]
    series = [
        {"name": "작은 이동만", "color": "light", "points": [(e["budget"], e["small"]) for e in b], "labels": "all", "pos": "up"},
        {"name": "부수고 다시 짓기만", "color": "hi", "points": [(e["budget"], e["dr"]) for e in b], "labels": "all", "pos": "up"},
        {"name": "혼합 (작은 이동 1/4 + 부수고 다시 짓기)", "color": "base", "points": [(e["budget"], e["hybrid"]) for e in b], "labels": "all", "pos": "down"},
    ]
    last = b[-1]
    desc = (f"순서 틀에서 연산 예산 {', '.join(ch.comma(e['budget']) for e in b)}일 때 시드 {seeds}개 중 10번째로 작은 최종 비용입니다. 작은 이동만은 "
            + ", ".join(ch.comma(e["small"]) for e in b) + "로 거의 내려가지 않고, 부수고 다시 짓기만은 " + ", ".join(ch.comma(e["dr"]) for e in b)
            + "로 모든 예산에서 가장 높으며, 혼합은 " + ", ".join(ch.comma(e["hybrid"]) for e in b) + "로 예산 " + ch.comma(last["budget"])
            + "에서 가장 낮습니다.")
    out["budget-route.svg"] = ch.line_chart(
        "같은 예산에서 세 방식의 비용 (순서 틀)", f"N=200, 시드 {seeds}개 중 10번째로 작은 비용. 작을수록 좋습니다. 부수고 다시 짓기만은 시작 해에서 곧바로 시작합니다",
        desc, series, xticks=[(e["budget"], ch.comma(e["budget"])) for e in b],
        yticks=[(v, ch.comma(v)) for v in (12_000, 14_000, 16_000, 18_000, 20_000)], xlog=False, ylog=False,
        xlabel="연산 예산", ylabel="최종 비용 ↓ (작을수록 좋음)", height=260)

    # 2. 부수는 크기 (순서 틀)
    sz = m["size"]["route"]
    rows = sz["rows"]
    best = min(rows, key=lambda e: e["median"])
    series = [{"name": "혼합 (가까운 점 부수기)", "color": "base", "points": [(e["size"], e["median"]) for e in rows], "labels": "none",
               "label_idx": [rows.index(best), len(rows) - 1], "pos": "down"},
              {"name": f"작은 이동만 {ch.comma(sz['small'])} (같은 예산)", "color": "hi", "points": [(rows[0]["size"], sz["small"]), (rows[-1]["size"], sz["small"])],
               "labels": "none", "pos": "up", "dash": "8 6"}]
    desc = (f"순서 틀에서 떼어 내는 점 수(로그 눈금)를 바꿨을 때 시드 {seeds}개 중 10번째로 작은 비용입니다. 점 1개에서 " + ch.comma(rows[0]["median"])
            + "이고 점 " + str(best["size"]) + "개에서 가장 낮은 " + ch.comma(best["median"]) + "이며, 200개(전체)에서는 " + ch.comma(rows[-1]["median"])
            + "로 다시 나빠집니다. 점선은 같은 예산의 작은 이동만(" + ch.comma(sz["small"]) + ")입니다. 점 2개에서 40개까지의 중앙값이 점선 아래입니다.")
    out["size-route.svg"] = ch.line_chart(
        "떼어 내는 크기별 비용 (순서 틀)", f"예산 4,000,000, 시드 {seeds}개 중 10번째로 작은 비용. 작을수록 좋습니다. 가운데 크기가 이깁니다",
        desc, series, xticks=[(e["size"], str(e["size"])) for e in rows if e["size"] in (1, 3, 8, 21, 80, 200)],
        yticks=[(v, ch.comma(v)) for v in (13_500, 14_000, 14_500)], xlog=True, ylog=False,
        xlabel="떼어 내는 점 수 (로그 눈금, 200 = 해 전체)", ylabel="최종 비용 ↓ (작을수록 좋음)",
        height=260)

    # 3. 부수는 크기 (배정 틀)
    sa = m["size"]["assign"]
    rows = sa["rows"]
    best = min(rows, key=lambda e: e["median"])
    series = [{"name": "혼합 (무작위 작업, 후회 기준)", "color": "base", "points": [(e["size"], e["median"]) for e in rows], "labels": "none",
               "label_idx": [rows.index(best)], "pos": "down"},
              {"name": f"작은 이동만 {ch.comma(sa['small'])} (같은 예산)", "color": "hi", "points": [(rows[0]["size"], sa["small"]), (rows[-1]["size"], sa["small"])],
               "labels": "none", "pos": "up", "dash": "8 6"}]
    desc = (f"배정 틀에서 떼어 내는 작업 수(로그 눈금)를 바꿨을 때 시드 {seeds}개 중 10번째로 작은 비용입니다. 작업 {best['size']}개에서 가장 낮은 "
            + ch.comma(best["median"]) + "이고 나머지 크기에서는 작은 이동만과 같은 " + ch.comma(sa["small"]) + " 근처입니다. 점선은 작은 이동만입니다. "
            + "점선보다 낮은 것은 작업 8개와 16개뿐이고 이득은 작습니다.")
    out["size-assign.svg"] = ch.line_chart(
        "떼어 내는 크기별 비용 (배정 틀)", f"예산 2,000,000, 시드 {seeds}개 중 10번째로 작은 비용. 작을수록 좋습니다. 이득이 작은 입력입니다",
        desc, series, xticks=[(e["size"], str(e["size"])) for e in rows if e["size"] in (1, 2, 4, 8, 16, 32, 64, 120)],
        yticks=[(v, ch.comma(v)) for v in (43_950, 43_960, 43_970, 43_980, 43_990, 44_000)], xlog=True, ylog=False,
        xlabel="떼어 내는 작업 수 (로그 눈금, 120 = 해 전체)", ylabel="최종 비용 ↓ (작을수록 좋음)",
        height=260)

    # 4. 지역 최적에서 개선을 찾은 횟수 (순서 틀)
    st = m["stuck"]["route"]
    sizes = sorted({e["size"] for e in st})
    names = [(0, "무작위", "mute"), (3, "비용 기여", "light"), (2, "가까운 점", "hi"), (1, "연속 구간", "base")]
    series = []
    for kind, name, col in names:
        pts = [(e["size"], e["median"]) for e in sorted(st, key=lambda e: e["size"]) if e["kind"] == kind and e["size"] >= 2]
        series.append({"name": name, "color": col, "points": pts, "labels": "none",
                       "label_idx": [] if kind in (0, 3) else ( [pts.index(max(pts, key=lambda p: p[1]))]), "pos": "up"})
    top = {name: max(e["median"] for e in st if e["kind"] == kind) for kind, name, _ in names}
    desc = (f"순서 틀의 지역 최적(시드 {seeds}개 모두 개선하는 작은 이동이 없음)에서 부수고 다시 짓기를 300번 시도해 새 해가 더 좋았던 횟수의 중앙값입니다. "
            "떼어 내는 점 수(로그 눈금)가 늘 때, 연속 구간은 8개에서 " + str(top["연속 구간"]) + "번까지 늘었다가 줄고, 가까운 점은 13개 이상에서 "
            + str(top["가까운 점"]) + "번에 이르며, 무작위와 비용 기여는 21개에서야 각각 " + str(top["무작위"]) + "번과 " + str(top["비용 기여"]) + "번입니다.")
    out["stuck-found.svg"] = ch.line_chart(
        "지역 최적에서 개선을 찾은 횟수 (순서 틀)", "시작 해의 지역 최적에서 300번 시도했을 때 새 해가 더 좋았던 횟수의 중앙값입니다. 클수록 잘 빠져나옵니다",
        desc, series, xticks=[(s, str(s)) for s in sizes if s in (2, 3, 5, 8, 13, 21)],
        yticks=[(v, str(v)) for v in (0, 20, 40, 60)], xlog=True, ylog=False,
        xlabel="떼어 내는 점 수 (로그 눈금)", ylabel="300번 중 개선한 횟수 (중앙값) ↑", height=260)
    return out
