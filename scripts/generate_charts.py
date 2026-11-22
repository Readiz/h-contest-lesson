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
import importlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts as ch  # noqa: E402

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


def check_spec(lesson_id: str, name: str, svg: str) -> list[str]:
    """그림 규격(폭 720, 글자 16~28 정수, 제목 27, role·title·desc)과 본문 삽입(대체 텍스트 + 크게 보기 줄)을 확인한다."""
    errs = []
    if not re.search(r'viewBox="0 0 720 \d+"', svg):
        errs.append("viewBox")
    if 'role="img"' not in svg or "<title" not in svg or "<desc" not in svg:
        errs.append("role/title/desc")
    sizes = [int(v) for v in re.findall(r'font-size="(\d+)"', svg)]
    if not sizes or min(sizes) < 16 or max(sizes) > 28 or 27 not in sizes:
        errs.append(f"font sizes {sorted(set(sizes))}")
    height = int(re.search(r'viewBox="0 0 720 (\d+)"', svg).group(1))
    for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="(\d+)"([^>]*)>([^<]*)</text>', svg):
        x, y, size, attrs, body = float(m.group(1)), float(m.group(2)), int(m.group(3)), m.group(4), m.group(5)
        width = ch.tw(body, size)
        if 'text-anchor="end"' in attrs:
            left, right = x - width, x
        elif 'text-anchor="middle"' in attrs:
            left, right = x - width / 2, x + width / 2
        else:
            left, right = x, x + width
        if left < 8 or right > 712 or y > height - 4:
            errs.append(f"text leaves the figure: {body!r}")
    pages = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "lessons" / lesson_id / "pages").glob("*.md"))
    base = "https://git.readiz.com/h-contest-lesson/lessons/" + lesson_id + "/lesson-assets/" + name
    pattern = r"!\[[^\]\[]+\]\(\.\./lesson-assets/" + re.escape(name) + r"\)\n\n\[그림 크게 보기\]\(" + re.escape(base) + r"\)"
    if not re.search(pattern, pages):
        errs.append("본문에 대체 텍스트 그림과 '그림 크게 보기' 줄이 없음")
    return errs


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
                bad += [f"{lesson_id}/{name}: {e}" for e in check_spec(lesson_id, name, svg)]
            else:
                path.write_bytes(svg.encode("utf-8"))
    if bad:
        sys.exit("차트가 measurements.json과 다릅니다(python3 scripts/generate_charts.py 로 다시 만드세요): " + ", ".join(bad))
    print(f"OK: {total} charts {'match' if args.check else 'written'}")


if __name__ == "__main__":
    main()
