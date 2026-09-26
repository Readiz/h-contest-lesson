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
// Static entry must stay usable in opaque-origin sandbox: classic local assets only.
const entry=fs.readFileSync(path.join(__dirname,'../demos/index.html'),'utf8');
assert(!entry.includes('type="module"'));assert(!/https?:\/\//.test(entry));
for(const asset of ['models.js','app.js','styles.css'])assert(entry.includes(asset));
checks+=5;
// Every published demo link must point to a reviewed, runnable entry.
const root=path.resolve(__dirname,'..'),manifest=JSON.parse(fs.readFileSync(path.join(root,'lessons.json'),'utf8'));
const demoIds=new Set(['binary-search','bfs','dijkstra','prefix-sum','two-opt','annealing']),linked=new Set();
for(const lesson of manifest.lessons){
  for(const file of ['lesson.md',...(lesson.pages||[]).map(page=>page.file)]){
    const body=fs.readFileSync(path.join(root,'lessons',lesson.lessonId,file),'utf8');
    for(const match of body.matchAll(/https:\/\/blog\.readiz\.com\/h-contest-lesson\/demos\/[^)\s]+/g)){
      const url=new URL(match[0]);equal(url.pathname,'/h-contest-lesson/demos/index.html');
      equal([...url.searchParams.keys()],['demo']);assert(demoIds.has(url.searchParams.get('demo')));checks++;
      linked.add(url.searchParams.get('demo'));
    }
  }
}
equal([...linked].sort(),[...demoIds].sort(),'all reviewed demos have a lesson entry point');
console.log(`PASS ${checks} checks: lower_bound, BFS, Dijkstra, prefix sums, open-path 2-opt, annealing, sandbox entry.`);
