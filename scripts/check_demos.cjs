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
// ---- Practical-lesson demos: every value is recomputed here by separate code, and the lesson text must contain the same numbers. ----
const lessonText=name=>fs.readFileSync(path.join(__dirname,'../lessons',name,'lesson.md'),'utf8');
const tableAfter=(text,marker)=>{const at=text.indexOf(marker);assert(at>=0,'missing marker '+marker);return text.slice(at).split('\n').slice(1).filter(l=>l.trim()!=='').slice(0,40).filter((l,i,a)=>a.slice(0,i+1).every(x=>x.startsWith('|')));};
const cells=line=>line.split('|').slice(1,-1).map(c=>c.trim());
// assignment-moves: a fresh makespan computation for every neighbor, exhaustive optimum, and the lesson's 11-row table.
{
  const text=lessonText('assignment-local-search'),T=M.amTime,n=T.length,m=T[0].length;
  const fresh=assign=>{const load=Array(m).fill(0);for(let j=0;j<n;j++)load[assign[j]]+=T[j][assign[j]];return load;};
  const neighborsOf=assign=>{const out=[];for(let j=0;j<n;j++)for(let k=0;k<m;k++)if(k!==assign[j]){const a=[...assign];a[j]=k;out.push(a);}for(let x=0;x<n;x++)for(let y=x+1;y<n;y++)if(assign[x]!==assign[y]){const a=[...assign];a[x]=assign[y];a[y]=assign[x];out.push(a);}return out;};
  let optimum=Infinity;for(let code=0;code<m**n;code++){const a=[];let c=code;for(let j=0;j<n;j++){a.push(c%m);c=Math.floor(c/m);}optimum=Math.min(optimum,Math.max(...fresh(a)));}
  equal(optimum,9,'brute force optimum of the lesson example');equal(M.amOptimum(T).makespan,9);
  const handtime=tableAfter(text,'<!-- check:handtime -->').slice(2).map(cells);equal(handtime.map(r=>[Number(r[1]),Number(r[2])]),T,'processing times equal the lesson table');
  const start=M.amExamples[0].start;equal(start,[0,1,1,0,1]);equal(fresh(start),[14,14]);
  const first=M.assignmentMovesTrace(M.amExamples[0],'improve',2),startNeighbors=first.find(s=>s.neighbors.length).neighbors;
  equal(startNeighbors.length,11,'five moves and six swaps');equal(neighborsOf(start).length,11);
  startNeighbors.forEach((nb,i)=>{const expected=neighborsOf(start)[i];equal(nb.assign,expected,'neighbor order');equal(nb.loads,fresh(expected),'neighbor loads vs full recompute');equal(nb.makespan,Math.max(...fresh(expected)));});
  const rows=tableAfter(text,'<!-- check:hand -->').slice(2).map(cells);equal(rows.length,12);
  equal(rows[0].slice(1).map(Number),[14,14,14],'lesson start row');
  startNeighbors.forEach((nb,i)=>equal(rows[i+1],[nb.label,...nb.loads.map(String),String(nb.makespan)],'demo neighbor equals lesson table row'));
  assert(first.at(-1).phase==='done'&&first.at(-1).makespan===14&&first.length===13);checks++;
  assert(startNeighbors.every(nb=>nb.makespan>14),'every neighbor is worse');checks++;
  const allowed=M.assignmentMovesTrace(M.amExamples[0],'allow',2),keyStates=allowed.filter(s=>['worsen','accept'].includes(s.phase));
  equal(keyStates.map(s=>s.makespan),[15,12,9],'14 -> 15 -> 12 -> 9');equal(allowed.at(-1).makespan,9);
  equal(keyStates.map(s=>s.phase),['worsen','accept','accept']);
  for(const mode of ['improve','allow'])for(const job of [1,2,4]){
    const trace=M.assignmentMovesTrace(M.amExamples[0],mode,job);
    for(const s of trace){equal(s.loads,fresh(s.assign),'state loads vs recompute');for(const nb of s.neighbors)equal(nb.loads,fresh(nb.assign));}
    const last=trace.at(-1);equal(last.phase,'done');assert(neighborsOf(last.assign).every(a=>Math.max(...fresh(a))>=last.makespan),'stopped at a local optimum');checks++;
  }
  equal(M.assignmentMovesTrace(M.amExamples[0],'allow',1).at(-1).makespan,14,'a different worsening move can get stuck');
  // Random instances: neighbors by differential loads equal full recomputation, and the run ends in a local optimum.
  for(let test=0;test<60;test++){
    const nn=3+test%5,mm=2+test%3,time=Array.from({length:nn},()=>Array.from({length:mm},()=>1+random()%9)),start2=Array.from({length:nn},()=>random()%mm);
    const f=a=>{const l=Array(mm).fill(0);a.forEach((k,j)=>{l[k]+=time[j][k];});return l;};
    const ex={time,start:start2};
    for(const mode of ['improve','allow']){const trace=M.assignmentMovesTrace(ex,mode,0);
      for(const s of trace){equal(s.loads,f(s.assign));for(const nb of s.neighbors){equal(nb.loads,f(nb.assign));equal(nb.makespan,Math.max(...f(nb.assign)));}}
      for(let i=1;i<trace.length;i++)if(trace[i].phase==='accept')assert(trace[i].makespan<trace[i-1].makespan);
      equal(trace.at(-1).phase,'done');assert(trace.at(-1).makespan>=M.amOptimum(time).makespan);checks+=2;}
  }
}
// route-insertion: permutation enumeration for every assignment, plus the lesson's 21/29, 41/39/43 and 23/23.
{
  const text=lessonText('assignment-with-routes'),D=M.riDrivers,P=M.riPassengers;
  const dist=(a,b)=>Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1]);
  const driverLoad=(d,order)=>{let at=D[d],sum=0;for(const p of order){sum+=dist(at,P[p].s)+dist(P[p].s,P[p].e);at=P[p].e;}return sum;};
  let globalBest=Infinity,bestSets=[];
  for(let mask=0;mask<16;mask++){const sets=[[],[]];for(let p=0;p<4;p++)sets[(mask>>p)&1].push(p);const loads=sets.map((set,d)=>Math.min(...permutations(set).map(o=>driverLoad(d,o))));const value=Math.max(...loads);if(value<globalBest){globalBest=value;bestSets=[mask];}else if(value===globalBest)bestSets.push(mask);}
  equal(globalBest,23,'permutation-exhaustive optimum');equal(bestSets,[0b0110],'unique optimum: passengers 0 and 3 vs 1 and 2');
  equal(P.map(p=>dist(p.s,p.e)),[5,5,7,11],'ride distances');
  equal(M.riStart.map((r,d)=>driverLoad(d,r)),[21,29],'start loads');
  const trace=M.routeInsertionTrace(3),inserts=trace.filter(s=>s.phase==='insert');
  equal(inserts.map(s=>Math.max(driverLoad(0,s.routes[0]),driverLoad(1,s.routes[1]))),[41,39,43],'insertion maxima');
  equal(inserts.map(s=>[driverLoad(0,s.routes[0]),driverLoad(1,s.routes[1])]),[[41,10],[39,10],[43,10]]);
  const swapStates=trace.filter(s=>s.phase==='swap');equal(swapStates.map(s=>s.candidates.at(-1).max),[23,29]);
  equal(trace.at(-1).routes.map((r,d)=>driverLoad(d,r)),[23,23],'swap gives 23/23');equal(trace.at(-1).routes,[[3,0],[1,2]]);
  equal(trace.at(-1).phase,'done');assert(trace.at(-1).improved);checks++;
  for(let p=0;p<4;p++){const t=M.routeInsertionTrace(p);for(const s of t){s.routes.forEach((r,d)=>{const load=s.loads[d];equal(load.total,driverLoad(d,r),'load vs independent');equal(load.ride+load.empty,load.total);equal(load.ride,r.reduce((a,q)=>a+dist(P[q].s,P[q].e),0));});equal([...s.routes[0],...s.routes[1]].sort(),s.phase==='detach'?[0,1,2,3].filter(q=>q!==p):[0,1,2,3],'every passenger once, except while detached');}}
  for(const s of M.routeInsertionTrace(1).filter(x=>x.phase==='insert'))assert(s.routes[0].includes(1)||s.routes[1].includes(1));
  const driverText='기사 0은 (2,7), 기사 1은 (9,2)에서 출발하고',passText=P.map((p,i)=>`승객 ${i} (${p.s[0]},${p.s[1]})→(${p.e[0]},${p.e[1]}) 탑승 ${dist(p.s,p.e)}`).join(', ');
  assert(text.includes(driverText)&&text.includes(passText),'lesson coordinates equal the demo');checks++;
  assert(text.includes('부하는 21과 29입니다')&&text.includes('맨 앞은 41, 승객 2 뒤는 39, 맨 끝은 43')&&text.includes('23과 23'),'lesson values');checks++;
  assert(text.includes('| **{0,3} / {1,2}** | 24 / 27 → 27 | 23 (3→0) / 23 (1→2) | **23** |'),'lesson table optimum row');checks++;
}
// bucket-search: exhaustive nearest search, ring counts and the one-ring-early mistake.
{
  const text=lessonText('large-input-search'),ex=M.bkExample,list=ex.deliveries;
  const brute=(alive,stock,at,items)=>{let best=Infinity;for(const i of alive)if(stock[items[i][2]]>0)best=Math.min(best,Math.abs(items[i][0]-at[0])+Math.abs(items[i][1]-at[1]));return best;};
  const exact=M.bucketSearchTrace(ex,false),early=M.bucketSearchTrace(ex,true);
  equal(exact.filter(s=>s.phase==='pick'||s.phase==='done').map(s=>s.history.at(-1).dist),[3,3,4],'lesson distances');
  equal(exact.at(-1).history.map(h=>h.min),[3,3,4]);assert(exact.at(-1).history.every(h=>h.correct));checks++;
  equal(early.find(s=>s.phase==='pick').history[0].dist,4,'early cut picks distance 4');equal(early.find(s=>s.phase==='pick').history[0].min,3);assert(!early.find(s=>s.phase==='pick').history[0].correct);checks++;
  const handRows=tableAfter(text,'<!-- check:hand -->').slice(2).map(cells);equal(handRows.length,3);
  const finals=exact.filter(s=>s.phase==='pick'||s.phase==='done');
  finals.forEach((s,i)=>{const h=s.history[i],sp=exact.filter(x=>x.pick===i+1);const rings=Math.max(...sp.filter(x=>x.phase==='scan').map(x=>x.ring))+1;
    equal(handRows[i],[`${i+1}번째`,`(${h.from[0]},${h.from[1]})`,String(rings),`${h.inspected} / ${h.remaining}`,`배송 ${h.id} (${list[h.id][0]},${list[h.id][1]}) ${h.type}`,String(h.dist),String(h.min)],'lesson hand table row');});
  const listText=list.map((d,i)=>`${i} (${d[0]},${d[1]}) ${d[2]}`).join(', ');assert(text.includes(listText),'delivery list equals the lesson');checks++;
  assert(text.includes('센터는 (5,5)에 있고 A를 1개, B를 2개 가집니다'));checks++;
  // Independent ring walk on random instances.
  for(let test=0;test<120;test++){
    const side=16,cell=[1,2,4,8][test%4],count=3+random()%14,types=['A','B','C'];
    const deliveries=Array.from({length:count},()=>[random()%side,random()%side,types[random()%3]]),stock0={A:random()%3,B:random()%3,C:random()%2};
    const example={side,cell,center:[random()%side,random()%side],stock:stock0,deliveries,picks:Math.min(4,count)};
    for(const earlyMode of [false,true]){
      const trace=M.bucketSearchTrace(example,earlyMode),alive=new Set(deliveries.map((_,i)=>i)),stock={...stock0};let at=[...example.center];
      for(const h of trace.at(-1).history){
        const truth=brute(alive,stock,at,deliveries);equal(h.min,truth,'reported minimum equals brute force');
        if(!earlyMode)equal(h.dist,truth,'exact ring search equals exhaustive search');
        equal(h.dist,Math.abs(deliveries[h.id][0]-at[0])+Math.abs(deliveries[h.id][1]-at[1]),'distance is Manhattan');
        const scans=trace.filter(s=>s.pick===h.pick&&s.phase==='scan'),last=scans.at(-1);
        const gy=Math.floor(at[0]/cell),gx=Math.floor(at[1]/cell),ringMax=last.ring;
        let inspected=0;for(const i of alive){const cy=Math.floor(deliveries[i][0]/cell),cx=Math.floor(deliveries[i][1]/cell);if(Math.max(Math.abs(cy-gy),Math.abs(cx-gx))<=ringMax)inspected++;}
        equal(h.inspected,inspected,'inspected count equals items in the viewed rings');equal(h.remaining,alive.size);
        alive.delete(h.id);stock[h.type]--;at=[deliveries[h.id][0],deliveries[h.id][1]];checks++;
      }
    }
  }
  // The early-cut variant is wrong on at least one random instance, and the exact one never is.
  let wrong=0;for(let test=0;test<200;test++){const example={side:16,cell:4,center:[random()%16,random()%16],stock:{A:1,B:2},deliveries:Array.from({length:12},()=>[random()%16,random()%16,['A','B','C'][random()%3]]),picks:3};if(M.bucketSearchTrace(example,true).at(-1).history.some(h=>!h.correct))wrong++;assert(M.bucketSearchTrace(example,false).at(-1).history.every(h=>h.correct));}
  assert(wrong>0,'early cut is detected as wrong');checks+=2;
}
// boundary-delta: quadratic pair sums, differential formula and the score formula.
{
  const text=lessonText('reading-the-score'),ex=M.bdExample;
  const pairSum=ps=>{let e=0;for(let i=0;i<ps.length;i++)for(let j=i+1;j<ps.length;j++)e+=Math.abs(ps[i][1]-ps[j][1])+Math.abs(ps[i][2]-ps[j][2]);return e;};
  const score=(e0,e,used,limit)=>Math.floor(1000000*Math.pow(Math.max(0,e0-e)/e0,2))+Math.floor((limit-used)/100);
  equal(pairSum(ex.particles),42,'E0 by pairs');
  const trace=M.boundaryDeltaTrace(ex,ex.calls);
  equal(trace.map(s=>s.entropy),[42,40,40,38,38],'42 -> 40 -> 38 with a failed call between');
  equal(trace.map(s=>s.boundSum),trace.map(s=>s.entropy),'boundary sum equals pair sum');
  equal(trace.map(s=>s.used),[0,1,2,3,3]);equal(trace.at(-1).score.ratioPart+trace.at(-1).score.bonus,score(42,38,3,800));equal(score(42,38,3,800),9077);
  equal(trace[1].call.formula,-2);equal(trace[1].call.full,-2);equal(trace[3].call.formula,-2);equal(trace[3].call.full,-2);equal(trace[2].call.ok,false);
  equal([trace[1].call.before.value,trace[1].call.after.value],[6,4]);equal([trace[3].call.before.value,trace[3].call.after.value],[6,4]);
  const ps=ex.particles.map(p=>`${p[0]}(${p[1]},${p[2]})`).join(' ');assert(text.includes(`입자 5개 \`${ps}\``),'lesson particles equal the demo');checks++;
  const colText=trace[0].bounds.col.map(b=>`${b.left}×${b.right}`).join(', '),rowText=trace[0].bounds.row.map(b=>`${b.left}×${b.right}`).join(', ');
  assert(text.includes(`열 경계는 각각 ${colText}로 합 ${trace[0].colSum}, 행 경계는 ${rowText}로 합 ${trace[0].rowSum}`),'boundary split equals the lesson figure text');checks++;
  assert(text.includes('42 → 40')&&text.includes('40 → 38')&&text.includes('**9077**')&&text.includes('한도는 `4 × 5 × 40 = 800`'));checks++;
  // Random grids, random (including illegal) calls, compared against an independent quadratic recomputation.
  for(let test=0;test<120;test++){
    const H=2+random()%5,W=2+random()%5,all=[];for(let y=0;y<H;y++)for(let x=0;x<W;x++)all.push([y,x]);
    for(let i=all.length-1;i>0;i--){const j=random()%(i+1);[all[i],all[j]]=[all[j],all[i]];}
    const count=2+random()%Math.max(1,Math.min(6,H*W-1)),particles=all.slice(0,count).map((p,i)=>['ABCDEFGH'[i],p[0],p[1]]),limit=H*W*40;
    const calls=Array.from({length:8},()=>[particles[random()%count][0],random()%4]);
    const result=M.boundaryDeltaTrace({H,W,limit,particles},calls),dy=[-1,0,1,0],dx=[0,1,0,-1];
    let cur=particles.map(p=>[...p]),used=0;const e0=pairSum(cur);
    calls.forEach(([name,dir],i)=>{
      const p=cur.find(q=>q[0]===name),ny=p[1]+dy[dir],nx=p[2]+dx[dir];used++;
      const legal=ny>=0&&ny<H&&nx>=0&&nx<W&&!cur.some(q=>q[1]===ny&&q[2]===nx),before=pairSum(cur);
      if(legal)p.splice(1,2,ny,nx);
      const s=result[i+1];equal(s.call.ok,legal,'legal move');equal(s.entropy,pairSum(cur),'entropy after call');equal(s.boundSum,s.entropy,'boundary sum');equal(s.used,used);
      equal(s.particles,cur,'particle positions');
      if(legal){equal(s.call.formula,pairSum(cur)-before,'differential formula equals full recomputation');equal(s.call.full,pairSum(cur)-before);}
      equal(s.score.ratioPart+s.score.bonus,score(e0,pairSum(cur),used,limit),'score formula');checks++;
    });
  }
}
// mirror-policy: BFS distance by relaxation, path gain by layered dynamic programming, brute-force targets.
{
  const text=lessonText('observe-and-act'),ex=M.mpExample,N=M.mpN;
  const valueMap=cellsList=>{const v={};cellsList.forEach(([y,x,val])=>{v[y*N+x]=val;});return v;};
  const independent=(value,seen,at,left)=>{
    const dist=Array.from({length:N},()=>Array(N).fill(Infinity));dist[at[0]][at[1]]=0;
    for(let pass=0;pass<N*2;pass++)for(let y=0;y<N;y++)for(let x=0;x<N;x++)for(const[dy,dx]of[[1,0],[-1,0],[0,1],[0,-1]]){const yy=y+dy,xx=x+dx;if(yy>=0&&yy<N&&xx>=0&&xx<N)dist[y][x]=Math.min(dist[y][x],dist[yy][xx]+1);}
    const gain=Array.from({length:N},()=>Array(N).fill(-Infinity));gain[at[0]][at[1]]=0;
    const order=[];for(let y=0;y<N;y++)for(let x=0;x<N;x++)if(dist[y][x]>0&&dist[y][x]<=left)order.push([y,x]);order.sort((a,b)=>dist[a[0]][a[1]]-dist[b[0]][b[1]]);
    for(const[y,x]of order){let g=-Infinity;for(const[dy,dx]of[[1,0],[-1,0],[0,1],[0,-1]]){const yy=y-dy,xx=x-dx;if(yy>=0&&yy<N&&xx>=0&&xx<N&&dist[yy][xx]===dist[y][x]-1)g=Math.max(g,gain[yy][xx]);}gain[y][x]=g+(seen.has(y*N+x)?0:(value[y*N+x]||0));}
    return {dist,gain};
  };
  const aroundOf=(value,seen,ty,tx)=>{let s=0;for(let y=0;y<N;y++)for(let x=0;x<N;x++){const d=Math.abs(y-ty)+Math.abs(x-tx);if(d>=1&&d<=3&&!seen.has(y*N+x))s+=value[y*N+x]||0;}return s;};
  const verify=(cellsList,start,budget,weight)=>{
    const value=valueMap(cellsList);
    [1,2].forEach(policy=>{
      const run=M.mpRun({start,cells:cellsList},policy,budget,weight);
      run.forEach(tick=>{
        if(!tick.pick)return;
        const seen=new Set(tick.seen),ind=independent(value,seen,tick.at,tick.left),wanted=[];
        for(let y=0;y<N;y++)for(let x=0;x<N;x++){if(ind.dist[y][x]>0&&ind.dist[y][x]<=tick.left&&!seen.has(y*N+x)&&value[y*N+x]>0)wanted.push({y,x,d:ind.dist[y][x],g:ind.gain[y][x],h:aroundOf(value,seen,y,x),key:(ind.gain[y][x]+weight*aroundOf(value,seen,y,x))/(ind.dist[y][x]+1)});}
        equal(tick.pick.candidates.length,wanted.length,'candidate count');
        for(const c of tick.pick.candidates){const w=wanted.find(q=>q.y===c.y&&q.x===c.x);assert(w,'candidate exists');equal([c.d,c.g,c.h],[w.d,w.g,w.h],'d, g, h vs independent');assert(Math.abs(c.key-w.key)<1e-9);checks++;}
        let target=null;for(const w of wanted){if(target===null||(policy===1?(w.d<target.d||(w.d===target.d&&w.g>target.g)):w.key>target.key))target=w;}
        equal(tick.pick.target,[target.y,target.x],`policy ${policy} target vs brute-force choice`);
      });
      let score=0;const seenWalk=new Set([start[0]*N+start[1]]);run.slice(1).forEach(t=>{const k=t.at[0]*N+t.at[1];if(!seenWalk.has(k))score+=value[k]||0;seenWalk.add(k);equal(t.score,score,'running score');});
      equal(run.at(-1).left+run.length-1,budget,'moves used + left = budget');
    });
  };
  verify(ex.cells,ex.start,6,0.1);
  for(const budget of [3,6,9])for(const weight of [0,0.1,1])verify(ex.cells,ex.start,budget,weight);
  for(let test=0;test<40;test++){const cellsList=Array.from({length:3+random()%6},()=>[random()%8,random()%8,1+random()%30]).filter((c,i,a)=>a.findIndex(d=>d[0]===c[0]&&d[1]===c[1])===i);verify(cellsList,[random()%8,random()%8],4+random()%8,[0,0.1,1][random()%3]);}
  const trace=M.mirrorPolicyTrace(ex,6,0.1),first=trace[0].policies;
  const table=first[1].pick.candidates.map(c=>`| (${c.y},${c.x}) | ${c.d} | ${c.g} | ${c.h} | ${M.fmtKey(c.key)} |`);
  for(const row of table)assert(text.includes(row),'lesson key table row '+row);checks+=table.length;
  equal(first[1].pick.target,[2,6]);equal(first[0].pick.target,[2,2]);
  const targets=policy=>M.mpRun(ex,policy,6,0.1).filter(t=>t.pick).map(t=>`(${t.pick.target[0]},${t.pick.target[1]})`).join(', ');
  equal([targets(1),targets(2)],['(2,2), (1,1), (0,0)','(2,6)']);
  const last=trace.at(-1).policies;equal([last[0].score,last[1].score],[7,100]);equal([6-last[0].left,6-last[1].left],[5,3]);
  assert(text.includes('| 1 | (2,2), (1,1), (0,0) | 5 | 7 |')&&text.includes('| 2 | (2,6) | 3 | 100 |'),'lesson summary table');checks++;
  assert(text.includes('시작은 `(2,3)`이고 남은 이동은 6번')&&text.includes('(100 + 0.1 × 40) / (3 + 1) = 26.0'));checks++;
  const gridRows=['| 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |','| 1 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |','| 2 | 0 | 0 | 2 | S | 0 | 40 | 60 |'];for(const r of gridRows)assert(text.includes(r));checks+=3;
  equal(ex.cells.map(c=>c[2]).sort((a,b)=>a-b),[2,2,3,40,60],'map values equal the lesson grid');
  assert(trace.some(s=>s.policies[0].seen.length>1)&&trace.at(-1).policies[0].seen.length===6&&trace.at(-1).policies[1].seen.length===4,'seen grows with each visit');checks++;
}
// Static entry must stay usable in opaque-origin sandbox: classic local assets only.
const entry=fs.readFileSync(path.join(__dirname,'../demos/index.html'),'utf8');
assert(!entry.includes('type="module"'));assert(!/https?:\/\//.test(entry));
for(const asset of ['models.js','app.js','styles.css'])assert(entry.includes(asset));
checks+=5;
// Every published demo link must point to a reviewed, runnable entry.
const root=path.resolve(__dirname,'..'),manifest=JSON.parse(fs.readFileSync(path.join(root,'lessons.json'),'utf8'));
const demoIds=new Set(['binary-search','bfs','dijkstra','prefix-sum','two-opt','annealing','nearest-neighbor','beam-search','destroy-repair','paired-compare','union-find','segment-tree','assignment-moves','route-insertion','bucket-search','boundary-delta','mirror-policy']),linked=new Set();
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
console.log(`PASS ${checks} checks: lower_bound, BFS, Dijkstra, prefix sums, open-path 2-opt, annealing, nearest neighbor, beam search, destroy/repair, paired comparison, union-find, segment tree, assignment moves, route insertion, bucket search, boundary delta, mirror policy, sandbox entry.`);
