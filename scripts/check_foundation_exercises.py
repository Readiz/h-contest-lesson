"""Check the exact input/output examples printed in the foundation exercises.

These deliberately small reference solvers verify the published sample answers;
they are not implementations intended for the full exercise constraints.
"""
from itertools import combinations, permutations
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
INF = 10**60
EXPECTED = {
    "complexity-input-size", "prefix-sum-difference", "two-pointers-sliding-window",
    "binary-search", "coordinate-compression", "priority-queue-heap", "meldable-heap",
    "bfs-dfs-grid", "dynamic-programming", "zero-one-bfs", "topological-sort-dag",
    "dijkstra", "bellman-ford-negative-cycle", "floyd-warshall", "fenwick-tree",
    "treap", "minimax-alpha-beta", "proof-and-invariants", "dynamic-segment-tree",
}


def all_pairs(n, edges):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] < INF and d[k][j] < INF:
                    d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d


def solve(slug, text):
    tokens = iter(text.split())
    integer = lambda: int(next(tokens))
    if slug == "complexity-input-size":
        t, n, width = integer(), integer(), integer()
        assert n <= 30
        return f"{t * len(list(combinations(range(n), 2)))} {n * width}"
    if slug == "prefix-sum-difference":
        n, m, q = integer(), integer(), integer()
        a = [integer() for _ in range(n)]
        for _ in range(m):
            l, r, delta = integer(), integer(), integer()
            for i in range(l, r):
                a[i] += delta
        return "\n".join(str(sum(a[integer():integer()])) for _ in range(q))
    if slug == "two-pointers-sliding-window":
        n, target = integer(), integer()
        a = [integer() for _ in range(n)]
        return str(min((r-l for l in range(n) for r in range(l+1, n+1)
                        if sum(a[l:r]) >= target), default=0))
    if slug == "binary-search":
        n, target = integer(), integer()
        a = [integer() for _ in range(n)]
        return str(next(t for t in range(min(a)*target+1) if sum(t//x for x in a) >= target))
    if slug == "coordinate-compression":
        a = [integer() for _ in range(integer())]
        coords = sorted(set(a))
        return "\n".join([str(len(coords)), " ".join(str(coords.index(x)) for x in a), " ".join(map(str, coords))])
    if slug == "priority-queue-heap":
        n, k = integer(), integer()
        a = [integer() for _ in range(n)]
        return "\n".join(str(sum(sorted(a[:i], reverse=True)[:k])) for i in range(1, n+1))
    if slug == "meldable-heap":
        n, q = integer(), integer()
        a = [integer() for _ in range(n)]
        group, alive, out = list(range(n)), [True]*n, []
        for _ in range(q):
            op = next(tokens)
            if op == "M":
                x, y = integer(), integer()
                gx, gy = group[x], group[y]
                group = [gx if g == gy else g for g in group]
            else:
                v = integer()
                have = [(a[i], i) for i in range(n) if alive[i] and group[i] == group[v]]
                if have:
                    value, i = min(have)
                    alive[i] = False
                    out.append(str(value))
                else:
                    out.append("EMPTY")
        return "\n".join(out)
    if slug == "bfs-dfs-grid":
        h, w, sy, sx, ty, tx = (integer() for _ in range(6))
        grid = [next(tokens) for _ in range(h)]
        edges = []
        for y in range(h):
            for x in range(w):
                if grid[y][x] != ".":
                    continue
                for dy, dx in ((0,1),(0,-1),(1,0),(-1,0)):
                    yy, xx = y+dy, x+dx
                    if 0 <= yy < h and 0 <= xx < w and grid[yy][xx] == ".":
                        edges.append((y*w+x, yy*w+xx, 1))
        value = all_pairs(h*w, edges)[sy*w+sx][ty*w+tx]
        return str(value if value < INF else -1)
    if slug == "dynamic-programming":
        n, limit = integer(), integer()
        items = [(integer(), integer()) for _ in range(n)]
        assert n <= 20
        best = 0
        for mask in range(1 << n):
            picked = [items[i] for i in range(n) if mask >> i & 1]
            if sum(w for w, _ in picked) <= limit:
                best = max(best, sum(v for _, v in picked))
        return str(best)
    if slug in {"zero-one-bfs", "dijkstra", "bellman-ford-negative-cycle"}:
        n, m, start = integer(), integer(), integer()
        edges = [(integer(), integer(), integer()) for _ in range(m)]
        d = all_pairs(n, edges)
        out = []
        for v in range(n):
            if slug == "bellman-ford-negative-cycle":
                bad = any(d[start][k] < INF and d[k][k] < 0 and d[k][v] < INF for k in range(n))
                out.append("NEGATIVE" if bad else "UNREACHABLE" if d[start][v] == INF else str(d[start][v]))
            else:
                out.append(str(d[start][v] if d[start][v] < INF else -1))
        return " ".join(out)
    if slug == "topological-sort-dag":
        n, m = integer(), integer()
        assert n <= 8
        edges = [(integer(), integer()) for _ in range(m)]
        for order in permutations(range(n)):
            if all(order.index(u) < order.index(v) for u, v in edges):
                return " ".join(map(str, order))
        return "CYCLE"
    if slug == "floyd-warshall":
        n, m, q = integer(), integer(), integer()
        edges = [(integer(), integer(), integer()) for _ in range(m)]
        out = []
        for _ in range(q):
            start, target = integer(), integer()
            d = [INF]*n
            d[start] = 0
            for _ in range(n-1):
                for u, v, weight in edges:
                    if d[u] < INF:
                        d[v] = min(d[v], d[u]+weight)
            out.append(str(d[target]) if d[target] < INF else "UNREACHABLE")
        return "\n".join(out)
    if slug == "fenwick-tree":
        n, q = integer(), integer()
        a, out = [integer() for _ in range(n)], []
        for _ in range(q):
            op, left, right = next(tokens), integer(), integer()
            if op == "A":
                a[left-1] += right
            else:
                out.append(str(sum(a[left-1:right])))
        return "\n".join(out)
    if slug == "treap":
        q, a, out = integer(), set(), []
        for _ in range(q):
            op, x = next(tokens), integer()
            if op == "I":
                a.add(x)
            elif op == "D":
                a.discard(x)
            elif op == "R":
                out.append(str(sum(v < x for v in a)))
            else:
                out.append(str(sorted(a)[x]) if x < len(a) else "INVALID")
        return "\n".join(out)
    if slug == "minimax-alpha-beta":
        depth = integer()
        values = [integer() for _ in range(1 << depth)]
        for level in reversed(range(depth)):
            choose = max if level % 2 == 0 else min
            values = [choose(values[i:i+2]) for i in range(0, len(values), 2)]
        return str(values[0])
    if slug == "proof-and-invariants":
        n = integer()
        intervals = [(integer(), integer()) for _ in range(n)]
        current, finish = 0, -1
        for start, end in sorted(intervals):
            if finish <= start:
                current, finish = current+1, end
        best = 0
        for mask in range(1 << n):
            picked = sorted(intervals[i] for i in range(n) if mask >> i & 1)
            if all(picked[i-1][1] <= picked[i][0] for i in range(1, len(picked))):
                best = max(best, len(picked))
        return f"{current} {best}"
    if slug == "dynamic-segment-tree":
        q, a, out = integer(), [0]*20, []
        for _ in range(q):
            op, l, r = next(tokens), integer(), integer()
            assert 0 <= l <= r <= 20
            if op == "A":
                delta = integer()
                for i in range(l, r):
                    a[i] += delta
            else:
                out.append(str(sum(a[l:r])))
        return "\n".join(out)
    raise AssertionError(slug)


def main():
    manifest = json.loads((ROOT / "lessons.json").read_text())
    found = set()
    for lesson in manifest["lessons"]:
        path = ROOT / "lessons" / lesson["lessonId"] / "lesson.md"
        examples = re.findall(r"```text exercise=([\w-]+) role=(input|output)\n(.*?)\n```", path.read_text(), re.S)
        if not examples:
            continue
        slug = lesson["lessonId"]
        assert [(s, role) for s, role, _ in examples] == [(slug, "input"), (slug, "output")], slug
        actual = solve(slug, examples[0][2])
        assert actual.strip() == examples[1][2].strip(), (slug, actual, examples[1][2])
        assert lesson["practiceStatus"] in {"linked", "verified"}, slug
        found.add(slug)
    assert found == EXPECTED, found ^ EXPECTED
    print(f"OK: {len(found)} foundation exercise samples match small independent reference solvers")


if __name__ == "__main__":
    main()
