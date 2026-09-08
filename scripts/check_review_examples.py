"""Compile actual lesson snippets together and check the errors found in the full review."""
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'scripts/review-example-cases.json').read_text())
HEADERS = '''#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#include <numeric>
#include <random>
#include <string>
#include <vector>
'''

def main():
    with tempfile.TemporaryDirectory(prefix='lesson-review-') as folder:
        for case in CASES:
            parts = [HEADERS]
            for snippet in case['snippets']:
                markdown = (ROOT / snippet['path']).read_text()
                blocks = re.findall(r'```cpp[^\n]*\n(.*?)\n```', markdown, re.S)
                parts.append(blocks[snippet['block']])
            if case['body'] is not None:
                parts.append('int main() {\n' + case['body'] + '\n}')
            src = Path(folder) / (case['name'] + '.cpp')
            exe = src.with_suffix('')
            src.write_text('\n'.join(parts))
            try:
                subprocess.run(['c++', '-std=c++17', '-O1', '-g',
                                '-fsanitize=address,undefined', str(src), '-o', str(exe)],
                               check=True, capture_output=True, text=True, timeout=60)
                result = subprocess.run([str(exe)], input=case['stdin'], capture_output=True,
                                        text=True, check=True, timeout=30)
                if case['body'] is None:
                    assert result.stdout == case['expected'], (result.stdout, case['expected'])
            except subprocess.CalledProcessError as exc:
                raise SystemExit(f"FAIL: {case['name']}\n{exc.stderr}")
            print('PASS:', case['name'], flush=True)
    print(f'OK: {len(CASES)} composed, boundary and differential cases with ASan/UBSan')

if __name__ == '__main__':
    main()
