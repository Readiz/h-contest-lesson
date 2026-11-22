"""observe-and-act 강의의 그림 설정. m = lesson-assets/measurements.json."""
from __future__ import annotations

import charts as ch


def _contract_figure() -> str:
    """채점기를 부르는 유일한 통로 act와 하루 10번 x 10일 구조(개념 그림)."""
    title = "채점기는 act 하나를 거쳐서만 부른다"
    c = ch.Canvas()
    y0 = ch._header(c, title, "계획은 거울만 읽고, 규칙 검사와 날짜 넘김과 거울 갱신은 act 안에서 한 번에 합니다")
    y = y0 + 14
    h = 188

    def box(x: float, w: float, head: str, lines: list[str], fill: str, hot: bool = False) -> None:
        c.rect(x, y, w, h, fill, rx=10)
        c.text(x + w / 2, y + 32, 19, head, ch.INK, anchor="middle", weight="700")
        for i, ln in enumerate(lines):
            c.text(x + 14, y + 68 + i * 28, 17, ln, ch.INK)

    box(28, 186, "계획", ["거울 M만 읽고", "BFS로 목표를 고름", "다음 방향 dir 결정", "(채점기를 직접", "부르지 않음)"], "#dbe6f7")
    box(246, 250, "act(dir)", ["① canStep: 규칙 검사", "② 오늘 10번이면 nextDay", "③ move(dir)", "④ 거울 갱신 (위치, seen,", "    mirrorScore)"], "#f6e1cb", True)
    box(528, 164, "채점기", ["move, nextDay", "이동 횟수 검사", "실제 점수 계산", "(내용은 못 읽음)"], "#e7edf7")
    mid = y + h / 2
    for x1, x2 in ((214, 246), (496, 528)):
        c.line(x1 + 2, mid, x2 - 8, mid, ch.INK, 3)
        c.polyline([(x2 - 18, mid - 8), (x2 - 6, mid), (x2 - 18, mid + 8)], ch.INK, 3)
    c.text(28, y + h + 30, 18, "채점 결과와 비교할 값은 거울의 mirrorScore 하나입니다", ch.MUTED)
    y += h + 66
    c.text(28, y, 19, "이동 100번의 구조: 하루 최대 10번 × 10일", ch.INK, weight="700")
    y += 14
    cw = 63
    for d in range(10):
        x = 28 + d * (cw + 3)
        c.rect(x, y, cw, 54, "#9db6e0")
        c.text(x + cw / 2, y + 24, 17, f"{d + 1}일", ch.INK, anchor="middle", weight="700")
        c.text(x + cw / 2, y + 46, 16, "10번", ch.INK, anchor="middle")
    c.text(28, y + 84, 17, "날짜 경계는 점수와 무관해 계획은 날짜를 모르고 act가 넘깁니다", ch.MUTED)
    desc = ("계획, act, 채점기 세 상자를 화살표로 잇습니다. 계획은 거울만 읽어 다음 방향을 정하고, act가 규칙 검사, 오늘 10번이면 nextDay, move, 거울 갱신을 차례로 하며 채점기를 부르는 유일한 통로입니다. "
            "아래에는 하루 최대 10번씩 10일, 모두 100번의 이동 구조를 보이고, 날짜 경계는 점수와 무관해 act가 넘깁니다.")
    return ch._finish(c, title, desc, y + 106)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {"act-gateway.svg": _contract_figure()}

    # 1. 거울을 어긴 세 실수: 채점기 점수 대 거울 점수
    ok = next(r for r in m["rows"] if r["label"] == "정책 2")
    groups = [{"label": "정상 (정책 2)", "values": [ok["total"], ok["mirror_total"]]}]
    groups += [{"label": f["label"], "values": [f["total"], f["mirror_total"]]} for f in m["failures"]]
    desc = ("정책 2 코드에서 한 줄씩 고친 세 실수의 채점기 점수 합과 거울 점수 합입니다. 정상은 둘 다 " + ch.comma(ok["total"]) + "입니다. "
            + " ".join(f"{f['label']}은 채점기 {ch.comma(f['total'])}, 거울 {ch.comma(f['mirror_total'])}이고" for f in m["failures"])
            + " 모두 두 값이 어긋나 점수 대조로 잡히며 거절 요청은 세 경우 모두 0입니다.")
    out["mirror-mismatch.svg"] = ch.grouped_hbar(
        "실수하면 두 점수가 어긋난다", "정책 2 코드에서 한 줄씩 고친 변형의 10개 TC 점수 합입니다. 정상은 두 값이 같습니다. 거절 요청은 세 경우 모두 0입니다",
        desc, groups, [("채점기 점수", "base"), ("거울 점수", "hi")], "10개 TC 점수 합 ↑ (클수록 좋음, 어긋남이 문제)")

    # 2. 예측(주변 값 h의 합) 대 실제(다음 결정의 이득)
    cal = m["calibration"]
    rows = [{"label": "주변 값 h의 합 (예측)", "value": cal["sum_around"], "color": "light"},
            {"label": "다음 이득 합 (실제)", "value": cal["sum_next_gain"], "color": "hi"}]
    desc = (f"정책 2 기본값으로 10개 TC의 결정 {cal['decisions']}개에서 주변 값 h의 합은 {ch.comma(cal['sum_around'])}, 다음 결정에서 얻은 이득 합은 {ch.comma(cal['sum_next_gain'])}입니다. "
            f"비율은 {cal['next_gain_per_around']}로 주변 값 1점이 평균 0.16점만 실현됩니다.")
    out["prediction-vs-actual.svg"] = ch.bar_chart(
        "예측한 주변 값과 실제 이득", f"정책 2 기본값, 결정 {cal['decisions']}개의 합입니다. 실제는 예측의 {cal['next_gain_per_around']}배입니다",
        desc, rows, "점수 합 (두 막대의 비율이 핵심)")
    return out
