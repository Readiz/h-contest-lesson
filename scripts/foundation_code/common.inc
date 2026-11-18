// 로컬 검사 하네스 공통부: 제출용 강의 코드 뒤에 붙으므로 여기서만 표준 헤더를 쓴다.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

static long long harnessChecks = 0;
#define CHECK(cond) do { ++harnessChecks; if (!(cond)) { \
    std::fprintf(stderr, "CHECK failed %s:%d: %s\n", __FILE__, __LINE__, #cond); \
    std::abort(); } } while (0)

static std::mt19937_64 harnessRng(20261119);
static int rnd(int n) { return (int)(harnessRng() % (unsigned long long)n); } // [0, n)
