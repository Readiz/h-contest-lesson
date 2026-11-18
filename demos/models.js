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
  return {lowerBoundTrace,bfsExamples,bfsTrace,graph,dijkstraTrace,matrix,prefixTable,prefixTrace,routes,manhattan,pathCost,twoOpt,twoOptTrace,acceptance,annealingPlotMax,annealingTrace,nnExamples,nearestNeighborTrace,optimalOpenRoute,beamExamples,beamSearchTrace,optimalBeamLeaf,drItems,DR_LENGTH,drExamples,drScore,drSlots,drRepair,destroyRepairTrace,pairedExamples,pairedStats,pairedTrace,ufExamples,ufFind,unionFindTrace,segExamples,segArray,segBuild,segmentTrace};
});
