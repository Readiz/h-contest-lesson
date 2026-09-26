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
  return {lowerBoundTrace,bfsExamples,bfsTrace,graph,dijkstraTrace,matrix,prefixTable,prefixTrace,routes,manhattan,pathCost,twoOpt,twoOptTrace,acceptance,annealingPlotMax,annealingTrace};
});
