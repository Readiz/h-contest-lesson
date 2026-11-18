#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const M = require('../demos/models.js');
let checks=0;
const equal=(actual,expected,label)=>{assert.deepEqual(actual,expected,label);checks++;};
// Independent linear scan oracle, including empty arrays, duplicates, and both sentinels.
for(const a of [[],[4],[1,1,1],[1,2,4,4,4,7,9,10],[-5,-2,0,0,9]])for(let t=-8;t<=14;t++){
  const trace=M.lowerBoundTrace(a,t),expected=a.findIndex(v=>v>=t);
  equal(trace.at(-1).lo,expected===-1?a.length:expected,'lower_bound linear oracle');
  trace.forEach(s=>{assert(s.lo<=s.hi&&s.lo>=0&&s.hi<=a.length);assert(a.slice(0,s.lo).every(v=>v<t));assert(a.slice(s.hi).every(v=>v>=t));checks+=3;});
}
// BFS distance oracle uses synchronous repeated relaxation, not a queue.
for(const {rows} of M.bfsExamples){
  const h=rows.length,w=rows[0].length,start=rows.join('').indexOf('S'),goal=rows.join('').indexOf('G');
  let oracle=Array(w*h).fill(Infinity);oracle[start]=0;
  for(let pass=0;pass<w*h;pass++){const next=[...oracle];for(let r=0;r<h;r++)for(let c=0;c<w;c++)if(rows[r][c]!=='#')for(const[dr,dc]of[[1,0],[-1,0],[0,1],[0,-1]]){const rr=r+dr,cc=c+dc;if(rr>=0&&rr<h&&cc>=0&&cc<w&&rows[rr][cc]!=='#')next[r*w+c]=Math.min(next[r*w+c],oracle[rr*w+cc]+1);}oracle=next;}
  const trace=M.bfsTrace(rows),last=trace.at(-1);
  equal(last.distance,oracle.map(v=>v===Infinity?-1:v),'BFS relaxation oracle');
  for(const state of trace){equal(new Set(state.queue).size,state.queue.length,'no duplicate queue entry');assert(state.queue.every(v=>state.distance[v]>=0));checks++;}
  if(last.distance[goal]>=0){equal(last.path.length-1,last.distance[goal],'BFS path length');equal(last.path[0],start);equal(last.path.at(-1),goal);for(let i=1;i<last.path.length;i++){const a=last.path[i-1],b=last.path[i];equal(Math.abs(Math.floor(a/w)-Math.floor(b/w))+Math.abs(a%w-b%w),1);}}
  else equal(last.path,[],'unreachable goal');
}
// Floyd-Warshall independently validates weighted shortest paths.
const graphs=[M.graph,{nodes:['S','A','B','C'],points:[],edges:[[0,1,0],[1,2,4],[0,2,9],[2,1,2]]}];
for(const g of graphs){const n=g.nodes.length,d=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?0:Infinity));for(const[a,b,w]of g.edges)d[a][b]=Math.min(d[a][b],w);for(let k=0;k<n;k++)for(let i=0;i<n;i++)for(let j=0;j<n;j++)d[i][j]=Math.min(d[i][j],d[i][k]+d[k][j]);const trace=M.dijkstraTrace(g);equal(trace.at(-1).distance,d[0].map(v=>Number.isFinite(v)?v:null),'Dijkstra Floyd-Warshall oracle');equal(M.dijkstraTrace(g,2).at(-1).distance,d[2].map(v=>Number.isFinite(v)?v:null),'alternate source oracle');trace.filter(s=>s.phase==='stale').forEach(s=>{assert.notEqual(s.popped[0],s.distance[s.popped[1]]);equal(s.edge,null,'stale item must not inspect edge');});}
assert(M.dijkstraTrace().some(s=>s.phase==='stale'&&s.popped[0]===7&&s.popped[1]===1));checks++;
// Every rectangular query, including empty regions and edges, against direct sums.
for(let r1=0;r1<=M.matrix.length;r1++)for(let r2=r1;r2<=M.matrix.length;r2++)for(let c1=0;c1<=M.matrix[0].length;c1++)for(let c2=c1;c2<=M.matrix[0].length;c2++){
  const last=M.prefixTrace(M.matrix,[r1,c1,r2,c2]).states.at(-1);let expected=0;
  for(let r=0;r<M.matrix.length;r++)for(let c=0;c<M.matrix[0].length;c++){const inRect=r>=r1&&r<r2&&c>=c1&&c<c2;if(inRect)expected+=M.matrix[r][c];equal(last.coefficient[r][c],inRect?1:0,'inclusion-exclusion coefficient');}
  equal(last.total,expected,'prefix rectangle direct oracle');
  M.prefixTrace(M.matrix,[r1,c1,r2,c2]).states.forEach((state,step)=>{
    let direct=0;
    for(let r=0;r<M.matrix.length;r++)for(let c=0;c<M.matrix[0].length;c++){
      const coefficient=(step>=1&&r<r2&&c<c2?1:0)-(step>=2&&r<r1&&c<c2?1:0)-(step>=3&&r<r2&&c<c1?1:0)+(step>=4&&r<r1&&c<c1?1:0);
      equal(state.coefficient[r][c],coefficient,'prefix intermediate inclusion count');direct+=coefficient*M.matrix[r][c];
    }
    equal(state.total,direct,'prefix intermediate sum');
  });
}
// Exhaust all valid reversal ranges; oracle rebuilds and fully sums the route.
let seed=8123;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed;};
for(let test=0;test<35;test++){
  const n=4+test%8,points=Array.from({length:n},()=>[random()%31-15,random()%31-15]),order=Array.from({length:n},(_,i)=>i);
  for(let i=n-1;i>1;i--){const j=1+random()%i;[order[i],order[j]]=[order[j],order[i]];}
  const fullCost=route=>{let value=0;for(let i=1;i<route.length;i++){const a=points[route[i-1]],b=points[route[i]];value+=Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);}return value;};
  for(let left=1;left<n;left++)for(let right=left;right<n;right++){
    const result=M.twoOpt(points,order,left,right),candidate=[...order];for(let a=left,b=right;a<b;a++,b--)[candidate[a],candidate[b]]=[candidate[b],candidate[a]];
    equal(result.candidate,candidate);equal(candidate[0],0,'fixed warehouse');equal(result.delta,fullCost(candidate)-fullCost(order),'2-opt boundary vs full distance');equal(result.removed.length,right===n-1?1:2,'open-tail boundary count');
  }
}
equal(M.twoOpt(M.routes[0].points,M.routes[0].order,2,4).delta,-7,'lesson tail example');
assert.throws(()=>M.twoOpt(M.routes[0].points,M.routes[0].order,0,3),RangeError);checks++;
for(const example of M.routes){
  const trace=M.twoOptTrace(example.points,example.order,example.left,example.right),last=trace.at(-1);
  equal(last.order,last.delta<0?last.candidate:example.order,'strict improvement acceptance');
  equal(trace[3].order,last.candidate,'candidate is shown before acceptance');
}
assert(M.twoOptTrace(M.routes[2].points,M.routes[2].order,1,2).at(-1).delta>0);checks++;
// SA handles temperature zero and always retains its best-so-far solution.
equal(M.acceptance(-2,0),1);equal(M.acceptance(0,0),1);equal(M.acceptance(5,0),0);
assert(Math.abs(M.acceptance(4,2)-Math.exp(-2))<1e-14);checks++;
for(const temp of [0,0.5,2,8,20])for(const scale of [1,6,20]){
  const trace=M.annealingTrace(temp,scale);let best=50;
  for(let i=1;i<trace.length;i++){const s=trace[i],prev=trace[i-1];equal(s.temperature,temp*Math.pow(0.88,i-1),'cooling temperature');const oracleP=s.delta<=0?1:(s.temperature===0?0:Math.exp(-s.delta/s.temperature));equal(s.probability,oracleP,'independent acceptance probability');equal(s.candidate,prev.current+s.delta);equal(s.accepted,s.draw<s.probability);equal(s.current,s.accepted?s.candidate:prev.current);best=Math.min(best,s.current);equal(s.best,best);assert(s.best<=prev.best);checks++;if(temp===0)assert(s.current<=prev.current);}
}
assert(M.annealingTrace(8,6).some(s=>s.accepted&&s.delta>0&&s.current>s.best));checks++;
for(let scale=1;scale<=20;scale++){const limit=M.annealingPlotMax(scale);for(const s of M.annealingTrace(8,scale)){if(s.delta!==null){assert(s.delta<=limit,'acceptance marker fits full delta axis');checks++;}}}
equal(M.annealingTrace(8,20).at(-1).delta,36,'maximum scale reaches delta 36');
assert(M.annealingPlotMax(20)>=36);checks++;
// Nearest neighbor: a separately written scan and a permutation search for the optimum.
const permutations=(items)=>items.length<=1?[items]:items.flatMap((x,i)=>permutations([...items.slice(0,i),...items.slice(i+1)]).map(rest=>[x,...rest]));
const routeLength=(points,order)=>order.slice(1).reduce((sum,v,i)=>sum+Math.abs(points[v][0]-points[order[i]][0])+Math.abs(points[v][1]-points[order[i]][1]),0);
const nnSets=[...M.nnExamples.map(e=>e.points)];
for(let test=0;test<40;test++){const n=2+test%7;nnSets.push(Array.from({length:n},(_,i)=>i===0?[0,0]:[random()%7-3,random()%7-3]));}
for(const points of nnSets){
  const left=new Set(points.map((_,i)=>i).slice(1)),order=[0];
  while(left.size){const here=points[order.at(-1)],ranked=[...left].map(v=>[Math.abs(here[0]-points[v][0])+Math.abs(here[1]-points[v][1]),v]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);order.push(ranked[0][1]);left.delete(ranked[0][1]);}
  const trace=M.nearestNeighborTrace(points),last=trace.at(-1);
  equal(last.order,order,'nearest neighbor route vs independent scan');equal(last.cost,routeLength(points,order),'nearest neighbor cost');
  const brute=Math.min(...permutations(points.slice(1).map((_,i)=>i+1)).map(rest=>routeLength(points,[0,...rest])));
  equal(last.optimal.cost,brute,'nearest neighbor optimum vs permutations');assert(last.cost>=brute);checks++;
  equal(routeLength(points,last.optimal.order),brute,'optimal order is a valid route');
  equal(trace.length,1+2*(points.length-1),'two states per chosen point');
  trace.forEach((state,i)=>{if(i)assert(state.cost>=trace[i-1].cost);equal(state.order[0],0);equal(new Set(state.order).size,state.order.length);checks++;});
  trace.filter(st=>st.phase==='scan').forEach(st=>{equal(st.candidates.length,points.length-st.order.length,'candidates are the unvisited points');for(const c of st.candidates)equal(c.dist,Math.abs(points[st.current][0]-points[c.v][0])+Math.abs(points[st.current][1]-points[c.v][1]));const best=Math.min(...st.candidates.map(c=>c.dist));equal(st.candidates.find(c=>c.v===st.chosen).dist,best,'chosen has minimal distance');equal(st.chosen,Math.min(...st.candidates.filter(c=>c.dist===best).map(c=>c.v)),'ties use the smaller index');});
}
{const first=M.nearestNeighborTrace(M.nnExamples[0].points).at(-1),third=M.nearestNeighborTrace(M.nnExamples[2].points).at(-1);assert(first.cost>first.optimal.cost);equal(third.cost,third.optimal.cost,'a case where greedy is optimal');checks++;}
// Beam search: every leaf enumerated independently; full width must equal exhaustive optimum.
const leafScores=t=>{const out=[];for(let a=0;a<3;a++)for(let b=0;b<3;b++)for(let c=0;c<3;c++)out.push({path:[a,b,c],score:t.g0[a]+t.g1[a][b]+t.g2[a][b][c]});return out;};
const randomTree=()=>{const R=()=>Array.from({length:3},()=>1+random()%9);return {g0:R(),g1:[R(),R(),R()],g2:[0,1,2].map(()=>[R(),R(),R()])};};
const trees=[...M.beamExamples];for(let i=0;i<60;i++)trees.push(randomTree());
for(const tree of trees){
  const leaves=leafScores(tree),optimum=Math.max(...leaves.map(l=>l.score));
  equal(M.optimalBeamLeaf(tree).score,optimum,'optimal leaf');
  for(const width of [1,2,3,4,9,27]){
    const trace=M.beamSearchTrace(tree,width),last=trace.at(-1);
    let layer=[{path:[],score:0}];
    for(let depth=0;depth<3;depth++){const next=[];for(const node of layer)for(let k=0;k<3;k++){const path=[...node.path,k];const gain=depth===0?tree.g0[k]:depth===1?tree.g1[node.path[0]][k]:tree.g2[node.path[0]][node.path[1]][k];next.push({path,score:node.score+gain});}next.sort((x,y)=>y.score-x.score||x.path.join('').localeCompare(y.path.join('')));layer=next.slice(0,width);}
    equal(last.best.path,layer[0].path,'beam best path vs independent beam');equal(last.best.score,layer[0].score,'beam best score');
    if(width>=9)equal(last.best.score,optimum,'W covering every state equals the exhaustive optimum');
    for(const state of trace.filter(st=>st.phase==='prune'||st.phase==='done')){const kept=state.candidates.filter(c=>c.kept);equal(kept.length,Math.min(width,state.candidates.length),'beam keeps exactly W');const dropped=state.candidates.filter(c=>!c.kept);if(dropped.length)assert(Math.min(...kept.map(c=>c.score))>=Math.max(...dropped.map(c=>c.score)));checks++;}
  }
}
{const [beamA,beamB]=M.beamExamples,bs=(tree,w)=>M.beamSearchTrace(tree,w).at(-1).best.score,bo=t=>M.optimalBeamLeaf(t).score;
assert(bs(beamA,1)<bo(beamA)&&bs(beamA,2)===bo(beamA));assert(bs(beamB,2)<bo(beamB)&&bs(beamB,3)===bo(beamB));checks+=2;}
// Destroy/repair: score and overlap recomputed from the strip, acceptance only when strictly better.
const drValue=place=>Object.keys(place).reduce((v,id)=>v+M.drItems[id].v,0);
for(const example of M.drExamples){
  const trace=M.destroyRepairTrace(example);let score=drValue(example.place);
  equal(trace[0].currentScore,score,'initial score');
  for(const state of trace){const used=Array(M.DR_LENGTH).fill(0);for(const [id,at] of Object.entries(state.working)){assert(at>=0&&at+M.drItems[id].w<=M.DR_LENGTH,'inside strip');for(let i=at;i<at+M.drItems[id].w;i++)used[i]++;}assert(used.every(v=>v<=1),'no overlap');equal(state.workingScore,drValue(state.working));equal(state.currentScore,drValue(state.current));checks++;}
  for(let trial=1;trial<=example.trials.length;trial++){
    const repaired=trace.find(x=>x.phase==='repair'&&x.trial===trial),judged=trace.filter(x=>x.trial===trial).at(-1);
    equal(judged.accepted,repaired.workingScore>score,'strict improvement only');
    if(judged.accepted)score=repaired.workingScore;
    equal(judged.currentScore,score,'rejected repair restores the earlier layout');
  }
  assert(trace.at(-1).currentScore>=trace[0].currentScore);checks++;
}
assert(M.destroyRepairTrace(M.drExamples[0]).some(st=>st.accepted===true&&st.currentScore>=15));assert(M.destroyRepairTrace(M.drExamples[1]).some(st=>st.accepted===false));checks+=2;
// Paired comparison: independent sum-of-squares formula and every sample count.
for(const example of M.pairedExamples)for(let count=2;count<=example.a.length;count++){
  const trace=M.pairedTrace(example,count);equal(trace.length,count+1,'one state per sample plus start');
  for(let k=2;k<=count;k++){
    const d=example.a.slice(0,k).map((x,i)=>x-example.b[i]),n=k,sum=d.reduce((x,y)=>x+y,0),sq=d.reduce((x,y)=>x+y*y,0),mean=sum/n,variance=(sq-n*mean*mean)/(n-1),stderr=Math.sqrt(variance/n),st=trace[k].stats;
    assert(Math.abs(st.mean-mean)<1e-9&&Math.abs(st.stderr-stderr)<1e-9&&Math.abs(st.low-(mean-2*stderr))<1e-9&&Math.abs(st.high-(mean+2*stderr))<1e-9);checks++;
    equal(st.verdict,mean-2*stderr>0?'better':mean+2*stderr<0?'worse':'unclear','interval vs zero');
  }
}
equal(M.pairedTrace(M.pairedExamples[0],30).at(-1).stats.verdict,'better');equal(M.pairedTrace(M.pairedExamples[1],30).at(-1).stats.verdict,'unclear');
equal(M.pairedStats([5]).stderr,null,'one sample has no standard error');equal(M.pairedStats([3,3,3]).stderr,0,'constant differences');
// Union-find: both forests must match naive label propagation after every operation.
const ufCases=[...M.ufExamples];for(let t=0;t<40;t++){const n=3+t%9;ufCases.push({n,ops:Array.from({length:12},()=>[random()%3?'union':'find',random()%n,random()%n])});}
for(const example of ufCases){
  const label=Array.from({length:example.n},(_,i)=>i),trace=M.unionFindTrace(example);equal(trace.length,example.ops.length+1);
  example.ops.forEach(([kind,a,b],i)=>{
    if(kind==='union'){const from=label[a],to=label[b];for(let v=0;v<example.n;v++)if(label[v]===from)label[v]=to;}
    const state=trace[i+1];
    for(const key of ['plain','packed']){const root=v=>{let x=v,guard=0;while(state[key][x]!==x){x=state[key][x];assert(++guard<=example.n,'parent cycle');}return x;};for(let x=0;x<example.n;x++)for(let y=0;y<example.n;y++)equal(root(x)===root(y),label[x]===label[y],'connectivity vs label propagation');}
    assert(state.packedDepth<=state.plainDepth);equal(state.plain.map((p,v)=>p===v),state.packed.map((p,v)=>p===v),'both forests keep the same representatives');checks++;
  });
}
{const chain=M.unionFindTrace(M.ufExamples[0]).at(-1);equal(chain.packed[0],4,'path compression points to the representative');assert(chain.plainDepth>chain.packedDepth);checks++;}
// Segment tree: every query against plain sums, every point update against a rebuilt tree.
for(const array of [M.segArray,[7],[2,9,4],[1,2,3,4,5,6,7,8,9,10,11]]){
  const n=array.length;
  for(let left=0;left<n;left++)for(let right=left;right<n;right++){
    const last=M.segmentTrace(array,{kind:'query',left,right}).at(-1);let expected=0;for(let i=left;i<=right;i++)expected+=array[i];
    equal(last.total,expected,'segment query vs plain sum');
    for(const v of last.visited){const nd=last.nodes.find(x=>x.node===v.node);equal(v.kind,nd.hi<left||right<nd.lo?'outside':left<=nd.lo&&nd.hi<=right?'inside':'partial','node relation');}
    equal(last.visited.filter(v=>v.kind==='inside').reduce((sum,v)=>sum+last.tree[v.node],0),expected,'inside nodes sum');
    assert(last.visited.length<=4*Math.ceil(Math.log2(n+1))+4);checks++;
  }
  for(let index=0;index<n;index++){
    const value=index*3+11,last=M.segmentTrace(array,{kind:'update',index,value}).at(-1),updated=[...array];updated[index]=value;
    equal(last.array,updated,'updated array');equal(last.tree[1],updated.reduce((x,y)=>x+y,0),'root sum');
    for(const node of last.nodes)equal(last.tree[node.node],updated.slice(node.lo,node.hi+1).reduce((x,y)=>x+y,0),'every node equals its range sum');
    equal(last.path.every(node=>{const nd=last.nodes.find(x=>x.node===node);return nd.lo<=index&&index<=nd.hi;}),true,'only nodes containing the index are touched');
  }
}
// Static entry must stay usable in opaque-origin sandbox: classic local assets only.
const entry=fs.readFileSync(path.join(__dirname,'../demos/index.html'),'utf8');
assert(!entry.includes('type="module"'));assert(!/https?:\/\//.test(entry));
for(const asset of ['models.js','app.js','styles.css'])assert(entry.includes(asset));
checks+=5;
// Every published demo link must point to a reviewed, runnable entry.
const root=path.resolve(__dirname,'..'),manifest=JSON.parse(fs.readFileSync(path.join(root,'lessons.json'),'utf8'));
const demoIds=new Set(['binary-search','bfs','dijkstra','prefix-sum','two-opt','annealing','nearest-neighbor','beam-search','destroy-repair','paired-compare','union-find','segment-tree']),linked=new Set();
for(const lesson of manifest.lessons){
  for(const file of ['lesson.md',...(lesson.pages||[]).map(page=>page.file)]){
    const body=fs.readFileSync(path.join(root,'lessons',lesson.lessonId,file),'utf8');
    for(const match of body.matchAll(/https:\/\/git\.readiz\.com\/h-contest-lesson\/demos\/[^)\s]+/g)){
      const url=new URL(match[0]);equal(url.pathname,'/h-contest-lesson/demos/index.html');
      equal([...url.searchParams.keys()],['demo']);assert(demoIds.has(url.searchParams.get('demo')));checks++;
      linked.add(url.searchParams.get('demo'));
    }
  }
}
equal([...linked].sort(),[...demoIds].sort(),'all reviewed demos have a lesson entry point');
console.log(`PASS ${checks} checks: lower_bound, BFS, Dijkstra, prefix sums, open-path 2-opt, annealing, nearest neighbor, beam search, destroy/repair, paired comparison, union-find, segment tree, sandbox entry.`);
