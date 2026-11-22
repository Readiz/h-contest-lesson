"""large-input-search 강의의 그림 설정. m = lesson-assets/measurements.json(= coupang1-benchmark.json 링크)."""
from __future__ import annotations

import math

import charts as ch


def _ops_figure() -> str:
    """연산 수 예산표(본문 표)를 로그 눈금 막대로: 5×10^9 선 아래만 쓸 수 있다. 숫자는 본문 표의 값이다."""
    title = "방법별 연산 수와 예산"
    rows = [("센터 목록에서 고르기", 5e6, "5×10^6", "base"), ("운행 안 순서 개선", 1e9, "약 10^9", "base"),
            ("배송마다 센터 전부", 1e9, "10^9", "base"), ("칸으로 후보 줄이기", 6.4e9, "6.4×10^9", "lhi"),
            ("남은 배송 전부 훑기", 5.0e11, "5.0×10^11", "hi"), ("배송 쌍 거리 전부", 5e11, "5×10^11", "hi")]
    budget = 5e9
    c = ch.Canvas()
    y0 = ch._header(c, title, "후보 하나를 확인하는 일을 기본 연산 1회로 세고, 시간 제한의 절반인 5×10^9를 상한으로 잡았습니다 (가로는 로그 눈금)")
    lo, hi = 1e6, 1e12
    lw = 230
    x0, x1 = 28 + lw + 14, 720 - 28 - 110

    def px(v: float) -> float:
        return x0 + (x1 - x0) * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    top = y0 + 8
    bottom = top + 40 * len(rows)
    for e in range(6, 13, 2):
        c.line(px(10 ** e), top, px(10 ** e), bottom, ch.GRID, 1.5)
        c.text(px(10 ** e), bottom + 22, 16, f"10^{e}", ch.MUTED, anchor="middle")
    y = top
    for label, v, text, col in rows:
        c.text(28, y + 26, 19, label, ch.INK, weight="700" if col == "hi" else "")
        c.rect(x0, y + 6, px(v) - x0, 26, ch.COLORS[col])
        c.text(x1 + 12, y + 26, 17, text, ch.INK)
        y += 40
    c.line(px(budget), top - 4, px(budget), bottom, ch.INK, 3, "8 6")
    c.text(px(budget) - 8, top - 10, 17, "예산 5×10^9", ch.INK, anchor="end", weight="700")
    c.line(x0, top, x0, bottom, ch.MUTED, 1.5)
    ch._axis_title(c, bottom + 50, "연산 수 (로그 눈금) ↓ (적을수록 좋음)")
    desc = ("방법별 연산 수를 로그 눈금 막대로 비교하고 시간 제한의 절반에 해당하는 예산 5×10^9에 선을 그은 그림입니다. 센터 목록에서 고르기 5×10^6, 운행 안 순서 개선 약 10^9, 배송마다 센터 전부 10^9는 예산 안이고, "
            "칸으로 후보 줄이기 6.4×10^9는 예산을 조금 넘지만 측정으로 가능했으며, 남은 배송 전부 훑기와 배송 쌍 거리 전부는 5×10^11로 예산의 백 배가 넘어 불가능합니다.")
    return ch._finish(c, title, desc, bottom + 66)


def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {"ops-budget.svg": _ops_figure()}
    st = {s["key"]: s for s in m["stages"]}
    line = m["pass_line"]

    # 1. 단계별: 통과 기준 대비 배수
    order = [("trip50", "50개씩 운행", "light"), ("trip20", "+ 적재 20개", "light"), ("choose", "+ 센터 선택 밀도", "light"), ("improve", "+ 순서 개선", "hi")]
    rows = [{"label": lab, "value": st[k]["total"] / line, "color": col, "text": f"{st[k]['total'] / line:.2f}배"} for k, lab, col in order]
    base = st["baseline"]["total"] / line
    desc = (f"통과 기준 {ch.comma(line)}에 대한 점수의 배수입니다. " + ", ".join(f"{lab} {r['text']}" for (k, lab, _), r in zip(order, rows))
            + f"이며 1배 아래면 통과입니다. 1개씩 싣는 기준선은 {base:.2f}배라 눈금 밖이라 뺐습니다.")
    out["stage-ratio.svg"] = ch.bar_chart(
        "단계별 점수, 통과 기준 대비", f"입력 1개, 점수는 결정적입니다. 1배가 통과 기준이고 1개씩 싣는 기준선({base:.2f}배)은 눈금 밖이라 뺐습니다",
        desc, rows, f"점수 ÷ 통과 기준 ↓ (작을수록 좋음, 1배 미만이 통과)", value_digits=2)

    # 2. 비용이 쌓이는 곳: 10% 구간별 비중
    dec = st["improve"]["deciles"]
    parts = [dec[0]] + [dec[i] - dec[i - 1] for i in range(1, len(dec))]
    total = dec[-1]
    rows = [{"label": f"{i * 10 + 1}~{i * 10 + 10}%", "value": p / total * 100, "color": "hi" if i == len(parts) - 1 else "base",
             "text": f"{p / total * 100:.1f}"} for i, p in enumerate(parts)]
    rows = [{"label": f"{(i + 1) * 10}%", "value": r["value"], "color": r["color"], "text": r["text"]} for i, r in enumerate(rows)]
    desc = ("본문 제출 코드가 쓴 비용을 처리한 배송 수 10% 구간마다 나눈 비중입니다. 비중은 " + ", ".join(f"{r['text']}%" for r in rows)
            + "이며 마지막 10% 구간이 전체의 " + rows[-1]["text"] + "%를 써 가장 큽니다. 남은 배송이 드물어져 배송 간격이 넓어지기 때문입니다.")
    out["decile-cost.svg"] = ch.bar_chart(
        "처리한 배송 10% 구간별 비용 비중", f"본문 제출 코드(적재 20, 밀도 가중치 25, 순서 개선 3회)의 총 비용 {ch.comma(total)}을 구간별로 나눴습니다. 마지막 구간을 강조했습니다",
        desc, rows, "총 비용 중 비중 (%), 가로는 누적 처리 배송 비율", orient="v", value_digits=1)

    # 3. 한 번에 한 값씩 바꾼 점수 (본문 표의 값만)
    groups = [("loads", "적재 {}개", (10, 20, 30, 50), "base"), ("betas", "밀도 가중치 {}", (0, 10, 25, 100), "light"),
              ("passes", "순서 개선 {}회", (0, 1, 3, 10), "mute")]
    body_total = st["improve"]["total"]
    rows = []
    for key, fmt, vals, col in groups:
        for e in m[key]:
            if e["value"] in vals:
                rows.append({"label": fmt.format(e["value"]), "value": e["total"], "color": col,
                             "text": ch.comma(e["total"]) + ("" if e["total"] == body_total else f" ({(e['total'] / body_total - 1) * 100:+.1f}%)")})
    body = {"loads": 20, "betas": 25, "passes": 3}
    for r, (key, fmt, vals, col) in zip(rows, [g for g in groups for _ in range(4)]):
        if r["label"] == fmt.format(body[key]):
            r["color"] = "hi"
    desc = ("한 번에 한 값씩 바꿔 얻은 점수입니다(나머지는 적재 20, 가중치 25, 개선 3회, 정확한 탐색). " + ", ".join(f"{r['label']} {r['text']}" for r in rows)
            + "입니다. 적재 10개와 50개, 가중치 0이 눈에 띄게 높고 나머지는 9.3억에서 9.5억대로 모여 있으며, 본문 설정 세 값은 같은 점수 " + ch.comma(st["improve"]["total"]) + "입니다.")
    out["param-scores.svg"] = ch.bar_chart(
        "한 값씩 바꿨을 때의 점수", "입력 1개, 점수는 결정적입니다. 주황은 본문이 쓰는 값(세 설정이 같은 점수)이고, 괄호는 본문 점수 대비 차이입니다. 막대는 0에서 시작합니다",
        desc, rows, "점수 ↓ (작을수록 좋음)",
        legend=[("box", ch.BLUE, "적재 수"), ("box", ch.LBLUE, "밀도 가중치"), ("box", ch.GRAY, "순서 개선 반복"), ("box", ch.ORANGE, "본문 설정")])
    return out
