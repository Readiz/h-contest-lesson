"""neighborhood-and-delta 강의의 실험 차트 설정. generate_charts.py가 charts(m)을 부른다(m = 이 강의의 measurements.json)."""
from __future__ import annotations

import charts as ch


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    seeds = len(m["seeds"])

    # 1. 같은 예산에서의 비용: 전체 재계산 대 차분
    b = m["budget"]["route"]
    full = [(e["budget"], e["full"]) for e in b]
    delta = [(e["budget"], e["delta"]) for e in b]
    desc = ("순서 틀에서 같은 연산 예산(로그 눈금)으로 얻은 비용의 비교입니다. 전체 재계산은 예산 " + ", ".join(ch.comma(x) for x, _ in full)
            + "에서 " + ", ".join(ch.comma(y) for _, y in full) + "이고 차분은 " + ", ".join(ch.comma(y) for _, y in delta)
            + "입니다. 차분이 예산 " + ch.comma(delta[1][0]) + "에서 낸 비용(" + ch.comma(delta[1][1]) + ")을 전체 재계산은 예산 "
            + ch.comma(full[-1][0]) + "에서도 내지 못합니다(" + ch.comma(full[-1][1]) + ").")
    series = [
        {"name": "전체 재계산 (적용 후 복구)", "color": "hi", "points": full, "labels": "all", "pos": "up"},
        {"name": "차분 (계산만)", "color": "base", "points": delta, "labels": "all", "pos": "down"},
    ]
    out["budget-curve.svg"] = ch.line_chart(
        "같은 예산에서 얻은 비용", f"순서 틀(점 200개), 구간 뒤집기, 시드 {seeds}개. 둘 다 좋아질 때만 받는 탐색입니다",
        desc, series,
        xticks=[(x, ch.comma(x)) for x, _ in full],
        yticks=[(v, ch.comma(v)) for v in (10_000, 20_000, 50_000, 100_000, 200_000)],
        xlog=True, ylog=True, xlabel="연산 예산 (로그 눈금)", ylabel="최종 비용 ↓ (로그 눈금, 작을수록 좋음)", height=280)

    # 2. 제안 5,000번에 드는 연산
    names = {("assign", 3): "배정 틀: 옮기기·맞바꾸기", ("route", 1): "순서 틀: 두 점 교환", ("route", 4): "순서 틀: 구간 뒤집기"}
    groups = []
    for (frame, mask), label in names.items():
        d = next(s for s in m["split"] if s["frame"] == frame and s["mask"] == mask and s["full"] == 0)
        f = next(s for s in m["split"] if s["frame"] == frame and s["mask"] == mask and s["full"] == 1)
        groups.append({"label": label, "values": [d["total"], f["total"]],
                       "texts": [ch.comma(d["total"]), f"{ch.comma(f['total'])} (×{f['total'] / d['total']:.0f})"]})
    desc = ("제안 5,000번을 처리하는 데 든 연산 합계입니다. " + " ".join(
        f"{g['label']}은 차분 {ch.comma(g['values'][0])}, 적용 후 복구 {ch.comma(g['values'][1])}이고." for g in groups)
        + " 적용 후 복구가 열여섯 배에서 서른두 배 많습니다.")
    out["ops-split.svg"] = ch.grouped_hbar(
        "제안 5,000번에 드는 연산", "같은 제안을 같은 순서로 받는 두 루프의 연산 합계입니다. 괄호는 차분 대비 배수입니다",
        desc, groups, [("차분 (계산만)", "base"), ("적용 후 복구 (전체 재계산)", "hi")], "연산 합계 ↓ (작을수록 좋음)")

    # 3. 근방별: 기준(구간 뒤집기)과 같은 시드끼리 비교
    nb = m["neighborhood"]["route"]
    rows = []
    for r in nb["rows"]:
        base = r["mask"] == nb["reference"]
        rows.append({"label": r["name"], "better": r["better"], "worse": r["worse"], "ref": base, "text": "비용 " + ch.comma(r["median"])})
    desc = ("순서 틀에서 이동의 구성을 바꿨을 때 기준(구간 뒤집기만)과 같은 시드끼리 비교한 결과입니다. 기준보다 나은 시드와 못한 시드의 수는 "
            + ", ".join(f"{r['name']} {r['better']} 대 {r['worse']}" for r in nb["rows"] if r["mask"] != nb["reference"])
            + "입니다. 옮기기와 뒤집기를 함께 쓰면 20개 중 16개에서 낫고 두 점 교환이나 이웃한 두 점 교환만 쓰면 모두 못합니다.")
    out["neighborhood-seeds.svg"] = ch.winloss_chart(
        "이동 구성별 승패 (기준: 구간 뒤집기)", f"순서 틀, 시드 {seeds}개를 기준과 짝지어 비교했습니다. 오른쪽 비용은 시드 20개 중 10번째로 작은 값입니다",
        desc, rows, seeds, "시드 20개 중 나은 시드와 못한 시드의 수", names=("기준보다 나은 시드", None, "기준보다 못한 시드"))
    return out
