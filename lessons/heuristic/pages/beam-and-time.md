# 휴리스틱 알고리즘: Beam Search와 시간 관리

## 9. Beam Search

Beam Search는 답 하나만 들고 가는 대신, 좋아 보이는 후보 여러 개를 동시에 유지하는 방법입니다.

```text
현재 후보 목록을 가지고 있다.
각 후보에서 다음 선택들을 만들어 낸다.
점수가 높은 후보 K개만 남긴다.
이 과정을 끝까지 반복한다.
```

![Beam Search 후보 유지](../lesson-assets/beam-search.svg)

STL 없이 구현할 때는 고정 크기 배열과 선택 정렬 일부만으로 충분합니다. 아래 코드는 전체 구조를 보여 주는 골격입니다. `makeBranches`와 `applyBranch`는 문제마다 달라지는 부분입니다.

```cpp
const int BEAM_SIZE = 24;
const int BRANCH_SIZE = 6;
const int POOL_SIZE = BEAM_SIZE * BRANCH_SIZE;
const int MAX_DEPTH = 256;

struct Branch {
    int value;
};

struct Candidate {
    int depth;
    int choice[MAX_DEPTH];
    long long score;
};

Candidate beam[BEAM_SIZE];
Candidate pool[POOL_SIZE];
int beamCount = 0;
int poolCount = 0;

void swapCandidate(Candidate& a, Candidate& b) {
    Candidate t = a;
    a = b;
    b = t;
}

void addCandidateToPool(const Candidate& c) {
    if (poolCount < POOL_SIZE) {
        pool[poolCount] = c;
        ++poolCount;
    }
}

void keepTopBeam() {
    int limit = poolCount < BEAM_SIZE ? poolCount : BEAM_SIZE;

    for (int i = 0; i < limit; ++i) {
        int best = i;
        for (int j = i + 1; j < poolCount; ++j) {
            if (pool[j].score > pool[best].score) {
                best = j;
            }
        }
        if (best != i) {
            swapCandidate(pool[i], pool[best]);
        }
        beam[i] = pool[i];
    }

    beamCount = limit;
}
```

Beam Search의 핵심은 후보 점수입니다. 아직 완성되지 않은 답을 비교해야 하므로, 지금까지의 점수뿐 아니라 앞으로 좋아질 가능성까지 어느 정도 반영해야 합니다.

```cpp
int makeBranches(const Candidate& c, Branch branches[]) {
    int count = 0;

    for (int v = 0; v < BRANCH_SIZE; ++v) {
        branches[count].value = v;
        ++count;
    }

    return count;
}

Candidate applyBranch(const Candidate& c, const Branch& b) {
    Candidate next = c;
    next.choice[next.depth] = b.value;
    ++next.depth;

    next.score += 1000 - b.value * 10; // 실제 문제에서는 평가식으로 바꾼다.
    return next;
}

void runBeamSearch(int targetDepth) {
    Candidate start;
    start.depth = 0;
    start.score = 0;

    beam[0] = start;
    beamCount = 1;

    for (int depth = 0; depth < targetDepth && depth < MAX_DEPTH; ++depth) {
        poolCount = 0;

        for (int i = 0; i < beamCount; ++i) {
            Branch branches[BRANCH_SIZE];
            int branchCount = makeBranches(beam[i], branches);

            for (int b = 0; b < branchCount; ++b) {
                Candidate next = applyBranch(beam[i], branches[b]);
                addCandidateToPool(next);
            }
        }

        keepTopBeam();
    }
}
```

`BEAM_SIZE`가 크면 탐색은 넓어지지만 느려지고, 작으면 빨라지지만 한 번 잘못 고른 후보를 놓치기 쉽습니다. 완성 전 후보의 점수가 부정확한 문제라면 beam을 조금 넓게 잡는 편이 안전합니다.

## 10. 무작위성과 재시도

휴리스틱은 한 번 실행한 결과만 믿기 어렵습니다. 같은 알고리즘이라도 seed, 초기해, 변경 연산 순서에 따라 결과가 달라질 수 있습니다.

그래서 제한 시간이 허락하면 여러 번 재시도합니다.

```cpp
void solveWithRestarts(const Problem& p, State& answer) {
    State current;
    State bestOfRun;
    State globalBest;
    long long globalBestScore = NEG_INF;

    for (int restart = 0; restart < 20; ++restart) {
        seed = 5ULL + (unsigned long long)restart * 1000003ULL;

        makeInitialState(p, current, 1);

        long long runScore;
        improveByAnnealing(p, current, bestOfRun, runScore);

        if (runScore > globalBestScore) {
            copyState(p, globalBest, bestOfRun);
            globalBestScore = runScore;
        }
    }

    copyState(p, answer, globalBest);
}
```

재시도를 쓸 때는 각 시도에 너무 긴 시간을 쓰지 않도록 조절해야 합니다. 좋은 답 하나를 깊게 개선하는 전략과, 여러 답을 얕게 훑는 전략 중 어느 쪽이 나은지는 문제마다 다릅니다.

## 11. 시간 관리

STL과 C 헤더를 못 쓰면 `chrono`나 `clock`을 쓸 수 없습니다. 그런 환경에서는 두 가지 방식 중 하나를 택합니다.

| 방식 | 설명 |
| --- | --- |
| 고정 반복 횟수 | 로컬에서 반복 횟수를 보수적으로 튜닝하고 제출 코드에서는 그 횟수만 돈다 |
| 제공 시간 함수 | 문제 템플릿이나 채점 환경이 `elapsedMillis()` 같은 함수를 제공하면 그 함수만 호출한다 |

제공 시간 함수가 없다면 아래처럼 반복 횟수로 제어합니다.

```cpp
int shouldStopByIteration(int iter) {
    return iter >= ITERATION_LIMIT;
}

void improveWithIterationBudget(const Problem& p, State& current, State& best, long long& bestScore) {
    long long currentScore = scoreState(p, current);
    copyState(p, best, current);
    bestScore = currentScore;

    for (int iter = 0; !shouldStopByIteration(iter); ++iter) {
        Move mv = makeRandomMove(p, current);
        applyMove(p, current, mv);

        long long nextScore = scoreState(p, current);
        if (nextScore >= currentScore) {
            currentScore = nextScore;
            if (currentScore > bestScore) {
                copyState(p, best, current);
                bestScore = currentScore;
            }
        } else {
            rollbackMove(p, current, mv);
        }
    }
}
```

반복 횟수는 로컬에서 충분히 여유 있게 잡아야 합니다. 실제 제한이 2초라면 로컬 최악 입력에서 1.6초에서 1.8초 정도에 끝나는 값을 쓰는 편이 안전합니다. 입출력, 최종 답 구성, 환경 차이 때문에 시간을 꽉 채우면 시간 초과가 날 수 있습니다.
