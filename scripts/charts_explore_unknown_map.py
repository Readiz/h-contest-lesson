"""explore-unknown-map 강의의 그림 설정. m = lesson-assets/measurements.json."""
from __future__ import annotations

import charts as ch

PASS_LINE = 6_500_000  # 본문 계약 표의 통과 기준(낮을수록 좋음)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    rows_m = m["rows"]

    # 1. 단계별 점수 합(비용, 작을수록 좋음)
    names = ["기준선 DFS", "정책 1, SCAN_MIN 0", "정책 1, SCAN_MIN 1", "정책 1, SCAN_MIN 6", "정책 2, SCAN_MIN 1", "정책 2, SCAN_MIN 6"]
    cols = ["mute", "light", "light", "base", "light", "hi"]
    rows = [{"label": nm, "value": r["total"], "color": col} for nm, r, col in zip(names, rows_m, cols)]
    rows.append({"label": "통과 기준", "value": PASS_LINE, "color": "mute"})
    desc = ("단계별 10개 TC 점수 합(비용)입니다. " + ", ".join(f"{r['label']} {ch.comma(r['value'])}" for r in rows)
            + "입니다. 통과 기준 6,500,000보다 낮은 것은 SCAN_MIN 6인 두 정책뿐이고 스캔을 줄이는 것이 가장 큰 개선입니다.")
    out["stage-costs.svg"] = ch.bar_chart(
        "단계별 점수 합 (비용)", "공식 입력 10개 TC의 총 비용입니다. 회색 막대는 통과 기준이며 이 값보다 낮아야 통과합니다",
        desc, rows, "총 비용 ↓ (작을수록 좋음)")

    # 2. 비용 구성: 정책 2 (SCAN_MIN 6)를 공식 입력과 홀드아웃에서
    off, hold = rows_m[5], m["holdout_rows"][5]
    unit = {"스캔": ("scans", 20), "이동": ("moves", 10), "막힘": ("bumps", 10), "회전": ("turns", 15)}
    groups = [{"label": f"{k} (칸당 {w})", "values": [off[key] * w, hold[key] * w]} for k, (key, w) in unit.items()]
    desc = ("정책 2(SCAN_MIN 6)의 총 비용을 행동별로 나눈 그림입니다. 공식 입력은 " + ", ".join(f"{k} {ch.comma(off[key] * w)}" for k, (key, w) in unit.items())
            + ", 직접 만든 홀드아웃 지도는 " + ", ".join(f"{k} {ch.comma(hold[key] * w)}" for k, (key, w) in unit.items())
            + "입니다. 이동이 가장 크고 회전, 스캔, 막힘 순이며 이동의 하한은 공식 입력 " + ch.comma(m["move_floor"]["official"]) + "입니다.")
    out["cost-parts.svg"] = ch.grouped_hbar(
        "행동별 비용 구성", "정책 2, SCAN_MIN 6의 10개 TC 비용 합을 행동별로 나눴습니다. 괄호는 행동 한 번의 비용입니다",
        desc, groups, [("공식 입력", "base"), ("홀드아웃 지도", "hi")], "행동별 비용 합 ↓ (작을수록 좋음)")

    # 3. SCAN_MIN에 따른 총 비용
    def pts(rows_: list[dict]) -> list[tuple[int, int]]:
        return [(int(r["label"].split()[1]), r["total"]) for r in rows_ if r["label"].startswith("SCAN_MIN")]

    a, b = pts(m["sweeps"]), pts(m["holdout_sweeps"])
    series = [
        {"name": "공식 입력", "color": "base", "points": a, "label_idx": [6], "pos": "down"},
        {"name": "홀드아웃 지도", "color": "hi", "points": b, "label_idx": [6], "pos": "up"},
    ]
    desc = ("SCAN_MIN을 0에서 9까지 바꿨을 때 정책 2의 10개 TC 비용 합입니다. 공식 입력은 " + ", ".join(ch.comma(y) for _, y in a)
            + "이고 홀드아웃 지도는 " + ", ".join(ch.comma(y) for _, y in b)
            + "입니다. 두 입력 모두 6에서 가장 낮고 7부터 오르며 8 이상에서는 스캔을 거의 안 해 막힘과 회전이 늘어 크게 높아집니다. 통과 기준은 6,500,000입니다.")
    out["scan-min-curve.svg"] = ch.line_chart(
        "SCAN_MIN에 따른 총 비용", "정책 2, TURN_W 15, UNK_PEN 0. 한 번에 SCAN_MIN만 바꿨고 가장 낮은 6에 값을 적었습니다. 통과 기준은 6,500,000입니다",
        desc, series, xticks=[(x, str(x)) for x in range(10)],
        yticks=[(v, ch.comma(v)) for v in range(5_000_000, 12_000_001, 1_000_000)],
        xlog=False, ylog=False, xlabel="SCAN_MIN (모르는 칸이 이 수 이상일 때만 스캔)", ylabel="총 비용 ↓ (작을수록 좋음)",
        height=300)
    return out
