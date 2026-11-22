"""reading-the-score 강의의 그림 설정. m = lesson-assets/measurements.json(= entropy2d-benchmark.json 링크)."""
from __future__ import annotations

import charts as ch

PASS_LINE = 1_917_000  # 본문 계약 표의 통과 기준


SOURCE = "entropy2d-benchmark.json"

def charts(m: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    rows_m = m["rows"]
    limit = sum(t["limit"] for t in m["tcs"])

    # 1. 단계별 점수 합
    names = ["0단계 기준선", "1단계 중앙으로 밀기", "2단계 차분 탐욕", "3단계 큰 이득부터", "4단계 빈 칸 경로", "5단계 목표 짝짓기"]
    rows = [{"label": nm, "value": r["total"], "color": "hi" if i == 5 else "base"} for i, (nm, r) in enumerate(zip(names, rows_m))]
    rows.append({"label": "통과 기준", "value": PASS_LINE, "color": "mute"})
    desc = ("단계별 10개 TC 점수 합입니다. " + ", ".join(f"{r['label']} {ch.comma(r['value'])}" for r in rows)
            + f"입니다. 4단계는 통과 기준에 {ch.comma(PASS_LINE - rows_m[4]['total'])}점 모자라고 5단계는 {ch.comma(rows_m[5]['total'] - PASS_LINE)}점 넘습니다.")
    out["stage-scores.svg"] = ch.bar_chart(
        "단계별 점수 합", "공개 채점기 10개 TC의 점수 합입니다. 점수는 같은 입력에서 항상 같고, 회색 막대는 통과 기준입니다",
        desc, rows, "점수 합 ↑ (클수록 좋음)")

    # 2. 단계별 사용한 이동 수
    rows = [{"label": nm, "value": sum(r["used"]), "color": "hi" if i == 4 else "base"} for i, (nm, r) in enumerate(zip(names, rows_m)) if i > 0]
    desc = (f"단계별로 쓴 이동 횟수의 10개 TC 합이고 한도는 {ch.comma(limit)}입니다. " + ", ".join(f"{r['label']} {ch.comma(r['value'])}" for r in rows)
            + "입니다. 4단계가 가장 많이 쓰고 5단계는 같은 엔트로피에서 이동을 938,573번 줄였으며 이동마다 보너스가 깎이므로 그만큼 점수가 오릅니다.")
    out["move-use.svg"] = ch.bar_chart(
        "단계별 사용한 이동 수", f"10개 TC 합이고 이동 한도 합은 {ch.comma(limit)}입니다. 이동이 많을수록 점수의 보너스가 깎입니다. 0단계는 이동이 없어 뺐습니다",
        desc, rows, "이동 횟수 ↓ (적을수록 좋음)")

    # 3. 5단계 변형: 5단계에 못 미친 점수(TC별 차이의 평균)
    base = rows_m[5]["tcs"]
    labels = {"ROUNDS 1": "ROUNDS 1", "빈 칸 순서대로 짝짓기": "빈 칸 순서대로", "3단계를 먼저 실행": "3단계를 먼저", "문턱 켬": "문턱 켬", "4단계 TC별 문턱 ×10": "4단계 TC별 문턱"}
    rows = []
    for a in m["ablations"]:
        loss = sum(b - x for b, x in zip(base, a["tcs"])) / len(base)
        rows.append({"label": labels[a["label"]], "value": loss, "color": "base", "text": ch.comma(loss, 1)})
    desc = ("5단계 전체에서 한 가지씩 바꿨을 때 TC별 점수가 5단계보다 평균 얼마나 낮아졌는지입니다. "
            + ", ".join(f"{r['label']} {r['text']}" for r in rows)
            + "이고 문턱을 켠 변형은 걸러지는 짝이 없어 0으로 5단계와 같습니다. 어느 변형도 5단계보다 높은 TC가 없어 값이 클수록 5단계보다 못합니다.")
    out["ablation-loss.svg"] = ch.bar_chart(
        "5단계에서 하나씩 바꾸면", "10개 TC에서 5단계 점수보다 평균 얼마나 낮아졌는지입니다. 모든 변형이 5단계보다 같거나 낮습니다",
        desc, rows, "5단계보다 낮아진 점수 (TC 평균) ↓ (작을수록 5단계에 가까움)", value_digits=1)
    return out
