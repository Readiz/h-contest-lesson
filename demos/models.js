/* The same deterministic model runs in the browser and in Node's oracle checks. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.LessonDemos = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const copy = value => JSON.parse(JSON.stringify(value));
  function lowerBoundTrace(array, target) {
    let lo = 0, hi = array.length;
    const states = [{lo, hi, mid: null, phase: 'start', message: '미비교 원소는 [lo, hi), 답이 될 수 있는 위치는 [lo, hi]입니다. hi = n도 반환 가능한 위치입니다.'}];
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      states.push({lo, hi, mid, phase: 'compare', message: `a[${mid}] = ${array[mid]}와 target = ${target}을 비교합니다.`});
      if (array[mid] < target) {
        lo = mid + 1;
        states.push({lo, hi, mid: null, phase: 'move', message: `${array[mid]} < ${target}. mid까지는 답이 될 수 없으므로 lo = ${lo}로 옮깁니다.`});
      } else {
        hi = mid;
        states.push({lo, hi, mid: null, phase: 'move', message: `${array[mid]} ≥ ${target}. 더 왼쪽에도 답이 있을 수 있으므로 hi = ${hi}로 옮깁니다.`});
      }
    }
    states.push({lo, hi, mid: null, phase: 'done', message: lo === array.length ? `lo = hi = ${lo}. target 이상인 원소가 없으므로 끝 위치 n을 반환합니다.` : `lo = hi = ${lo}. target 이상인 첫 원소는 a[${lo}] = ${array[lo]}입니다. 같은 값이 여러 개여도 첫 위치를 찾습니다.`});
    return states;
  }
  const bfsExamples = [
    {name: '벽을 돌아가는 길', rows: ['S...#.', '.##.#.', '...#..', '.#....', '....#G']},
    {name: '도달할 수 없는 도착점', rows: ['S.....', '..##..', '..#G#.', '...#..', '......']}
  ];
  function bfsTrace(rows) {
    const h = rows.length, w = rows[0].length;
    const start = rows.join('').indexOf('S'), goal = rows.join('').indexOf('G');
    const distance = Array(w * h).fill(-1), parent = Array(w * h).fill(-1), queue = [start], states = [];
    distance[start] = 0;
    let current = null;
    const add = (phase, message, focus = null) => states.push(copy({phase, message, distance, parent, queue, current, focus, path: []}));
    add('start', '시작점을 큐에 넣으면서 visited를 표시합니다. distance = 0입니다.', start);
    while (queue.length) {
      current = queue.shift();
      add('pop', `큐 맨 앞 (${Math.floor(current / w)}, ${current % w})을 꺼냅니다. 거리 = ${distance[current]}.`);
      for (const [dr, dc] of [[0,1],[1,0],[0,-1],[-1,0]]) {
        const r = Math.floor(current / w) + dr, c = current % w + dc, next = r * w + c;
        if (r < 0 || r >= h || c < 0 || c >= w || rows[r][c] === '#' || distance[next] !== -1) continue;
        distance[next] = distance[current] + 1; parent[next] = current; queue.push(next);
        add('enqueue', `(${r}, ${c})을 처음 발견했습니다. visited 표시와 큐 삽입을 함께 합니다. 거리 = ${distance[next]}.`, next);
      }
    }
    current = null;
    add('done', distance[goal] < 0 ? '큐가 비었습니다. 도착점은 미방문 상태이므로 도달할 수 없습니다.' : `큐가 비었습니다. 도착점까지 최단 거리는 ${distance[goal]}입니다. parent를 역추적한 길을 표시합니다.`);
    if (distance[goal] >= 0) { let v = goal; while (v !== -1) { states.at(-1).path.unshift(v); v = parent[v]; } }
    return states;
  }
  const graph = {nodes: ['S','A','B','C','D'], points: [[48,124],[155,44],[155,206],[292,65],[292,188]], edges: [[0,1,7],[0,2,2],[2,1,1],[1,3,2],[2,3,8],[2,4,9],[3,4,1]]};
  function dijkstraTrace(g = graph, source = 0) {
    const distance = Array(g.nodes.length).fill(null), settled = Array(g.nodes.length).fill(false), queue = [], states = [];
    distance[source] = 0; queue.push([0,source]);
    let current = null, edge = null, popped = null;
    const add = (phase, message) => states.push(copy({phase, message, distance, settled, queue: [...queue].sort((a,b) => a[0]-b[0] || a[1]-b[1]), current, edge, popped}));
    add('start', `시작점 ${g.nodes[source]}의 거리를 0으로 두고 (0, ${g.nodes[source]})를 최소 우선순위 큐에 넣습니다.`);
    while (queue.length) {
      queue.sort((a,b) => a[0]-b[0] || a[1]-b[1]);
      const [d,v] = queue.shift(); current = v; popped = [d,v]; edge = null;
      if (distance[v] !== d) { add('stale', `(${d}, ${g.nodes[v]})는 오래된 항목입니다. 최신 dist[${g.nodes[v]}] = ${distance[v]}와 다르므로 간선을 보지 않고 건너뜁니다.`); continue; }
      settled[v] = true;
      add('pop', `(${d}, ${g.nodes[v]})를 꺼냈습니다. 최신 거리와 같으므로 ${g.nodes[v]}에서 나가는 간선을 확인합니다.`);
      g.edges.forEach(([a,b,weight], index) => {
        if (a !== v) return;
        edge = index;
        const next = d + weight, old = distance[b];
        if (old === null || next < old) {
          distance[b] = next; queue.push([next,b]);
          add('relax', `${g.nodes[a]} → ${g.nodes[b]}: ${d} + ${weight} = ${next}. dist를 ${old === null ? '∞' : old} → ${next}로 갱신하고 새 항목을 넣습니다.`);
        } else add('skip', `${g.nodes[a]} → ${g.nodes[b]}의 후보 ${next}는 현재 거리 ${old}보다 작지 않습니다. 갱신하지 않습니다.`);
      });
    }
    current = null; edge = null; popped = null;
    add('done', '큐가 비었습니다. 오래된 항목은 버렸고, 각 정점의 최단 거리가 남았습니다.');
    return states;
  }
  const matrix = [[2,1,4,2,3],[3,5,1,6,2],[1,2,7,3,4],[4,3,2,1,5]];
  function prefixTable(a) {
    const p = Array.from({length:a.length+1}, () => Array(a[0].length+1).fill(0));
    for (let r=1;r<p.length;r++) for(let c=1;c<p[0].length;c++) p[r][c]=a[r-1][c-1]+p[r-1][c]+p[r][c-1]-p[r-1][c-1];
    return p;
  }
  function prefixTrace(a, rectangle) {
    const [r1,c1,r2,c2] = rectangle, p = prefixTable(a);
    const terms = [[1,r2,c2],[-1,r1,c2],[-1,r2,c1],[1,r1,c1]], states=[];
    const coefficient = a.map(row => row.map(() => 0)); let total=0;
    const messages = ['선택 영역은 행 [r1, r2), 열 [c1, c2)입니다. 누적합 P[r][c]는 왼쪽 위 r×c 영역의 합입니다.', '먼저 오른쪽 아래까지의 큰 직사각형을 더합니다.', '선택 영역 위쪽을 뺍니다.', '선택 영역 왼쪽을 뺍니다. 왼쪽 위 겹침이 있으면 두 번 빠져 계수가 −1이 됩니다.', '왼쪽 위 겹침을 한 번 돌려놓습니다. 선택 영역만 계수 1로 남습니다.'];
    states.push(copy({phase:'start', term:null, total, coefficient, message:messages[0]}));
    terms.forEach(([sign,r,c],i) => {
      for(let y=0;y<r;y++) for(let x=0;x<c;x++) coefficient[y][x]+=sign;
      total+=sign*p[r][c];
      states.push(copy({phase:i===3?'done':'term', term:i, total, coefficient, message:messages[i+1]}));
    });
    return {states, p, terms};
  }
  const routes = [
    {name:'열린 경로의 꼬리 뒤집기', points:[[0,0],[1,0],[9,0],[8,0],[2,0]], order:[0,1,2,3,4], left:2, right:4},
    {name:'두 경계가 바뀌는 구간', points:[[0,0],[1,4],[7,1],[2,5],[8,5],[9,0]], order:[0,1,2,3,4,5], left:2, right:3},
    {name:'개선되지 않아 거절하는 구간', points:[[0,0],[2,1],[4,1],[6,2],[8,2]], order:[0,1,2,3,4], left:1, right:2}
  ];
  const manhattan = (a,b) => Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);
  const pathCost = (points,order) => order.slice(1).reduce((sum,v,i) => sum+manhattan(points[order[i]],points[v]),0);
  function twoOpt(points, order, left, right) {
    if(left<1 || right>=order.length || left>right) throw new RangeError('fixed origin requires 1 <= left <= right < n');
    const a=order[left-1], b=order[left], c=order[right], d=order[right+1];
    const removed=[[a,b]], added=[[a,c]];
    if(d!==undefined) { removed.push([c,d]); added.push([b,d]); }
    const sum=edges=>edges.reduce((v,[x,y])=>v+manhattan(points[x],points[y]),0);
    const before=sum(removed), after=sum(added), candidate=[...order.slice(0,left),...order.slice(left,right+1).reverse(),...order.slice(right+1)];
    return {before,after,delta:after-before,candidate,removed,added,oldCost:pathCost(points,order),newCost:pathCost(points,candidate)};
  }
  function twoOptTrace(points,order,left,right) {
    const result=twoOpt(points,order,left,right), tail=right===order.length-1;
    const messages=[`order[${left}..${right}]를 뒤집습니다. 창고 0은 고정하고 마지막 점에서 돌아오지 않습니다.`, `기존 경계 ${tail?'하나':'두 개'}의 비용 합은 ${result.before}입니다. 구간 내부 간선 비용은 뒤집어도 같습니다.`, `새 경계 비용은 ${result.after}. Δ = after − before = ${result.delta}입니다. ${tail?'꼬리에는 오른쪽 바깥 간선이 없습니다.':''}`, `구간을 실제로 뒤집은 후보입니다. 전체 비용 ${result.oldCost} → ${result.newCost}; 전체 재계산의 차이도 ${result.delta}입니다.`, result.delta<0?'Δ < 0이므로 개선 후보를 채택합니다.':'Δ ≥ 0이므로 엄격한 개선만 받는 지역 탐색에서는 기존 경로를 유지합니다.'];
    return messages.map((message,i)=>({...result,phase:['start','remove','add','candidate','done'][i],message,order:i===3 || (i===4 && result.delta<0)?result.candidate:order}));
  }
  function acceptance(delta,temperature) {
    if(delta<=0) return 1;
    if(temperature<=0) return 0;
    return Math.exp(-delta/temperature);
  }
  const annealingPlotMax = deltaScale => Math.max(30, Math.ceil(Math.round(1.8 * deltaScale) / 10) * 10);
  function annealingTrace(temperature,deltaScale=6) {
    const deltas=[-5,1.0,-3,1.5,-8,0.6,-2,1.2,-7,0.8,-4,1.8];
    const draws=[0.42,0.25,0.72,0.86,0.14,0.12,0.61,0.48,0.07,0.15,0.31,0.93];
    let current=50,best=50; const history=[{current,best}],states=[];
    states.push({phase:'start',current,best,candidate:null,delta:null,probability:null,draw:null,temperature,accepted:null,history:copy(history),message:'최소화 문제입니다. current는 탐색 중인 비용, best는 지금까지 발견한 최저 비용입니다. 같은 제안·난수로 온도만 바꿔 비교할 수 있습니다.'});
    deltas.forEach((d,i)=>{
      const delta=d>0?Math.round(d*deltaScale):d, candidate=current+delta, t=temperature*Math.pow(0.88,i), p=acceptance(delta,t), accepted=draws[i]<p;
      if(accepted) current=candidate;
      best=Math.min(best,current); history.push({current,best});
      states.push({phase:i===deltas.length-1?'done':'trial',current,best,candidate,delta,probability:p,draw:draws[i],temperature:t,accepted,history:copy(history),message:`제안 ${i+1}: Δ = ${delta>0?'+':''}${delta}, P = ${(p*100).toFixed(1)}%, u = ${draws[i].toFixed(2)}. ${accepted?'u < P이므로 수락':'u ≥ P이므로 거절'}합니다. ${accepted&&delta>0?'current는 나빠져도 best는 보존합니다.':'best는 더 작은 비용을 발견했을 때만 갱신합니다.'}`});
    });
    return states;
  }
  // ---- nearest neighbor: construct an open route from warehouse 0 ----
  const nnExamples = [
    {name:'가까운 점을 먼저 쓰면 멀리 남는 점', points:[[0,0],[2,1],[4,0],[6,1],[-3,1]]},
    {name:'같은 거리는 번호가 작은 점', points:[[0,0],[3,0],[0,3],[4,4],[1,5]]},
    {name:'선택이 그대로 잘 맞는 경우', points:[[0,0],[1,1],[2,2],[4,2],[5,3]]}
  ];
  function nearestNeighborTrace(points) {
    const n = points.length, used = Array(n).fill(false), order = [0], states = [];
    used[0] = true;
    let cost = 0, current = 0;
    const base = () => ({order: [...order], used: [...used], cost, current, candidates: [], chosen: null});
    states.push(copy({...base(), phase: 'start', message: '창고 0에서 시작합니다. 매 단계 현재 점에서 가장 가까운 미방문 점을 고르고, 마지막 점에서 창고로 돌아오는 비용은 없습니다.'}));
    while (order.length < n) {
      const candidates = [];
      for (let v = 1; v < n; v++) if (!used[v]) candidates.push({v, dist: manhattan(points[current], points[v])});
      let chosen = candidates[0];
      for (const c of candidates) if (c.dist < chosen.dist) chosen = c;
      const ties = candidates.filter(c => c.dist === chosen.dist).length;
      states.push(copy({...base(), phase: 'scan', candidates, chosen: chosen.v, message: `점 ${current}에서 후보 거리: ${candidates.map(c => `${c.v}번 ${c.dist}`).join(', ')}. 최솟값 ${chosen.dist}${ties > 1 ? `가 ${ties}개 같아 번호가 작은 ${chosen.v}번을 고릅니다` : `인 ${chosen.v}번을 고릅니다`}.`}));
      used[chosen.v] = true; order.push(chosen.v); cost += chosen.dist; const from = current; current = chosen.v;
      const last = order.length === n;
      states.push(copy({...base(), phase: last ? 'done' : 'visit', lastLeg: chosen.dist, message: `${from} → ${chosen.v}로 이동합니다. 누적 비용 = ${cost - chosen.dist} + ${chosen.dist} = ${cost}.${last ? '' : ` 남은 점 ${n - order.length}개.`}`}));
    }
    const optimal = optimalOpenRoute(points);
    states[states.length - 1].message += ` 모든 순서를 비교한 최적 비용은 ${optimal.cost}이므로 ${cost === optimal.cost ? '이 경로는 최적입니다.' : `nearest neighbor 경로는 ${cost - optimal.cost}만큼 더 깁니다. 가까운 점을 먼저 소비해 멀리 남은 점을 마지막에 길게 이동했습니다.`}`;
    states.at(-1).optimal = optimal;
    return states;
  }
  function optimalOpenRoute(points) {
    const n = points.length; let best = {cost: Infinity, order: null};
    const walk = (order, left) => {
      if (!left.length) { const c = pathCost(points, order); if (c < best.cost) best = {cost: c, order: [...order]}; return; }
      left.forEach((v, i) => walk([...order, v], [...left.slice(0, i), ...left.slice(i + 1)]));
    };
    walk([0], [...Array(n - 1)].map((_, i) => i + 1));
    return best;
  }
  // ---- beam search on a small decision tree (3 choices x 3 depths) ----
  const beamExamples = [
    {name:'W=2부터 최적 경로를 찾는 트리', g0:[7,6,3], g1:[[2,9,9],[4,8,2],[8,8,7]], g2:[[[2,2,5],[4,6,1],[8,7,6]],[[2,3,9],[7,5,2],[2,7,8]],[[9,8,2],[3,5,4],[6,4,3]]]},
    {name:'W=3이 되어야 최적 경로를 찾는 트리', g0:[7,1,9], g1:[[8,6,1],[9,2,4],[4,4,6]], g2:[[[6,6,2],[1,9,4],[3,5,9]],[[6,4,6],[4,4,5],[8,3,8]],[[8,7,4],[2,1,6],[1,3,5]]]}
  ];
  const beamGain = (tree, path) => path.length === 1 ? tree.g0[path[0]] : path.length === 2 ? tree.g1[path[0]][path[1]] : tree.g2[path[0]][path[1]][path[2]];
  const comparePath = (a, b) => { for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return a[i] - b[i]; return 0; };
  function beamSearchTrace(tree, width) {
    let layer = [{path: [], score: 0, gain: 0}];
    const layers = [layer.map(n => ({...n, kept: true}))];
    const states = [copy({phase: 'start', depth: 0, width, layers, candidates: [], message: `깊이 0의 상태 하나에서 시작합니다. 매 깊이마다 모든 후보를 만들고 평가값(누적 점수)이 큰 상위 W = ${width}개만 남깁니다.`})];
    for (let depth = 1; depth <= 3; depth++) {
      const candidates = [];
      layer.forEach((node, parent) => { for (let k = 0; k < 3; k++) { const path = [...node.path, k], gain = beamGain(tree, path); candidates.push({path, parent, gain, score: node.score + gain}); } });
      const open = candidates.map(c => ({...c, kept: null}));
      states.push(copy({phase: 'expand', depth, width, layers: [...layers, open], candidates: open, message: `깊이 ${depth}: 남은 상태 ${layer.length}개에서 후보 ${candidates.length}개를 만들었습니다. 아직 평가값만 계산했고 버린 후보는 없습니다.`}));
      const ranked = [...candidates].sort((a, b) => b.score - a.score || comparePath(a.path, b.path));
      const keep = new Set(ranked.slice(0, width).map(c => c.path.join(',')));
      const marked = candidates.map(c => ({...c, kept: keep.has(c.path.join(','))}));
      layer = ranked.slice(0, width);
      layers.push(marked);
      const droppedList = marked.filter(c => !c.kept);
      states.push(copy({phase: depth === 3 ? 'done' : 'prune', depth, width, layers: [...layers], candidates: marked, message: `평가값 상위 ${layer.length}개(${layer.map(c => c.score).join(', ')})를 남기고 ${droppedList.length}개를 버립니다.${droppedList.length ? ` 버린 후보의 최고 평가값은 ${Math.max(...droppedList.map(c => c.score))}입니다.` : ' 버린 후보가 없습니다.'}`}));
    }
    const best = layer[0], optimum = optimalBeamLeaf(tree), last = states.at(-1);
    last.best = {path: best.path, score: best.score}; last.optimum = optimum;
    last.message += ` 최종 경로 ${best.path.join('-')}의 점수는 ${best.score}, 모든 경로의 최댓값은 ${optimum.score}(${optimum.path.join('-')})이므로 ${best.score === optimum.score ? `W = ${width}에서 최적을 찾았습니다.` : `W = ${width}에서는 최적 경로를 놓쳤습니다.`}`;
    return states;
  }
  function optimalBeamLeaf(tree) {
    let best = {score: -Infinity, path: null};
    for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) for (let c = 0; c < 3; c++) { const score = tree.g0[a] + tree.g1[a][b] + tree.g2[a][b][c]; if (score > best.score) best = {score, path: [a, b, c]}; }
    return best;
  }
  // ---- destroy / repair on a one-dimensional strip ----
  const drItems = {A:{w:2,v:3},B:{w:2,v:3},C:{w:4,v:9},D:{w:1,v:1},E:{w:3,v:2}};
  const DR_LENGTH = 10;
  const drExamples = [
    {name:'큰 제거로 막힌 배치 고치기', strategy:'density', place:{A:1,B:5,D:9}, trials:[['D'],['A','B']]},
    {name:'나빠진 repair는 되돌리기', strategy:'narrow', place:{C:0,A:4,B:6}, trials:[['C'],['A','B']]}
  ];
  const drScore = place => Object.keys(place).reduce((s, id) => s + drItems[id].v, 0);
  function drSlots(place) { const slots = Array(DR_LENGTH).fill(null); for (const [id, at] of Object.entries(place)) for (let i = at; i < at + drItems[id].w; i++) slots[i] = id; return slots; }
  function drRepair(place, pool, strategy) {
    const next = {...place}, log = [];
    const order = [...pool].sort((a, b) => strategy === 'density' ? drItems[b].v / drItems[b].w - drItems[a].v / drItems[a].w || (a < b ? -1 : 1) : drItems[a].w - drItems[b].w || (a < b ? -1 : 1));
    for (const id of order) {
      const slots = drSlots(next), w = drItems[id].w; let at = -1;
      for (let s = 0; s + w <= DR_LENGTH && at < 0; s++) if (slots.slice(s, s + w).every(x => x === null)) at = s;
      if (at >= 0) { next[id] = at; log.push(`${id}는 ${at}번 칸부터 배치`); } else log.push(`${id}는 들어갈 빈 구간이 없어 건너뜀`);
    }
    return {place: next, order, log};
  }
  function destroyRepairTrace(example) {
    let current = {...example.place}; const states = [], names = {density:'가치/폭이 큰 순서', narrow:'폭이 좁은 순서'};
    const snap = extra => states.push(copy({strategy: example.strategy, trials: example.trials.length, current, currentScore: drScore(current), ...extra}));
    snap({phase: 'start', working: current, workingScore: drScore(current), removed: [], trial: 0, message: `${DR_LENGTH}칸 띠에 광고를 놓습니다. 현재 점수는 ${drScore(current)}입니다. 한 개를 옮기는 작은 이동으로는 막힌 배치를 고치기 어렵습니다. 일부를 제거하고 ${names[example.strategy]}로 다시 채웁니다.`});
    example.trials.forEach((removed, index) => {
      const trial = index + 1, before = drScore(current), working = {...current};
      removed.forEach(id => delete working[id]);
      snap({phase: 'destroy', working, workingScore: drScore(working), removed, trial, message: `시도 ${trial}: ${removed.join(', ')} 제거. 점수 ${before} → ${drScore(working)}, 내려갑니다.`});
      const pool = Object.keys(drItems).filter(id => !(id in working));
      const repaired = drRepair(working, pool, example.strategy), after = drScore(repaired.place);
      snap({phase: 'repair', working: repaired.place, workingScore: after, removed, trial, repairOrder: repaired.order, message: `${names[example.strategy]}로 ${repaired.order.join(' → ')}를 다시 채웁니다. ${repaired.log.join(', ')}. 점수 ${after}.`});
      const accept = after > before;
      if (accept) current = repaired.place;
      snap({phase: 'judge', working: current, workingScore: drScore(current), removed, trial, accepted: accept, message: accept ? `점수 ${before} → ${after}, 좋아졌으므로 새 배치를 채택합니다.` : `점수 ${before} → ${after}, 좋아지지 않았으므로 제거 전 배치로 되돌립니다.`});
    });
    states.at(-1).phase = 'done';
    states.at(-1).message += ` 모든 시도가 끝났습니다. 최종 점수 ${drScore(current)}.`;
    return states;
  }
  // ---- paired comparison of two solvers ----
  const pairedExamples = [
    {name:'A가 안정적으로 좋은 경우', a:[1052,988,1130,1015,970,1204,1096,934,1170,1008,1087,1121,975,1063,1149,1002,1038,1190,964,1077,1112,1025,1004,1141,958,1099,1068,1033,1176,1018], b:[1040,975,1118,1010,988,1189,1091,933,1160,1012,1076,1108,972,1054,1138,990,1031,1175,952,1070,1101,1020,998,1129,949,1093,1055,1027,1161,1009]},
    {name:'차이가 0 근처에서 흔들리는 경우', a:[1052,988,1130,1015,970,1204,1096,934,1170,1008,1087,1121,975,1063,1149,1002,1038,1190,964,1077,1112,1025,1004,1141,958,1099,1068,1033,1176,1018], b:[1040,1010,1090,1004,985,1171,1118,951,1161,1031,1064,1109,990,1071,1133,1027,1020,1200,979,1066,1101,1042,1011,1124,972,1088,1074,1041,1151,1020]}
  ];
  function pairedStats(diffs) {
    const n = diffs.length, mean = diffs.reduce((s, d) => s + d, 0) / n;
    if (n < 2) return {n, mean, std: null, stderr: null, low: null, high: null, verdict: 'insufficient'};
    const std = Math.sqrt(diffs.reduce((s, d) => s + (d - mean) * (d - mean), 0) / (n - 1)), stderr = std / Math.sqrt(n);
    const low = mean - 2 * stderr, high = mean + 2 * stderr;
    return {n, mean, std, stderr, low, high, verdict: low > 0 ? 'better' : high < 0 ? 'worse' : 'unclear'};
  }
  const signedInt = v => v > 0 ? `+${v}` : String(v);
  function pairedTrace(example, count) {
    const diffs = example.a.map((x, i) => x - example.b[i]).slice(0, count), states = [];
    const verdictText = {insufficient: '표본이 하나라 표준오차를 계산할 수 없습니다.', better: '구간 전체가 0보다 커서 A가 좋아졌다는 근거입니다.', worse: '구간 전체가 0보다 작아서 A가 나빠졌다는 근거입니다.', unclear: '구간이 0을 포함하므로 이 표본만으로 어느 쪽이 좋은지 확정하지 않습니다.'};
    const f = v => (Math.round(v * 100) / 100).toFixed(2);
    for (let k = 0; k <= diffs.length; k++) {
      const used = diffs.slice(0, k), stats = k === 0 ? {n: 0, mean: null, std: null, stderr: null, low: null, high: null, verdict: 'empty'} : pairedStats(used);
      const message = k === 0 ? `입력 ${count}개에서 A와 B의 점수 차이 d = A − B를 하나씩 쌓습니다. 점수가 클수록 좋은 문제입니다.` : `입력 ${k}: A ${example.a[k - 1]}, B ${example.b[k - 1]}, d = ${signedInt(diffs[k - 1])}. 평균 ${f(stats.mean)}${stats.stderr === null ? '. ' + verdictText[stats.verdict] : `, 표준오차 ${f(stats.stderr)}, 구간 [${f(stats.low)}, ${f(stats.high)}]. ${verdictText[stats.verdict]}`}`;
      states.push({phase: k === 0 ? 'start' : k === diffs.length ? 'done' : 'sample', k, diffs: used, stats, message});
    }
    return states;
  }
  // ---- union-find: naive links vs. path compression, side by side ----
  const ufExamples = [
    {name:'사슬을 만든 뒤 경로 압축', n:8, ops:[['union',0,1],['union',1,2],['union',2,3],['union',3,4],['find',0],['find',0],['union',5,6],['union',4,6]]},
    {name:'여러 집합을 합치고 질의하기', n:8, ops:[['union',0,1],['union',2,3],['union',1,3],['union',4,5],['find',0],['union',5,0],['find',3],['union',6,7]]}
  ];
  function ufFind(parent, x, compress) {
    const path = [x];
    while (parent[x] !== x) { x = parent[x]; path.push(x); }
    if (compress) for (const v of path.slice(0, -1)) parent[v] = x;
    return {root: x, path};
  }
  const ufDepth = parent => parent.map((_, v) => { let d = 0, x = v; while (parent[x] !== x) { x = parent[x]; d++; } return d; });
  function unionFindTrace(example) {
    const plain = Array.from({length: example.n}, (_, i) => i), packed = [...plain], states = [];
    const add = (phase, message, op, extra = {}) => states.push(copy({phase, message, op, plain, packed, plainDepth: Math.max(...ufDepth(plain)), packedDepth: Math.max(...ufDepth(packed)), path: null, ...extra}));
    add('start', `원소 ${example.n}개가 각각 대표인 집합으로 시작합니다. 같은 연산을 경로 압축 없는 숲(왼쪽)과 있는 숲(오른쪽)에 적용합니다. union은 parent[a의 대표] = b의 대표로 연결합니다.`, null);
    example.ops.forEach(([kind, a, b], i) => {
      const p = ufFind(plain, a, false), q = ufFind(packed, a, true);
      if (kind === 'find') {
        add('find', `find(${a}): 압축 없음은 ${p.path.join(' → ')}(${p.path.length - 1}칸)를 따라갑니다. 압축 있음은 같은 길을 지난 뒤 지나온 점의 부모를 대표 ${q.root}로 바꿉니다.`, i + 1, {path: {plain: p.path, packed: q.path}});
      } else {
        const pb = ufFind(plain, b, false), qb = ufFind(packed, b, true), merged = p.root !== pb.root;
        if (merged) { plain[p.root] = pb.root; packed[q.root] = qb.root; }
        add('union', `union(${a}, ${b}): 대표는 ${p.root}와 ${pb.root}. ${merged ? `${p.root}의 부모를 ${pb.root}로 바꿔 두 집합을 합칩니다.` : '이미 같은 대표이므로 합치지 않습니다.'} 압축 있음은 find 중 지나온 점의 부모를 대표로 정리했습니다.`, i + 1, {path: {plain: [...p.path, ...pb.path], packed: [...q.path, ...qb.path]}});
      }
    });
    states.at(-1).phase = 'done';
    states.at(-1).message += ` 모든 연산이 끝났습니다. 가장 깊은 노드: 압축 없음 ${states.at(-1).plainDepth}칸, 압축 있음 ${states.at(-1).packedDepth}칸.`;
    return states;
  }
  // ---- segment tree: range sum queries and point updates ----
  const segExamples = [
    {name:'구간 합 [1, 5]', kind:'query', left:1, right:5},
    {name:'구간 합 [4, 7] · 한쪽만 걸침', kind:'query', left:4, right:7},
    {name:'점 갱신 a[4] = 9', kind:'update', index:4, value:9}
  ];
  const segArray = [5, 3, 8, 6, 2, 7, 4, 1];
  function segBuild(array) {
    const tree = Array(4 * array.length).fill(0);
    const build = (node, lo, hi) => { if (lo === hi) { tree[node] = array[lo]; return; } const mid = (lo + hi) >> 1; build(2 * node, lo, mid); build(2 * node + 1, mid + 1, hi); tree[node] = tree[2 * node] + tree[2 * node + 1]; };
    build(1, 0, array.length - 1);
    return tree;
  }
  function segmentTrace(array, example) {
    const n = array.length, a = [...array], tree = segBuild(a), states = [], nodes = [];
    const collect = (node, lo, hi) => { nodes.push({node, lo, hi}); if (lo < hi) { const mid = (lo + hi) >> 1; collect(2 * node, lo, mid); collect(2 * node + 1, mid + 1, hi); } };
    collect(1, 0, n - 1);
    const snap = (phase, message, extra = {}) => states.push(copy({phase, message, nodes, tree, array: a, kind: example.kind, visited: [], current: null, ...extra}));
    if (example.kind === 'query') {
      const {left, right} = example, visited = [];
      let total = 0;
      snap('start', `a[${left}..${right}]의 합을 구합니다. 각 노드의 구간 [lo, hi]를 질의 구간과 비교해 무관하면 0, 완전히 포함되면 저장된 합, 일부만 겹치면 두 자식으로 내려갑니다.`, {left, right, total});
      const walk = (node, lo, hi) => {
        const kind = hi < left || right < lo ? 'outside' : left <= lo && hi <= right ? 'inside' : 'partial';
        if (kind === 'inside') total += tree[node];
        visited.push({node, kind, value: kind === 'inside' ? tree[node] : 0});
        const text = {outside: '질의 구간과 겹치지 않으므로 0을 반환합니다.', inside: `질의 구간에 완전히 들어가므로 tree[${node}] = ${tree[node]}를 반환합니다. 누적 ${total}.`, partial: '일부만 겹치므로 두 자식으로 내려갑니다.'}[kind];
        snap(kind, `노드 ${node} [${lo}, ${hi}]: ${text}`, {left, right, total, visited, current: node});
        if (kind === 'partial') { const mid = (lo + hi) >> 1; walk(2 * node, lo, mid); walk(2 * node + 1, mid + 1, hi); }
      };
      walk(1, 0, n - 1);
      states.push(copy({...states.at(-1), phase: 'done', current: null, message: `방문한 노드 ${visited.length}개. 완전 포함 노드의 합을 더해 a[${left}..${right}] = ${total}입니다.`}));
    } else {
      const {index, value} = example, path = [], before = tree[1];
      snap('start', `a[${index}]를 ${a[index]}에서 ${value}로 바꿉니다. 이 위치를 포함하는 노드만 다시 계산합니다.`, {index, path});
      const walk = (node, lo, hi) => {
        path.push(node);
        if (lo === hi) { a[index] = value; tree[node] = value; snap('point', `리프 ${node} [${lo}, ${hi}]의 값을 ${value}로 바꿉니다.`, {index, path, current: node}); return; }
        const mid = (lo + hi) >> 1;
        snap('node', `노드 ${node} [${lo}, ${hi}]는 index ${index}를 포함하므로 ${index <= mid ? '왼쪽' : '오른쪽'} 자식으로 내려갑니다.`, {index, path, current: node});
        if (index <= mid) walk(2 * node, lo, mid); else walk(2 * node + 1, mid + 1, hi);
        const old = tree[node]; tree[node] = tree[2 * node] + tree[2 * node + 1];
        snap('recalc', `돌아오며 tree[${node}] = tree[${2 * node}] + tree[${2 * node + 1}] = ${tree[node]}로 다시 계산합니다(이전 ${old}).`, {index, path, current: node});
      };
      walk(1, 0, n - 1);
      states.push(copy({...states.at(-1), phase: 'done', current: null, message: `경로의 노드 ${path.length}개만 고쳤습니다. 전체 합 ${before} → ${tree[1]}.`}));
    }
    return states;
  }
  // Korean particle chosen by the last character's final consonant (digits are read as Korean numerals).
  const jo = (word, withFinal, without) => { const text = String(word), c = text.slice(-1), code = c.charCodeAt(0); const final = /[0-9]/.test(c) ? '013678'.includes(c) : code >= 0xac00 && code <= 0xd7a3 ? (code - 0xac00) % 28 !== 0 : /[LMNRlmnr]/.test(c); return text + (final ? withFinal : without); };
  // ---- assignment moves: one-job moves and two-job swaps on a makespan objective ----
  const amTime = [[8,9],[1,3],[1,5],[6,9],[1,6]];
  const amExamples = [{name:'작업 5개 · 기계 2개 · 본문 손계산', time:amTime, start:[0,1,1,0,1]}];
  const amLoads = (time, assign) => { const load = Array(time[0].length).fill(0); assign.forEach((m, j) => { load[m] += time[j][m]; }); return load; };
  // Neighbors use differential loads (only the touched machines change), like the lesson's tryMove/trySwap.
  function amNeighbors(time, assign) {
    const load = amLoads(time, assign), m = time[0].length, n = assign.length, out = [];
    const push = (nb, a, b, loadA, loadB) => { const loads = [...load]; loads[a] = loadA; loads[b] = loadB; out.push({...nb, loads, makespan: Math.max(...loads)}); };
    for (let j = 0; j < n; j++) for (let k = 0; k < m; k++) if (k !== assign[j]) {
      const from = assign[j], next = [...assign]; next[j] = k;
      push({kind:'move', label:`작업 ${j} → 기계 ${k}`, assign:next, job:j, to:k, changed:[j]}, from, k, load[from] - time[j][from], load[k] + time[j][k]);
    }
    for (let x = 0; x < n; x++) for (let y = x + 1; y < n; y++) if (assign[x] !== assign[y]) {
      const a = assign[x], b = assign[y], next = [...assign]; next[x] = b; next[y] = a;
      push({kind:'swap', label:`작업 ${x} ↔ 작업 ${y}`, assign:next, x, y, changed:[x, y]}, a, b, load[a] - time[x][a] + time[y][a], load[b] - time[y][b] + time[x][b]);
    }
    return out;
  }
  function amOptimum(time) {
    const n = time.length, m = time[0].length;
    let best = Infinity, assign = null;
    for (let code = 0; code < Math.pow(m, n); code++) {
      const a = []; let c = code; for (let j = 0; j < n; j++) { a.push(c % m); c = Math.floor(c / m); }
      const value = Math.max(...amLoads(time, a));
      if (value < best) { best = value; assign = a; }
    }
    return {makespan: best, assign};
  }
  function assignmentMovesTrace(example, mode, worseJob) {
    const time = example.time, states = [], optimum = amOptimum(time).makespan;
    let assign = [...example.start], used = false, changed = [];
    const peak = a => Math.max(...amLoads(time, a));
    const snap = (phase, message, extra = {}) => states.push(copy({phase, message, assign, changed, loads: amLoads(time, assign), makespan: peak(assign), optimum, mode, neighbors: [], evaluated: 0, current: null, picked: null, ...extra}));
    snap('start', `작업 ${assign.length}개를 기계 ${time[0].length}대에 배정한 상태입니다. 점수는 기계별 부하의 최댓값입니다. 이웃(한 작업 이동, 두 작업 교환)을 하나씩 계산해 봅니다.`);
    for (let round = 1; round <= 40; round++) {
      const neighbors = amNeighbors(time, assign), now = peak(assign);
      neighbors.forEach((nb, i) => snap('scan', `이웃 ${i + 1} / ${neighbors.length}: ${nb.label}. 부하 ${nb.loads.join(' · ')}, 최대 ${nb.makespan}${nb.makespan < now ? ` (현재 ${now}보다 낮음)` : nb.makespan === now ? ' (현재와 같음)' : ` (현재 ${now}보다 ${nb.makespan - now} 나쁨)`}.`, {neighbors, evaluated: i + 1, current: i}));
      let best = 0; neighbors.forEach((nb, i) => { if (nb.makespan < neighbors[best].makespan) best = i; });
      if (neighbors.length && neighbors[best].makespan < now) {
        const nb = neighbors[best]; assign = nb.assign; changed = nb.changed;
        snap('accept', `가장 낮은 이웃은 ${nb.label}로 최대 ${nb.makespan}입니다. 현재 ${now}보다 낮으므로 받아들입니다.`, {neighbors, evaluated: neighbors.length, picked: best});
      } else if (mode === 'allow' && !used && neighbors.length) {
        let pick = neighbors.findIndex(nb => nb.kind === 'move' && nb.job === worseJob);
        if (pick < 0) { pick = 0; neighbors.forEach((nb, i) => { if (nb.makespan < neighbors[pick].makespan) pick = i; }); }
        const nb = neighbors[pick]; assign = nb.assign; changed = nb.changed; used = true;
        snap('worsen', `개선하는 이웃이 없습니다. 한 번만 나빠지는 이동을 허용해 ${jo(nb.label, '을', '를')} 받아들입니다. 최대 ${now} → ${nb.makespan}. 이 뒤로는 다시 개선만 받습니다.`, {neighbors, evaluated: neighbors.length, picked: pick});
      } else {
        snap('done', `모든 이웃이 현재 ${now}보다 낮지 않아 멈춥니다. 전수 탐색의 최솟값은 ${optimum}이므로 ${now === optimum ? '최적에 닿았습니다.' : `${now - optimum}만큼 모자랍니다.`}`, {neighbors, evaluated: neighbors.length});
        break;
      }
    }
    return states;
  }
  // ---- route insertion: where to put a passenger in another driver's route ----
  const riDrivers = [[2,7],[9,2]];
  const riPassengers = [{s:[8,7],e:[7,11]},{s:[11,5],e:[7,4]},{s:[4,7],e:[6,2]},{s:[1,6],e:[8,2]}];
  const riStart = [[2,0],[1,3]];
  const riExamples = riPassengers.map((_, i) => ({name:`승객 ${i}을 다른 기사에게 옮기기${i === 3 ? ' · 본문 예시' : ''}`, passenger:i}));
  function riLoad(driver, route) {
    const segments = []; let at = riDrivers[driver];
    for (const p of route) {
      const q = riPassengers[p];
      segments.push({kind:'empty', length:manhattan(at, q.s), passenger:p}, {kind:'ride', length:manhattan(q.s, q.e), passenger:p});
      at = q.e;
    }
    const sum = kind => segments.filter(s => s.kind === kind).reduce((a, s) => a + s.length, 0);
    return {segments, ride: sum('ride'), empty: sum('empty'), total: sum('ride') + sum('empty')};
  }
  function routeInsertionTrace(passenger) {
    const states = [], routes = copy(riStart), owner = routes.findIndex(r => r.includes(passenger)), other = 1 - owner;
    const maxOf = shown => Math.max(riLoad(0, shown[0]).total, riLoad(1, shown[1]).total), startMax = maxOf(routes);
    const snap = (phase, message, shown, extra = {}) => states.push(copy({phase, message, routes: shown, loads: shown.map((r, d) => riLoad(d, r)), startMax, passenger, owner, other, candidates: [], candidate: null, ...extra}));
    snap('start', `기사 0의 경로는 ${routes[0].join(' → ')}, 기사 1의 경로는 ${routes[1].join(' → ')}입니다. 부하는 ${jo(riLoad(0, routes[0]).total, '과', '와')} ${riLoad(1, routes[1]).total}이고 점수는 큰 쪽인 ${startMax}입니다. ${jo('승객 ' + passenger, '을', '를')} 기사 ${other}에게 옮겨 봅니다.`, routes);
    const removed = copy(routes); removed[owner] = routes[owner].filter(p => p !== passenger);
    snap('detach', `${jo('승객 ' + passenger, '을', '를')} 기사 ${owner}의 경로에서 빼면 기사 ${owner}의 부하가 ${riLoad(owner, removed[owner]).total}으로 줄어듭니다. 이제 기사 ${other}의 경로 어디에 끼울지 정해야 합니다.`, removed);
    const candidates = [];
    for (let pos = 0; pos <= routes[other].length; pos++) {
      const next = copy(removed); next[other] = [...routes[other].slice(0, pos), passenger, ...routes[other].slice(pos)];
      const where = pos === 0 ? '맨 앞' : pos === routes[other].length ? '맨 끝' : `승객 ${routes[other][pos - 1]} 뒤`, max = maxOf(next), l = next.map((r, d) => riLoad(d, r).total);
      candidates.push({kind:'insert', label:`${where}에 끼우기`, routes: next, max});
      snap('insert', `기사 ${other}의 ${where}에 끼우면 경로는 ${next[other].join(' → ')}, 부하는 ${jo(l[0], '과', '와')} ${l[1]}, 최대 ${max}입니다.`, next, {candidates: copy(candidates), candidate: candidates.length - 1});
    }
    const bestInsert = candidates.reduce((a, c) => c.max < a.max ? c : a, candidates[0]);
    snap('judge', `끼우는 자리 중 가장 좋은 곳은 ${bestInsert.label}로 최대 ${bestInsert.max}입니다. 현재 ${startMax}${bestInsert.max < startMax ? '보다 낮아 받아들일 수 있습니다. 교환도 확인합니다.' : '보다 낮지 않아 옮기기만으로는 벗어나지 못합니다. 교환을 시도합니다.'}`, bestInsert.routes, {candidates: copy(candidates), candidate: candidates.indexOf(bestInsert)});
    for (const y of routes[other]) {
      const next = copy(routes);
      next[owner] = routes[owner].map(p => p === passenger ? y : p);
      next[other] = routes[other].map(p => p === y ? passenger : p);
      const max = maxOf(next), l = next.map((r, d) => riLoad(d, r).total);
      candidates.push({kind:'swap', label:`승객 ${passenger} ↔ 승객 ${y}`, routes: next, max});
      snap('swap', `승객 ${jo(passenger, '과', '와')} ${jo(y, '을', '를')} 바꾸면 기사 0의 경로는 ${next[0].join(' → ')}, 기사 1의 경로는 ${next[1].join(' → ')}이고 부하는 ${jo(l[0], '과', '와')} ${l[1]}, 최대 ${max}입니다.`, next, {candidates: copy(candidates), candidate: candidates.length - 1});
    }
    const best = candidates.reduce((a, c) => c.max < a.max ? c : a, candidates[0]), improved = best.max < startMax;
    snap('done', improved ? `가장 좋은 이웃은 ${best.label}로 최대 ${best.max}입니다. ${startMax}보다 낮으므로 받아들입니다.` : `모든 이웃의 최대가 현재 ${startMax}보다 낮지 않아 경로를 그대로 둡니다.`, improved ? best.routes : routes, {candidates: copy(candidates), candidate: improved ? candidates.indexOf(best) : null, improved});
    return states;
  }
  // ---- bucket search: widening rings of cells and the stopping rule ----
  const bkExample = {name:'16×16 지도 · 4×4 칸 · 센터 (5,5)', side:16, cell:4, center:[5,5], stock:{A:1,B:2}, deliveries:[[4,6,'C'],[7,7,'A'],[5,8,'B'],[1,1,'A'],[10,10,'B'],[11,2,'A'],[2,5,'C'],[9,5,'B'],[0,8,'B'],[14,9,'A'],[13,14,'B'],[3,14,'B']], picks:3};
  function bucketSearchTrace(example, early) {
    const {side, cell, deliveries} = example, G = side / cell, states = [];
    const stock = {...example.stock}, alive = new Set(deliveries.map((_, i) => i)), history = [];
    let at = [...example.center];
    const cellOf = i => [Math.floor(deliveries[i][0] / cell), Math.floor(deliveries[i][1] / cell)];
    const dist = (i, p) => Math.abs(deliveries[i][0] - p[0]) + Math.abs(deliveries[i][1] - p[1]);
    const snap = (phase, message, extra = {}) => states.push(copy({phase, message, early, at, stock, alive: [...alive], history, pick: 0, ring: null, ringCells: [], viewedCells: [], ringItems: [], inspected: 0, remaining: alive.size, best: null, chosen: null, ...extra}));
    snap('start', `센터 (${at[0]},${at[1]})에 A ${stock.A}개, B ${stock.B}개가 있고 C는 없습니다. 배송은 ${deliveries.length}개이고 칸 한 변은 ${cell}입니다. 종료 조건은 ${early ? '한 겹 일찍 끊는' : '정확한'} 식 bestDist ≤ ${early ? 'r' : '(r − 1)'} × ${cell}입니다. 세 번 고릅니다.`);
    for (let pick = 1; pick <= example.picks; pick++) {
      const gy0 = Math.floor(at[0] / cell), gx0 = Math.floor(at[1] / cell), viewed = [], remaining = alive.size;
      let best = null, inspected = 0, scanned = 0;
      for (let r = 0; r < G; r++) {
        const threshold = early ? r * cell : (r - 1) * cell;
        if (r > 0 && best && best.dist <= threshold) {
          snap('stop', `${jo('링 ' + r, '을', '를')} 보기 전에 최선 거리 ${jo(best.dist, '이', '가')} ${early ? 'r' : '(r − 1)'} × ${cell} = ${threshold} 이하인지 봅니다. ${best.dist} ≤ ${threshold}이므로 멈춥니다. 검사한 후보 ${inspected} / 남은 배송 ${remaining}.`, {pick, ring: r, viewedCells: copy(viewed), inspected, best: copy(best), remaining});
          break;
        }
        const cells = [];
        for (let gy = gy0 - r; gy <= gy0 + r; gy++) for (let gx = gx0 - r; gx <= gx0 + r; gx++) {
          if (gy < 0 || gy >= G || gx < 0 || gx >= G || Math.max(Math.abs(gy - gy0), Math.abs(gx - gx0)) !== r) continue;
          cells.push([gy, gx]); viewed.push([gy, gx]);
        }
        const items = [];
        for (const [gy, gx] of cells) for (const i of alive) { const [cy, cx] = cellOf(i); if (cy === gy && cx === gx) items.push({id: i, type: deliveries[i][2], y: deliveries[i][0], x: deliveries[i][1], ok: stock[deliveries[i][2]] > 0, dist: dist(i, at)}); }
        inspected += items.length; scanned = r;
        for (const it of items) if (it.ok && (!best || it.dist < best.dist)) best = {id: it.id, dist: it.dist};
        snap('scan', `${r > 0 ? `링 ${r} 앞의 종료 조건은 거짓이라 계속합니다. ` : ''}링 ${r}의 칸 ${cells.length}개에서 후보 ${items.length}개를 검사했습니다(누적 ${inspected} / 남은 배송 ${remaining}). 실을 수 있는 후보 중 최선은 ${best ? `배송 ${best.id}, 거리 ${best.dist}` : '아직 없음'}입니다.`, {pick, ring: r, ringCells: cells, viewedCells: copy(viewed), ringItems: items, inspected, best: best && copy(best), remaining});
      }
      let truth = null;
      for (const i of alive) if (stock[deliveries[i][2]] > 0 && (truth === null || dist(i, at) < dist(truth, at))) truth = i;
      if (!best) { snap('done', '실을 수 있는 후보가 없어 멈춥니다.', {pick, viewedCells: copy(viewed), inspected, remaining}); return states; }
      const chosen = best.id, min = dist(truth, at), correct = best.dist === min, from = [...at];
      history.push({pick, id: chosen, type: deliveries[chosen][2], from, dist: best.dist, min, correct, inspected, remaining});
      alive.delete(chosen); stock[deliveries[chosen][2]]--; at = [deliveries[chosen][0], deliveries[chosen][1]];
      snap(pick === example.picks ? 'done' : 'pick', `${pick}번째 고르기: 배송 ${chosen} (${at[0]},${at[1]}) ${deliveries[chosen][2]}, 거리 ${best.dist}. 전수 탐색의 최솟값은 ${min}이므로 ${correct ? '같은 답입니다.' : '틀린 답입니다. 더 가까운 배송을 놓쳤습니다.'} 검사한 후보 ${inspected} / 남은 배송 ${remaining}.`, {pick, ring: scanned, viewedCells: copy(viewed), inspected, best: copy(best), chosen, remaining});
    }
    return states;
  }
  // ---- boundary delta: entropy as a sum of boundary products ----
  const bdExample = {name:'4×5 격자 · 입자 5개 · 본문 손계산', H:4, W:5, limit:800, particles:[['A',0,0],['B',0,4],['C',3,0],['D',3,4],['E',1,2]], calls:[['A',1],['B',1],['C',0]]};
  const bdDirNames = ['위로', '오른쪽으로', '아래로', '왼쪽으로'], bdDY = [-1, 0, 1, 0], bdDX = [0, 1, 0, -1];
  function bdBoundaries(H, W, ps) {
    const n = ps.length, col = [], row = [];
    for (let c = 0; c < W - 1; c++) { const left = ps.filter(p => p[2] <= c).length; col.push({index: c, left, right: n - left, value: left * (n - left)}); }
    for (let r = 0; r < H - 1; r++) { const up = ps.filter(p => p[1] <= r).length; row.push({index: r, left: up, right: n - up, value: up * (n - up)}); }
    return {col, row};
  }
  const bdPairs = ps => { let e = 0; for (let i = 0; i < ps.length; i++) for (let j = i + 1; j < ps.length; j++) e += Math.abs(ps[i][1] - ps[j][1]) + Math.abs(ps[i][2] - ps[j][2]); return e; };
  const bdScore = (e0, e, used, limit) => { const r = Math.max(0, e0 - e) / e0; return {ratioPart: Math.floor(1000000 * r * r), bonus: Math.floor((limit - used) / 100), improvement: e0 - e, ratio: r}; };
  function boundaryDeltaTrace(example, calls) {
    const {H, W, limit} = example, n = example.particles.length, states = [];
    let ps = copy(example.particles), used = 0;
    const e0 = bdPairs(ps), sum = list => list.reduce((a, x) => a + x.value, 0);
    const snap = (phase, message, extra = {}) => { const b = bdBoundaries(H, W, ps), e = bdPairs(ps); states.push(copy({phase, message, particles: ps, bounds: b, colSum: sum(b.col), rowSum: sum(b.row), boundSum: sum(b.col) + sum(b.row), entropy: e, e0, used, limit, score: bdScore(e0, e, used, limit), H, W, call: null, ...extra})); };
    snap('start', `격자 ${H}×${W}에 입자 ${n}개가 있습니다. 모든 쌍의 거리 합 E0 = ${e0}는 열 경계 ${W - 1}개와 행 경계 ${H - 1}개의 (한쪽 개수 × 반대쪽 개수) 합과 같습니다. 호출 ${calls.length}번을 차례로 해 봅니다.`);
    calls.forEach(([name, dir], index) => {
      const before = bdBoundaries(H, W, ps), p = ps.find(q => q[0] === name), ny = p[1] + bdDY[dir], nx = p[2] + bdDX[dir];
      used++;
      const out = ny < 0 || ny >= H || nx < 0 || nx >= W, blocked = !out && ps.some(q => q[1] === ny && q[2] === nx);
      if (out || blocked) {
        snap('fail', `호출 ${index + 1}: 입자 ${jo(name, '을', '를')} ${bdDirNames[dir]} 옮깁니다. ${out ? '격자 밖이라' : '이미 입자가 있어'} 실패입니다. 입자와 엔트로피는 그대로이고 사용 횟수만 ${used}로 늘어납니다.`, {call: {name, dir, ok: false, reason: out ? 'out' : 'blocked', index: index + 1}});
        return;
      }
      const horizontal = dir % 2 === 1, forward = dir === 1 || dir === 2, axis = horizontal ? 'col' : 'row', coordinate = horizontal ? p[2] : p[1];
      const bi = forward ? coordinate : coordinate - 1, pre = before[axis][bi].left, delta = forward ? 2 * pre - 1 - n : n - 1 - 2 * pre, eBefore = bdPairs(ps);
      ps = ps.map(q => q[0] === name ? [name, ny, nx] : q);
      const after = bdBoundaries(H, W, ps), eAfter = bdPairs(ps);
      snap('shift', `호출 ${index + 1}: 입자 ${jo(name, '을', '를')} ${bdDirNames[dir]} 옮깁니다. ${axis === 'col' ? '열' : '행'} 경계 ${bi} 하나만 ${before[axis][bi].left}×${before[axis][bi].right} = ${before[axis][bi].value}에서 ${after[axis][bi].left}×${after[axis][bi].right} = ${after[axis][bi].value}로 바뀌고 E는 ${eBefore} → ${eAfter}입니다.`, {call: {name, dir, ok: true, index: index + 1, axis, boundary: bi, pre, formula: delta, full: eAfter - eBefore, before: before[axis][bi], after: after[axis][bi], eBefore}});
    });
    const last = states.at(-1), s = last.score;
    states.push(copy({...last, phase: 'done', call: null, message: `호출 ${used}번 뒤 E = ${last.entropy}. 줄어든 비율 ${last.e0 - last.entropy}/${last.e0}의 제곱 ${s.ratioPart}점에 남은 횟수 (${limit} − ${used}) ÷ 100의 몫 ${s.bonus}점을 더해 ${s.ratioPart + s.bonus}점입니다.`}));
    return states;
  }
  // ---- mirror policy: nearest valuable cell vs. value per move ----
  const mpN = 30;
  const mpExample = {name:'30×30 지도의 왼쪽 위 · 시작 (2,3)', start:[2,3], cells:[[0,0,2],[1,1,3],[2,2,2],[2,5,40],[2,6,60]], rows:3, cols:7};
  const mpDY = [-1, 0, 1, 0], mpDX = [0, 1, 0, -1], mpOpts = {radius: 3, cost: 1};
  const fmtKey = k => { const r = Math.round(k * 1000) / 1000; return Number.isInteger(r * 10) ? r.toFixed(1) : String(r); };
  function mpBfs(value, seen, at, movesLeft) {
    const grid = () => Array.from({length: mpN}, () => Array(mpN).fill(-1)), dist = grid(), from = grid(), gain = Array.from({length: mpN}, () => Array(mpN).fill(0));
    const queue = [[at[0], at[1]]]; dist[at[0]][at[1]] = 0;
    for (let head = 0; head < queue.length; head++) {
      const [y, x] = queue[head];
      if (dist[y][x] === movesLeft) continue;
      for (let d = 0; d < 4; d++) {
        const ny = y + mpDY[d], nx = x + mpDX[d];
        if (ny < 0 || ny >= mpN || nx < 0 || nx >= mpN) continue;
        const g = gain[y][x] + (seen.has(ny * mpN + nx) ? 0 : (value[ny * mpN + nx] || 0));
        if (dist[ny][nx] < 0) { dist[ny][nx] = dist[y][x] + 1; gain[ny][nx] = g; from[ny][nx] = d; queue.push([ny, nx]); }
        else if (dist[ny][nx] === dist[y][x] + 1 && g > gain[ny][nx]) { gain[ny][nx] = g; from[ny][nx] = d; }
      }
    }
    return {dist, gain, from};
  }
  function mpAround(value, seen, ty, tx, radius) {
    let sum = 0;
    for (let y = ty - radius; y <= ty + radius; y++) for (let x = tx - radius; x <= tx + radius; x++) {
      const d = Math.abs(y - ty) + Math.abs(x - tx);
      if (d === 0 || d > radius || y < 0 || y >= mpN || x < 0 || x >= mpN || seen.has(y * mpN + x)) continue;
      sum += value[y * mpN + x] || 0;
    }
    return sum;
  }
  // One policy's walk: ticks[t] describes the state after t moves, with the target pick made on arrival (if any).
  function mpRun(example, policy, budget, weight) {
    const value = {}; example.cells.forEach(([y, x, v]) => { value[y * mpN + x] = v; });
    const seen = new Set([example.start[0] * mpN + example.start[1]]);
    let at = [...example.start], left = budget, score = 0;
    const ticks = [{at: [...at], left, score, got: 0, seen: [...seen], path: [], target: null, pick: null, ended: false}];
    while (true) {
      const here = ticks.at(-1), R = left > 0 ? mpBfs(value, seen, at, left) : null, cands = [];
      if (R) for (let y = 0; y < mpN; y++) for (let x = 0; x < mpN; x++) {
        if (R.dist[y][x] <= 0 || seen.has(y * mpN + x) || !(value[y * mpN + x] > 0)) continue;
        const h = mpAround(value, seen, y, x, mpOpts.radius);
        cands.push({y, x, d: R.dist[y][x], g: R.gain[y][x], h, key: (R.gain[y][x] + weight * h) / (R.dist[y][x] + mpOpts.cost)});
      }
      if (!cands.length) { here.ended = true; break; }
      let target = cands[0];
      for (const c of cands) if (policy === 1 ? (c.d < target.d || (c.d === target.d && c.g > target.g)) : c.key > target.key) target = c;
      here.pick = {target: [target.y, target.x], candidates: [...cands].sort((a, b) => a.d - b.d || b.g - a.g || a.y - b.y || a.x - b.x)};
      const dirs = []; for (let y = target.y, x = target.x; R.dist[y][x] > 0;) { const d = R.from[y][x]; dirs.push(d); y -= mpDY[d]; x -= mpDX[d]; }
      dirs.reverse();
      const path = []; { let y = at[0], x = at[1]; for (const d of dirs) { y += mpDY[d]; x += mpDX[d]; path.push([y, x]); } }
      dirs.forEach((d, i) => {
        at = [at[0] + mpDY[d], at[1] + mpDX[d]]; left--;
        const key = at[0] * mpN + at[1], got = seen.has(key) ? 0 : (value[key] || 0);
        seen.add(key); score += got;
        ticks.push({at: [...at], left, score, got, seen: [...seen], path: copy(path), pathIndex: i, target: [target.y, target.x], pick: null, ended: false});
      });
    }
    return ticks;
  }
  function mirrorPolicyTrace(example, budget, weight) {
    const runs = [1, 2].map(policy => mpRun(example, policy, budget, weight)), count = Math.max(...runs.map(r => r.length)), states = [];
    for (let t = 0; t < count; t++) {
      const policies = runs.map(run => ({...run[Math.min(t, run.length - 1)], idle: t >= run.length, lastPick: [...run.slice(0, Math.min(t, run.length - 1) + 1)].reverse().find(x => x.pick)?.pick || null}));
      const text = policies.map((v, i) => {
        const name = `정책 ${i + 1}`, keyText = v.pick && i === 1 ? ` (키 ${fmtKey(v.pick.candidates.find(c => c.y === v.pick.target[0] && c.x === v.pick.target[1]).key)})` : '';
        const head = t === 0 ? `${name}: 시작 칸 (${v.at[0]},${v.at[1]}), 남은 이동 ${budget}번.` : v.idle ? `${name}: 이미 끝났습니다. 누적 ${v.score}점.` : `${name}: (${v.at[0]},${v.at[1]}) 칸으로 이동${v.got ? `해 ${v.got}점을 얻음` : ''}. 누적 ${v.score}점, 남은 이동 ${v.left}번.`;
        return `${head}${v.pick ? ` 다음 목표는 (${v.pick.target[0]},${v.pick.target[1]})입니다${keyText}.` : ''}${v.ended && !v.idle ? ' 남은 이동으로 닿는 값 있는 칸이 없어 끝납니다.' : ''}`;
      }).join(' ');
      states.push(copy({phase: t === count - 1 ? 'done' : t === 0 ? 'start' : 'visit', message: text, tick: t, count, policies, budget, weight}));
    }
    return states;
  }
  // ---- score check: the problem-modeling lesson's assignment hand example ----
  const scExample = {name:'작업 6개 · 기계 3대 · 기계당 3개 · 본문 손계산', M:3, K:3, d:[31,26,10,35,13,21], c:[[10,16,19],[11,29,4],[10,8,29],[22,17,2],[9,21,10],[9,5,25]], baseline:[0,0,0,1,1,1], hand:[0,2,1,2,0,1]};
  // assign[j] is a machine number or null (not chosen yet). The score exists only for a complete, valid assignment.
  function scEvaluate(ex, assign) {
    const loads = Array(ex.M).fill(0), counts = Array(ex.M).fill(0), jobs = Array.from({length: ex.M}, () => []), missing = [];
    let extra = 0;
    assign.forEach((m, j) => { if (m === null || m === undefined) { missing.push(j); return; } loads[m] += ex.d[j]; counts[m]++; jobs[m].push(j); extra += ex.c[j][m]; });
    const over = counts.map((n, m) => n > ex.K ? m : -1).filter(m => m >= 0), sumSq = loads.reduce((a, l) => a + l * l, 0), quotient = Math.floor(sumSq / 100);
    const valid = !over.length && !missing.length;
    return {loads, counts, jobs, extra, missing, over, sumSq, quotient, valid, score: valid ? quotient + extra : null};
  }
  function scLowerBound(ex) {
    const cheapest = ex.c.reduce((a, row) => a + Math.min(...row), 0), total = ex.d.reduce((a, v) => a + v, 0), balanced = Math.floor(total * total / (100 * ex.M));
    return {cheapest, total, balanced, bound: cheapest + balanced};
  }
  function scOptimum(ex) {
    const n = ex.d.length; let best = Infinity, assign = null, valid = 0;
    for (let code = 0; code < Math.pow(ex.M, n); code++) {
      const a = []; let q = code; for (let j = 0; j < n; j++) { a.push(q % ex.M); q = Math.floor(q / ex.M); }
      const r = scEvaluate(ex, a); if (!r.valid) continue;
      valid++; if (r.score < best) { best = r.score; assign = a; }
    }
    return {score: best, assign, valid, total: Math.pow(ex.M, n)};
  }
  // ---- construction steps: the construction-heuristics lesson's seven-point hand example ----
  const csExample = {name:'점 7개 · 본문 손계산', points:[[5,5],[3,3],[7,3],[6,2],[6,9],[5,0],[5,7]]};
  const csRuleNames = [['nn','가장 가까운 점 잇기'],['cheapest','가장 싼 삽입'],['farthest','가장 먼 점 삽입'],['regret','후회 삽입']];
  function csSlots(points, order, p, anySlot) {
    const len = order.length, out = [], d = (a, b) => manhattan(points[a], points[b]);
    for (let s = anySlot ? 0 : len; s <= len; s++) {
      let cost;
      if (s === 0) cost = d(p, order[0]);
      else if (s === len) cost = d(order[len - 1], p);
      else cost = d(order[s - 1], p) + d(p, order[s]) - d(order[s - 1], order[s]);
      out.push({slot: s, cost});
    }
    return out;
  }
  // Every remaining point with its cheapest slot (earliest on ties), second cheapest cost, regret, and distance to the path.
  function csCandidates(points, order, rule) {
    const used = new Set(order), list = [];
    for (let p = 0; p < points.length; p++) {
      if (used.has(p)) continue;
      const slots = csSlots(points, order, p, rule !== 'nn'), best = slots.reduce((a, b) => b.cost < a.cost ? b : a), costs = slots.map(x => x.cost).sort((a, b) => a - b);
      const second = costs.length > 1 ? costs[1] : null;
      list.push({p, slot: best.slot, best: best.cost, second, regret: second === null ? null : second - best.cost, near: Math.min(...order.map(q => manhattan(points[p], points[q])))});
    }
    return list;
  }
  const csPrimary = (c, rule) => rule === 'farthest' ? -c.near : rule === 'regret' ? -c.regret : c.best;
  function csPick(list, rule) {
    let chosen = list[0];
    for (const c of list) {
      const a = [csPrimary(c, rule), c.best, c.p], b = [csPrimary(chosen, rule), chosen.best, chosen.p];
      for (let i = 0; i < 3; i++) { if (a[i] !== b[i]) { if (a[i] < b[i]) chosen = c; break; } }
    }
    return chosen;
  }
  const csOptimumCache = {};
  function csOptimum(points) {
    const key = JSON.stringify(points);
    if (csOptimumCache[key]) return csOptimumCache[key];
    let best = {cost: Infinity, order: null};
    const walk = (order, left) => {
      if (!left.length) { const c = pathCost(points, order); if (c < best.cost) best = {cost: c, order: [...order]}; return; }
      left.forEach((v, i) => walk([...order, v], [...left.slice(0, i), ...left.slice(i + 1)]));
    };
    walk([], points.map((_, i) => i));
    return (csOptimumCache[key] = best);
  }
  function constructionTrace(points, rule) {
    const n = points.length, order = [0], states = [], name = csRuleNames.find(r => r[0] === rule)[1];
    let cost = 0;
    states.push(copy({phase: 'start', rule, step: 0, total: n - 1, order, cost, candidates: [], chosen: null, message: `${name}: 점 0에서 시작합니다. 동률이면 번호가 작은 점, 자리 번호가 작은 쪽을 먼저 고릅니다. "한 단계"를 누르면 다음 점과 끼울 자리를 정합니다.`}));
    while (order.length < n) {
      const cands = csCandidates(points, order, rule), pick = csPick(cands, rule), tied = cands.filter(c => csPrimary(c, rule) === csPrimary(pick, rule)).length;
      const before = [...order]; order.splice(pick.slot, 0, pick.p); cost += pick.best;
      const step = order.length - 1, last = order.length === n;
      const tie = tied > 1 ? ` 같은 값이 ${tied}개라 번호가 작은 점을 고릅니다.` : '';
      let why;
      if (rule === 'nn') why = `점 ${before[before.length - 1]}에서 가장 가까운 점은 ${pick.p}번으로 거리 ${pick.best}입니다.${tie} 경로 끝에 붙입니다.`;
      else if (rule === 'cheapest') why = `모든 (점, 자리) 쌍 중 늘어나는 길이가 가장 작은 쌍은 점 ${pick.p}, 자리 ${pick.slot}이고 ${pick.best}입니다.${tie}`;
      else if (rule === 'farthest') why = `경로의 가장 가까운 점까지의 거리가 가장 큰 점은 ${pick.p}번(${pick.near})입니다.${tie} 가장 싼 자리 ${pick.slot}에 끼웁니다.`;
      else why = `가장 싼 자리와 두 번째로 싼 자리의 비용 차(후회)가 가장 큰 점은 ${pick.p}번(후회 ${pick.regret})입니다.${tie} 가장 싼 자리 ${pick.slot}에 끼웁니다.`;
      const opt = last ? csOptimum(points) : null;
      states.push(copy({phase: last ? 'done' : 'step', rule, step, total: n - 1, order, cost, candidates: cands, chosen: pick.p, slot: pick.slot, added: pick.best, before, optimum: opt, message: `${step}단계: ${why} 늘어난 길이 +${pick.best}. 경로 ${order.join(' → ')}, 비용 ${cost}.${last ? ` 모든 점을 지났습니다. 5,040개 순열을 모두 계산한 최단 길이는 ${opt.cost}이므로 ${cost === opt.cost ? '이 경로는 최적과 같습니다.' : `이 경로는 최적보다 ${cost - opt.cost} 깁니다.`}` : ''}`}));
    }
    return states;
  }
  return {lowerBoundTrace,bfsExamples,bfsTrace,graph,dijkstraTrace,matrix,prefixTable,prefixTrace,routes,manhattan,pathCost,twoOpt,twoOptTrace,acceptance,annealingPlotMax,annealingTrace,nnExamples,nearestNeighborTrace,optimalOpenRoute,beamExamples,beamSearchTrace,optimalBeamLeaf,drItems,DR_LENGTH,drExamples,drScore,drSlots,drRepair,destroyRepairTrace,pairedExamples,pairedStats,pairedTrace,ufExamples,ufFind,unionFindTrace,segExamples,segArray,segBuild,segmentTrace,amTime,amExamples,amLoads,amNeighbors,amOptimum,assignmentMovesTrace,riDrivers,riPassengers,riStart,riExamples,riLoad,routeInsertionTrace,bkExample,bucketSearchTrace,bdExample,bdBoundaries,bdPairs,bdScore,bdDirNames,boundaryDeltaTrace,mpN,mpExample,mpBfs,mpAround,mpRun,mirrorPolicyTrace,fmtKey,scExample,scEvaluate,scLowerBound,scOptimum,csExample,csRuleNames,csSlots,csCandidates,csPick,csOptimum,constructionTrace};
});
