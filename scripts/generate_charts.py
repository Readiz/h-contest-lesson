"""실험 차트 생성기: 각 강의의 lesson-assets/measurements.json 값에서 차트 SVG를 다시 만든다.

    python3 scripts/generate_charts.py            # 모든 강의의 차트를 다시 쓴다
    python3 scripts/generate_charts.py --check    # 저장된 SVG와 바이트 비교(다르면 실패). validate_lessons.py가 호출한다

새 강의에 차트를 더하는 법 (설정 한 덩어리만 더하면 된다):
  1. `scripts/charts_<강의 id를 밑줄로>.py` 파일을 새로 만들고 `def charts(m: dict) -> dict[str, str]:` 를 쓴다
     (예: scripts/charts_hill_climbing_and_annealing.py). m은 그 강의의 measurements.json,
     반환값은 {"파일이름.svg": svg 문자열}. svg는 scripts/charts.py의 bar_chart · grouped_hbar · line_chart ·
     strip_chart · winloss_chart 중 하나로 만든다(숫자는 모두 m에서 읽는다. 손으로 옮기지 않는다).
  2. 이 파일은 고칠 필요가 없다. 모듈은 파일 이름으로 자동 발견된다(강의 하나당 파일 하나라 서로 충돌하지 않는다).
  3. `python3 scripts/generate_charts.py` 로 파일을 만들고, 본문 표 바로 위나 아래에
     `![대괄호 없는 설명](../lesson-assets/파일.svg)` 와 빈 줄 뒤 `[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/<id>/lesson-assets/파일.svg)` 를 둔다.
  4. 중앙값은 강의마다 정의가 다르다. 표가 "10번째로 작은 값"이면 measurements.json에 이미 있는 값을 쓰고,
     시드별 값에서 직접 구할 때는 표와 같은 정의(charts.median은 짝수 개일 때 가운데 둘의 평균)를 쓴다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load(lesson_id: str) -> dict:
    return json.loads((ROOT / "lessons" / lesson_id / "lesson-assets" / "measurements.json").read_text(encoding="utf-8"))


def discover() -> dict:
    out = {}
    for path in sorted((ROOT / "scripts").glob("charts_*.py")):
        mod = importlib.import_module(path.stem)
        lesson_id = path.stem[len("charts_"):].replace("_", "-")
        out[lesson_id] = mod.charts
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="저장된 SVG와 바이트 비교만 한다")
    args = ap.parse_args()
    bad: list[str] = []
    total = 0
    for lesson_id, fn in discover().items():
        for name, svg in fn(load(lesson_id)).items():
            path = ROOT / "lessons" / lesson_id / "lesson-assets" / name
            total += 1
            if args.check:
                if not path.exists() or path.read_bytes() != svg.encode("utf-8"):
                    bad.append(f"{lesson_id}/{name}")
            else:
                path.write_bytes(svg.encode("utf-8"))
    if bad:
        sys.exit("차트가 measurements.json과 다릅니다(python3 scripts/generate_charts.py 로 다시 만드세요): " + ", ".join(bad))
    print(f"OK: {total} charts {'match' if args.check else 'written'}")


if __name__ == "__main__":
    main()
