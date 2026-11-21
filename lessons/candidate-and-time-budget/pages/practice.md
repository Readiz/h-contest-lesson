# stub practice

코드 환경: 일반 C++17

```cpp snippet=tb-timing
#include <chrono>
#include <cstdio>

long long nowNs() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}

// climbPlan의 시계 버전: 연산 수 대신 시각으로 멈추고, 후보 수를 정하는 남은 비율도 시각으로 계산한다.
// 마무리 단계가 없는 가장 짧은 형태이며, 바뀐 곳은 시계를 읽는 줄과 멈추는 줄 둘뿐이다.
template <class P>
long long climbTimed(P& p, hc::Random& rng, long long cost, long long endNs, int every, int kFirst, int kLast) {
    const long long begin = nowNs();
    int k = kFirst, since = every;
    while (true) {
        if (++since >= every) {
            since = 0; ++p.reads;
            const long long now = nowNs();                  // 시계는 여기서만 읽는다
            if (now >= endNs) break;
            k = byRemaining(kFirst, kLast, endNs - now, endNs - begin);
        }
        ++p.ops; ++p.props;
        Move mv;
        if (!proposeCand(p, rng, k, mv)) continue;
        const long long d = p.delta(mv);
        if (d < 0) { p.apply(mv); cost += d; }
    }
    return cost;
}

int main() {
    // 1) 연산 하나가 걸리는 시간: 실제로 쓸 틀(여기서는 N = 2000, 목록 8개)을 연산 수 예산으로 돌려 잰다.
    Plan plan;
    plan.limit = 3000000; plan.finish = 0; plan.every = 64; plan.clockCost = 0; plan.kFirst = plan.kLast = 8; plan.kFinish = 0;
    const long long t0 = nowNs();
    runRoute(1, 2000, 8, true, plan);
    const long long t1 = nowNs();
    const double nsPerOp = (double)(t1 - t0) / (double)route.ops;

    // 2) 시계를 한 번 읽는 데 드는 시간
    long long sink = 0;
    const long long t2 = nowNs();
    for (int i = 0; i < 100000; ++i) sink += nowNs() & 1;
    const long long t3 = nowNs();
    const double nsPerRead = (double)(t3 - t2) / 100000.0;

    // 3) 시간 제한 T ms를 연산 수 예산으로 바꾼다. 안전 계수 0.8은 이 환경과 채점 환경의 차이를 위한 여유다.
    const double limitMs = 2000.0, safety = 0.8;
    printf("연산 하나: %.2f ns\n", nsPerOp);
    printf("시계 한 번 읽기: %.1f ns (연산 %.1f개 분량, 확인값 %lld)\n", nsPerRead, nsPerRead / nsPerOp, sink & 1);
    printf("시간 제한 %.0f ms, 안전 계수 %.1f: 연산 예산 %lld\n", limitMs, safety, (long long)(limitMs * 1e6 * safety / nsPerOp));

    // 4) 시계 버전으로 50 ms 돌린다.
    genRoute(route, 1, 2000);
    route.buildCells(defaultSide(2000)); route.initSnake(); route.buildNbGrid(8);
    const long long saved = route.ops;
    const long long start = route.fullCost();
    route.ops = saved; route.props = route.reads = 0;
    hc::Random rng; rng.reset(1);
    const long long end = climbTimed(route, rng, start, nowNs() + 50000000LL, 64, 8, 8);
    printf("시계 버전 50 ms: 제안 %lld번, 시계 %lld번 읽음, 비용 %lld → %lld\n", route.props, route.reads, start, end);
    return 0;
}
```
