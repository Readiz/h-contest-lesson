// Runs the beam-search lesson's own code (Beam with state merging, estimate 1) on the same grids, as a cross-check for the compact planner.
#include <cstdio>
#include "lesson.cpp"

int main() {
    const int widths[3] = {16, 64, 256};
    for (int wi = 0; wi < 3; ++wi)
        for (int s = 1; s <= 20; ++s) printf("B5 %d %d %lld\n", widths[wi], s, solveGrid((unsigned long long)s, 1, widths[wi]));
    return 0;
}
