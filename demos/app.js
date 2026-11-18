(function () {
  'use strict';
  const M = window.LessonDemos;
  const $ = id => document.getElementById(id);
  const C = {blue:'#4166d9',blueLight:'#e8eeff',teal:'#158d84',tealLight:'#e0f3ee',orange:'#ba7926',orangeLight:'#fff0da',red:'#bd4d60',redLight:'#fff0f2',gray:'#e9eef6',ink:'#30445e',muted:'#8795a9'};
  const config = {
    'binary-search':{title:'같은 값이 있어도, 첫 위치를 찾기',subtitle:'lower_bound의 lo · hi · mid를 움직이며 탐색 구간이 줄어드는 이유를 확인합니다.',footnote:'인덱스는 0부터 시작합니다. [lo, hi)는 hi를 포함하지 않습니다. target이 배열의 모든 값보다 크면 n을 반환합니다.'},
    bfs:{title:'큐와 방문 표시를 함께 따라가기',subtitle:'한 칸씩 퍼지는 탐색과 큐의 순서를 나란히 봅니다. 큐에 넣는 순간 방문 처리합니다.',footnote:'상하좌우 이동의 비용은 모두 1입니다. 좌표는 (행, 열), 0부터 시작합니다. 전체 도달 가능 영역을 탐색한 뒤 최단 경로를 복원합니다.'},
    dijkstra:{title:'같은 정점이 큐에 여러 번 있어도',subtitle:'거리 갱신으로 남겨진 오래된 우선순위 큐 항목을 찾아봅니다. 간선은 화살표 방향으로만 이동합니다.',footnote:'가중치는 모두 0 이상입니다. 큐 표시는 최소값 우선으로 정렬한 논리적 내용이며, 실제 힙 내부 배열의 순서와 다를 수 있습니다.'},
    'prefix-sum':{title:'더하고, 빼고, 겹침을 돌려놓기',subtitle:'2차원 누적합의 포함배제 네 항이 각 칸에 남기는 계수를 색으로 확인합니다.',footnote:'행과 열은 0부터 시작합니다. 질의는 반열린 구간 [r1, r2) × [c1, c2)이고, P에는 0행과 0열을 추가합니다.'},
    'two-opt':{title:'전체 경로 대신, 경계만 계산하기',subtitle:'ORDERING의 열린 경로에서 구간을 뒤집습니다. 창고 0과 마지막 점의 역할에 주목하세요.',footnote:'비용은 맨해튼 거리입니다. 곡선·직선은 방문 순서를 나타내며 화면의 선 길이가 비용은 아닙니다. 마지막 점에서 창고로 돌아가는 간선은 없습니다.'},
    annealing:{title:'나빠진 현재 해, 보존되는 최고 해',subtitle:'온도와 악화 제안 크기를 바꾸며 수락 확률과 current / best의 차이를 실험합니다.',footnote:'최소화 예제입니다. T는 매 시도마다 0.88배로 냉각됩니다. 비교를 위해 제안 패턴과 난수 u는 고정했으며, 실제 탐색에서는 이웃 해와 난수를 생성합니다.'},
    'nearest-neighbor':{title:'가장 가까운 점만 고르면 생기는 일',subtitle:'창고 0에서 출발해 가장 가까운 미방문 점을 차례로 고릅니다. 후보 거리 비교와 누적 비용을 따라가 보세요.',footnote:'맨해튼 거리 |Δx| + |Δy|입니다. 같은 거리는 번호가 작은 점을 고르고, 마지막 점에서 창고로 돌아오는 간선은 없습니다. 최적 비용은 모든 순서를 비교한 값입니다.'},
    'beam-search':{title:'상위 W개만 남기는 가지치기',subtitle:'작은 결정 트리에서 깊이마다 후보를 평가하고 상위 W개만 남깁니다. 빔 너비를 바꿔 탐욕이 놓친 답이 살아남는지 확인합니다.',footnote:'각 깊이에서 선택지는 3개이고 평가값은 지금까지 얻은 점수의 합입니다. 값이 클수록 좋으며, 동점은 선택 번호가 작은 경로를 남깁니다.'},
    'destroy-repair':{title:'작은 이동으로 못 고치는 배치를 다시 채우기',subtitle:'배치의 일부를 제거하고 규칙대로 다시 채웁니다. 점수가 오르면 채택하고, 오르지 않으면 제거 전 배치로 되돌립니다.',footnote:'가치가 점수이며 광고는 겹칠 수 없는 1차원 띠 문제입니다. repair는 정해진 순서로 가장 왼쪽의 들어갈 수 있는 빈 구간에 놓습니다.'},
    'paired-compare':{title:'같은 입력에서 A와 B의 차이를 쌓기',subtitle:'입력별 점수 차이를 하나씩 쌓으며 평균, 표준오차와 mean ± 2·stderr 구간이 변하는 모습을 봅니다.',footnote:'d = A − B이며 점수가 클수록 좋습니다. 표준편차는 n − 1로 나눈 표본 표준편차이고, 구간은 독립 표본과 근사 정규성을 가정한 거친 근사입니다.'},
    'union-find':{title:'부모를 따라 올라가 대표 찾기',subtitle:'union과 find를 순서대로 실행하며 parent 배열과 숲이 바뀌는 과정을 봅니다. 경로 압축이 없는 숲과 있는 숲을 나란히 비교합니다.',footnote:'union(a, b)은 a의 대표 밑에 있던 트리를 b의 대표에 연결합니다. 크기 기준 합치기는 쓰지 않아 경로 압축의 효과가 잘 보입니다.'},
    'segment-tree':{title:'구간 질의가 방문하는 노드',subtitle:'구간 합 질의에서 노드를 완전 포함, 일부 겹침, 무관으로 나누고, 점 갱신에서는 경로의 합이 다시 계산되는 모습을 봅니다.',footnote:'노드 번호는 루트 1, 자식은 2i와 2i+1입니다. 구간은 양 끝을 포함하는 [lo, hi]이고 배열 인덱스는 0부터 시작합니다.'},
    'assignment-moves':{title:'이웃을 하나씩 평가해 최대 부하 보기',subtitle:'작업을 기계에 배정한 상태에서 한 작업 이동과 두 작업 교환을 모두 계산합니다. 개선만 받을 때와 한 번 나빠지는 이동을 허용할 때를 비교합니다.',footnote:'점수는 기계별 부하의 최댓값이고 낮을수록 좋습니다. 이웃은 이동 5개와 교환 6개이며, 가장 낮은 이웃이 동점이면 표의 앞쪽을 고릅니다. 전수 탐색의 최솟값은 2⁵ = 32개 배정을 모두 계산한 값입니다.'},
    'route-insertion':{title:'승객을 옮길 자리와 교환 비교하기',subtitle:'기사 2명이 승객 4명을 태우는 예시에서 승객 한 명을 다른 기사 경로의 어디에 끼울지 보고, 옮기기만으로 막힐 때 교환이 해결하는 과정을 봅니다.',footnote:'이동 거리는 맨해튼 거리입니다. 기사는 처음 위치에서 출발해 승객의 출발지, 도착지 순으로 움직이며, 마지막 승객 뒤에 돌아오는 구간은 없습니다. 점수는 두 기사 부하의 최댓값입니다.'},
    'bucket-search':{title:'칸을 한 겹씩 넓히며 가장 가까운 배송 찾기',subtitle:'지도를 칸으로 나누고 링 0에서 링 1로 넓히며 후보를 검사합니다. 종료 조건을 한 겹 일찍 끊으면 틀린 배송을 고르는 모습도 봅니다.',footnote:'거리는 맨해튼 거리이고 좌표는 (행, 열)입니다. 센터가 가진 상품만 실을 수 있으며 같은 거리면 먼저 만난 후보를 씁니다. 전수 탐색은 남은 배송 전부의 거리를 비교한 값입니다.'},
    'boundary-delta':{title:'경계 하나만 바뀌는 점수 계산',subtitle:'모든 쌍의 거리 합을 열·행 경계의 (한쪽 개수 × 반대쪽 개수) 합으로 보고, 입자를 옮길 때 차분식과 전체 재계산이 같은 값을 내는지 확인합니다.',footnote:'방향은 위, 오른쪽, 아래, 왼쪽이고 좌표는 (행, 열)입니다. 격자 밖이나 입자가 있는 칸으로의 호출은 실패하지만 사용 횟수는 셉니다. 점수는 내림한 정수입니다.'},
    'mirror-policy':{title:'가까운 칸 먼저 vs 이동당 이득',subtitle:'같은 지도와 이동 예산에서 두 정책이 고르는 목표와 경로, 누적 점수를 단계마다 나란히 비교합니다. 거울의 seen이 갱신되는 모습도 함께 봅니다.',footnote:'좌표는 (행, 열)이며 실제 지도는 30×30이고 화면에는 왼쪽 위 3×7만 그렸습니다. 정책 2의 RADIUS는 3, COST는 1입니다. 목표 하나마다 BFS로 거리와 경로 이득을 다시 계산합니다.'}
  };
  let id = new URLSearchParams(location.search).get('demo') || 'binary-search';
  if (!config[id]) id = 'binary-search';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let position=0, states=[], timer=null, context={}, options={target:4,example:0,source:0,rectangle:0,temperature:8,delta:6,width:1,count:12,mode:1,worse:2,passenger:3,early:0,p1:0,d1:1,p2:1,d2:1,p3:2,d3:0,budget:6,weight:0.1};
  const phaseNames={start:'준비',compare:'비교',move:'구간 축소',done:'완료',pop:'꺼내기',enqueue:'발견',stale:'오래된 항목',relax:'거리 갱신',skip:'유지',term:'포함배제',remove:'기존 경계',add:'새 경계',candidate:'후보 확인',trial:'수락 판단',scan:'후보 비교',visit:'이동',expand:'후보 생성',prune:'가지치기',destroy:'제거',repair:'다시 채우기',judge:'채택 판단',sample:'표본 추가',find:'find',union:'union',outside:'겹치지 않음',inside:'완전 포함',partial:'일부 겹침',point:'리프 갱신',node:'내려가기',recalc:'재계산',accept:'받아들임',worsen:'나쁜 이동 허용',detach:'경로에서 빼기',insert:'끼워 보기',swap:'교환 시도',stop:'탐색 종료',pick:'고르기',shift:'입자 이동',fail:'실패'};
  const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=value=>value===null?'∞':value;
  const signed=v=>v>0?`+${v}`:String(v);
  const svg=(content,height=260)=>`<svg class="viz" viewBox="0 0 360 ${height}" role="img" aria-label="${esc(config[id].title)}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${C.muted}"/></marker><marker id="arrow-hot" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${C.teal}"/></marker></defs>${content}</svg>`;
  const text=(x,y,value,extra='')=>`<text x="${x}" y="${y}" text-anchor="middle" ${/\bfill=/.test(extra)?'':`fill="${C.ink}"`} ${extra}>${esc(value)}</text>`;
  const title=value=>`<p class="visual-title">${value}</p>`;
  const metric=(label,value,type='')=>`<div class="metric ${type}"><small>${label}</small><strong>${value}</strong></div>`;
  const legend=items=>items.map(([color,label])=>`<span><i class="swatch" style="--swatch:${color}"></i>${label}</span>`).join('');
  const chips=(values,cls='')=>values.length?`<div class="chips">${values.map(value=>`<span class="chip ${cls}">${value}</span>`).join('')}</div>`:'<p class="empty">비어 있음</p>';
  const select=(key,label,values)=>`<label class="setting">${label}<select id="option-${key}" data-option="${key}">${values.map(([v,t])=>`<option value="${v}" ${Number(options[key])===Number(v)?'selected':''}>${t}</option>`).join('')}</select></label>`;
  const range=(key,label,min,max,step)=>`<label class="setting" for="option-${key}"><span>${label} <output id="value-${key}">${options[key]}</output></span><input id="option-${key}" data-option="${key}" type="range" min="${min}" max="${max}" step="${step}" value="${options[key]}" aria-label="${label}"></label>`;
  function setup() {
    document.title=config[id].title+' · 알고리즘 실험실';
    $('title').textContent=config[id].title;$('subtitle').textContent=config[id].subtitle;$('footnote').textContent=config[id].footnote;
    if(id==='binary-search') $('settings').innerHTML=select('target','찾을 값 target',[-1,1,4,5,7,10,12].map(n=>[n,`${n}${n===4?' · 중복값':n===12?' · 모든 값보다 큼':n===-1?' · 모든 값보다 작음':''}`]));
    else if(id==='bfs') $('settings').innerHTML=select('example','지도 선택',M.bfsExamples.map((e,i)=>[i,e.name]));
    else if(id==='dijkstra') $('settings').innerHTML=select('source','시작 정점',[[0,'S · 오래된 큐 항목 확인'],[2,'B · 도달하지 못하는 정점 확인']]);
    else if(id==='prefix-sum') $('settings').innerHTML=select('rectangle','질의 영역',[ [0,'가운데 영역 · [1, 3) × [1, 4)'],[1,'맨 위 · 왼쪽 경계 포함'],[2,'오른쪽 아래 한 칸'],[3,'전체 행렬']]);
    else if(id==='two-opt') $('settings').innerHTML=select('example','경로 예제',M.routes.map((e,i)=>[i,e.name]));
    else if(id==='nearest-neighbor') $('settings').innerHTML=select('example','점 배치 예제',M.nnExamples.map((e,i)=>[i,e.name]));
    else if(id==='beam-search') $('settings').innerHTML=select('example','결정 트리',M.beamExamples.map((e,i)=>[i,e.name]))+select('width','빔 너비 W',[[1,'W = 1 · 탐욕'],[2,'W = 2'],[3,'W = 3']]);
    else if(id==='destroy-repair') $('settings').innerHTML=select('example','배치 예제',M.drExamples.map((e,i)=>[i,e.name]));
    else if(id==='paired-compare') $('settings').innerHTML=select('example','실험 예제',M.pairedExamples.map((e,i)=>[i,e.name]))+range('count','사용할 입력 수',2,30,1);
    else if(id==='union-find') $('settings').innerHTML=select('example','연산 예제',M.ufExamples.map((e,i)=>[i,e.name]));
    else if(id==='segment-tree') $('settings').innerHTML=select('example','질의 예제',M.segExamples.map((e,i)=>[i,e.name]));
    else if(id==='assignment-moves'){const ex=M.amExamples[0],now=Math.max(...M.amLoads(ex.time,ex.start)),worse=M.amNeighbors(ex.time,ex.start).filter(n=>n.kind==='move'&&n.makespan>=now);$('settings').innerHTML=select('mode','탐색 방식',[[0,'개선만 받기'],[1,'한 번 나빠지는 이동 허용']])+select('worse','허용할 나쁜 이동',worse.map(n=>[n.job,`${n.label} · 최대 ${n.makespan}`]));}
    else if(id==='route-insertion') $('settings').innerHTML=select('passenger','옮길 승객',M.riExamples.map((e,i)=>[i,e.name]));
    else if(id==='bucket-search') $('settings').innerHTML=select('early','종료 조건',[[0,'정확한 조건 · bestDist ≤ (r − 1) × 칸 크기'],[1,'한 겹 일찍 끊기 · bestDist ≤ r × 칸 크기']]);
    else if(id==='boundary-delta'){const names=M.bdExample.particles.map((p,i)=>[i,`입자 ${p[0]}`]),dirs=[[0,'위'],[1,'오른쪽'],[2,'아래'],[3,'왼쪽']];$('settings').innerHTML=[1,2,3].map(n=>select('p'+n,`호출 ${n} 입자`,names)+select('d'+n,`호출 ${n} 방향`,dirs)).join('');}
    else if(id==='mirror-policy') $('settings').innerHTML=select('budget','이동 예산',[[3,'3번'],[6,'6번 · 본문 예시'],[9,'9번']])+select('weight','정책 2의 WEIGHT',[[0,'0 · 주변 값 무시'],[0.1,'0.1 · 본문 예시'],[1,'1.0 · 주변 값을 크게 믿음']]);
    else $('settings').innerHTML=range('temperature','시작 온도 T',0,20,0.5)+range('delta','악화 제안 기본 Δ',1,20,1);
    $('settings').querySelectorAll('[data-option]').forEach(input=>input.addEventListener('input',()=>{options[input.dataset.option]=Number(input.value);const out=$('value-'+input.dataset.option);if(out)out.value=input.value;rebuild();}));
    rebuild();
  }
  function rebuild() {
    stop();position=0;
    if(id==='binary-search') {context={array:[1,2,4,4,4,7,9,10]};states=M.lowerBoundTrace(context.array,options.target);}
    if(id==='bfs') {context=M.bfsExamples[options.example];states=M.bfsTrace(context.rows);}
    if(id==='dijkstra') {context=M.graph;states=M.dijkstraTrace(context,options.source);}
    if(id==='prefix-sum') {context={array:M.matrix,rectangle:[[1,1,3,4],[0,0,2,3],[3,4,4,5],[0,0,4,5]][options.rectangle]};Object.assign(context,M.prefixTrace(context.array,context.rectangle));states=context.states;}
    if(id==='two-opt') {context=M.routes[options.example];states=M.twoOptTrace(context.points,context.order,context.left,context.right);}
    if(id==='annealing') {states=M.annealingTrace(options.temperature,options.delta);const costs=states.flatMap(s=>[s.current,s.best]);context={ymin:Math.min(...costs)-5,ymax:Math.max(...costs)+5};}
    if(id==='nearest-neighbor') {context=M.nnExamples[options.example];states=M.nearestNeighborTrace(context.points);}
    if(id==='beam-search') {context=M.beamExamples[options.example];states=M.beamSearchTrace(context,options.width);}
    if(id==='destroy-repair') {context=M.drExamples[options.example];states=M.destroyRepairTrace(context);}
    if(id==='paired-compare') {const ex=M.pairedExamples[options.example],count=options.count,diffs=ex.a.map((x,i)=>x-ex.b[i]).slice(0,count);states=M.pairedTrace(ex,count);const edge=states.slice(3).flatMap(s=>s.stats.stderr===null?[]:[Math.abs(s.stats.low),Math.abs(s.stats.high)]);context={count,diffs,maxAbs:Math.max(1,...diffs.map(Math.abs)),axis:Math.max(1,...(edge.length?edge:[1]),0)*1.15};}
    if(id==='union-find') {context=M.ufExamples[options.example];states=M.unionFindTrace(context);context={...context,rows:Math.max(...states.map(s=>Math.max(s.plainDepth,s.packedDepth)))+1};}
    if(id==='segment-tree') {context={example:M.segExamples[options.example]};states=M.segmentTrace(M.segArray,context.example);}
    if(id==='assignment-moves') {context=M.amExamples[0];states=M.assignmentMovesTrace(context,options.mode?'allow':'improve',options.worse);}
    if(id==='route-insertion') {context={passenger:options.passenger};states=M.routeInsertionTrace(options.passenger);}
    if(id==='bucket-search') {context=M.bkExample;states=M.bucketSearchTrace(context,!!options.early);}
    if(id==='boundary-delta') {context=M.bdExample;const names=context.particles.map(p=>p[0]);states=M.boundaryDeltaTrace(context,[1,2,3].map(n=>[names[options['p'+n]],options['d'+n]]));}
    if(id==='mirror-policy') {context=M.mpExample;states=M.mirrorPolicyTrace(context,options.budget,options.weight);}
    $('timeline').max=states.length-1;render();
  }
  function renderBinary(s) {
    const a=context.array, w=37, start=13;
    let content=text(176,30,`target = ${options.target}`,'font-size="13" font-weight="700"');
    for(let i=0;i<=a.length;i++){
      const x=start+i*w,active=i>=s.lo&&i<s.hi,upper=i===s.hi,found=s.phase==='done'&&i===s.lo;
      const fill=found||upper?C.tealLight:i===s.mid?C.orangeLight:active?C.blueLight:'#f3f5f9';
      content+=`<rect x="${x}" y="87" width="32" height="48" rx="7" fill="${fill}" stroke="${found||upper?C.teal:i===s.mid?C.orange:active?'#a7b9f0':'#dfe5ef'}" ${i===a.length?'stroke-dasharray="3 3"':''}/>`;
      content+=text(x+16,116,i===a.length?'n':a[i],`font-size="18" font-weight="700" opacity="${active||upper||found||i===a.length?1:.5}"`)+text(x+16,154,i,'font-size="10"');
      if(i===s.mid) content+=text(x+16,72,'mid',`font-size="10" font-weight="800" fill="${C.orange}"`);
    }
    const lx=start+s.lo*w+16,hx=start+s.hi*w+16;
    content+=`<path d="M${lx} 170 v14" stroke="${C.blue}" stroke-width="2"/>`+text(lx,199,`lo ${s.lo}`,`font-size="10" font-weight="700" fill="${C.blue}"`);
    content+=`<path d="M${hx} 170 v40" stroke="${C.teal}" stroke-width="2"/>`+text(hx,225,`hi ${s.hi}`,`font-size="10" font-weight="700" fill="${C.teal}"`);
    $('visual').innerHTML=title('탐색 범위 · [lo, hi)')+svg(content,248);
    $('legend').innerHTML=legend([[C.blueLight,'미비교 원소 [lo, hi)'],[C.orangeLight,'이번 비교 mid'],[C.tealLight,s.phase==='done'?'확정한 첫 위치':'hi · 답이 될 수 있는 경계']]);
    $('metrics').innerHTML=metric('lo · 왼쪽 경계',s.lo,'accent')+metric('hi · 오른쪽 경계',s.hi)+metric('mid',s.mid===null?'—':s.mid)+metric('미비교 원소',s.hi-s.lo);
    $('details').innerHTML='<p class="detail-title">유지하는 조건</p><div class="formula">i &lt; lo → a[i] &lt; target<br>i ≥ hi → a[i] ≥ target</div><p class="note">미비교 원소 범위 [lo, hi)와 달리, 답 후보 위치 [lo, hi]는 hi도 포함합니다. 같은 값을 만나도 더 왼쪽 위치를 확인합니다.</p>';
  }
  function renderBfs(s) {
    const rows=context.rows,h=rows.length,w=rows[0].length,cell=44,x0=48,y0=28,path=new Set(s.path),queued=new Set(s.queue);
    let content='';
    for(let r=0;r<h;r++) for(let c=0;c<w;c++) {
      const v=r*w+c,wall=rows[r][c]==='#',x=x0+c*cell,y=y0+r*cell;
      const fill=wall?'#516079':v===s.current?C.orangeLight:path.has(v)?C.tealLight:queued.has(v)?C.blueLight:s.distance[v]>=0?'#edf2f8':'#fff';
      content+=`<rect x="${x}" y="${y}" width="39" height="39" rx="6" fill="${fill}" stroke="${v===s.focus?C.blue:path.has(v)?C.teal:'#d8e0ec'}" stroke-width="${v===s.focus?2.5:1}"/>`;
      if(!wall){const label=rows[r][c]==='S'?'S':rows[r][c]==='G'?'G':s.distance[v]>=0?s.distance[v]:'';content+=text(x+19.5,y+25,label,'font-size="16" font-weight="700"');if('SG'.includes(rows[r][c])&&s.distance[v]>=0) content+=text(x+32,y+11,s.distance[v],'font-size="8"');}
    }
    for(let c=0;c<w;c++)content+=text(x0+c*cell+19.5,17,c,'font-size="9"');
    for(let r=0;r<h;r++)content+=text(33,y0+r*cell+24,r,'font-size="9"');
    $('visual').innerHTML=title('격자 안 숫자 = 시작점에서의 최단 거리')+svg(content,260);
    $('legend').innerHTML=legend([[C.orangeLight,'현재 확장'],[C.blueLight,'큐에서 대기'],['#edf2f8','방문 완료'],[C.tealLight,'복원한 최단 경로'],['#516079','벽']]);
    const goal=rows.join('').indexOf('G');
    $('metrics').innerHTML=metric('큐 크기',s.queue.length,'accent')+metric('방문한 칸',s.distance.filter(d=>d>=0).length)+metric('도착점 거리',s.distance[goal]===-1?'—':s.distance[goal],s.path.length?'good':'')+metric('현재 거리',s.current===null?'—':s.distance[s.current]);
    $('details').innerHTML='<p class="detail-title">QUEUE · 왼쪽이 먼저 나옵니다</p>'+chips(s.queue.map((v,i)=>`(${Math.floor(v/w)},${v%w}) <b>d${s.distance[v]}</b>`))+'<p class="note">visited는 distance ≠ −1인 칸입니다. 큐에 넣을 때 표시하므로 같은 칸이 중복 삽입되지 않습니다.</p>';
  }
  function renderDijkstra(s) {
    let content='';
    context.edges.forEach(([a,b,w],i)=>{
      const [x1,y1]=context.points[a],[x2,y2]=context.points[b],dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy),hot=s.edge===i;
      const ax=x1+dx/len*21,ay=y1+dy/len*21,bx=x2-dx/len*23,by=y2-dy/len*23;
      content+=`<path d="M${ax} ${ay} L${bx} ${by}" fill="none" stroke="${hot?C.teal:'#b8c4d5'}" stroke-width="${hot?3:1.6}" marker-end="url(#${hot?'arrow-hot':'arrow'})"/>`;
      const mx=(x1+x2)/2,my=(y1+y2)/2;
      content+=`<rect x="${mx-10}" y="${my-10}" width="20" height="19" rx="5" fill="${hot?C.tealLight:'#fff'}"/>`+text(mx,my+3,w,`font-size="11" font-weight="700" fill="${hot?C.teal:C.ink}"`);
    });
    context.nodes.forEach((name,i)=>{const [x,y]=context.points[i],hot=s.current===i;content+=`<circle cx="${x}" cy="${y}" r="21" fill="${hot&&s.phase==='stale'?C.redLight:hot?C.orangeLight:s.settled[i]?C.tealLight:C.blueLight}" stroke="${hot&&s.phase==='stale'?C.red:hot?C.orange:s.settled[i]?C.teal:'#a7b9f0'}" stroke-width="${hot?2.5:1.5}"/>`+text(x,y+5,name,'class="node-label"')+text(x,y+37,`d = ${fmt(s.distance[i])}`,'font-size="10" font-weight="650"');});
    $('visual').innerHTML=title('방향 그래프 · 간선 위 숫자 = 이동 비용')+svg(content,268);
    $('legend').innerHTML=legend([[C.orangeLight,'꺼낸 정점'],[C.tealLight,'최단 거리 확정'],[C.teal,'확인 중인 간선'],[C.redLight,'오래된 항목 무시']]);
    $('metrics').innerHTML=metric('꺼낸 (거리, 정점)',s.popped?`${s.popped[0]}, ${context.nodes[s.popped[1]]}`:'—',s.phase==='stale'?'':'accent')+metric('큐에 남은 항목',s.queue.length);
    $('details').innerHTML='<p class="detail-title">MIN PRIORITY QUEUE</p>'+(s.queue.length?`<div class="chips">${s.queue.map(([d,v])=>`<span class="chip ${d!==s.distance[v]?'stale':''}">(${d}, ${context.nodes[v]})</span>`).join('')}</div>`:'<p class="empty">비어 있음</p>')+'<p class="detail-title">현재 dist[]</p>'+chips(context.nodes.map((n,i)=>`${n}: <b>${fmt(s.distance[i])}</b>`))+'<p class="note">취소선은 이미 더 짧은 경로가 발견된 항목입니다. 큐에서 꺼낸 d가 현재 dist[v]와 다르면 건너뜁니다.</p>';
  }
  function renderPrefix(s) {
    const a=context.array,[r1,c1,r2,c2]=context.rectangle,cell=51,x0=53,y0=35;
    let content='';
    for(let r=0;r<a.length;r++)for(let c=0;c<a[0].length;c++){
      const k=s.coefficient[r][c],x=x0+c*cell,y=y0+r*cell;
      content+=`<rect x="${x}" y="${y}" width="46" height="46" rx="6" fill="${k===1?C.blueLight:k===-1?C.redLight:'#f4f6fa'}" stroke="${k===1?'#b0c0f0':k===-1?'#e4bec6':'#e0e6ef'}"/>`+text(x+23,y+28,a[r][c],'font-size="18" font-weight="700"');
      if(k!==0)content+=text(x+37,y+12,signed(k),`font-size="10" font-weight="750" fill="${k<0?C.red:C.blue}"`);
    }
    content+=`<rect x="${x0+c1*cell-3}" y="${y0+r1*cell-3}" width="${(c2-c1)*cell+1}" height="${(r2-r1)*cell+1}" rx="8" fill="none" stroke="${C.teal}" stroke-width="2.5" stroke-dasharray="5 3"/>`;
    for(let c=0;c<a[0].length;c++)content+=text(x0+c*cell+23,20,c,'font-size="10"');
    for(let r=0;r<a.length;r++)content+=text(35,y0+r*cell+28,r,'font-size="10"');
    $('visual').innerHTML=title('A 행렬 · 작은 +1 / −1은 현재까지의 포함 계수')+svg(content,255);
    $('legend').innerHTML=legend([[C.blueLight,'1번 포함'],[C.redLight,'1번 과하게 빠짐'],['#f4f6fa','계수 0'],[C.teal,'구하려는 영역']]);
    $('metrics').innerHTML=metric('현재 계산값',s.total,s.phase==='done'?'good':'accent')+metric('선택한 칸 수',(r2-r1)*(c2-c1));
    $('details').innerHTML='<p class="detail-title">네 항을 한 단계씩 적용</p><ol class="term-list">'+context.terms.map(([sign,r,c],i)=>`<li class="${position>i?'applied':''} ${s.term===i?'active':''}"><code>${sign>0?'+':'−'} P[${r}][${c}]</code><strong>${context.p[r][c]}</strong></li>`).join('')+'</ol><p class="detail-title">미리 계산한 P · 0행 / 0열 포함</p><table class="data-table"><thead><tr><th></th>'+context.p[0].map((_,c)=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>'+context.p.map((row,r)=>'<tr><th>'+r+'</th>'+row.map((v,c)=>`<td class="${s.term!==null&&context.terms[s.term][1]===r&&context.terms[s.term][2]===c?'highlight':''}">${v}</td>`).join('')+'</tr>').join('')+'</tbody></table>';
  }
  function renderTwoOpt(s) {
    const pts=context.points,flat=pts.every(p=>p[1]===pts[0][1]),maxX=Math.max(...pts.map(p=>p[0])),maxY=Math.max(1,...pts.map(p=>p[1]));
    const xy=pts.map(([x,y])=>[28+x/maxX*300,flat?152:205-y/maxY*150]);
    const candidate=s.phase==='candidate'||(s.phase==='done'&&s.delta<0),order=candidate?s.candidate:context.order;
    const boundary=(a,b,edges)=>edges.some(([x,y])=>(x===a&&y===b)||(x===b&&y===a));
    const edgePath=(a,b)=>{const [x1,y1]=xy[a],[x2,y2]=xy[b];return flat?`M${x1} ${y1} Q${(x1+x2)/2} ${y1-Math.max(34,Math.abs(x2-x1)*.65)} ${x2} ${y2}`:`M${x1} ${y1} L${x2} ${y2}`;};
    let content='';
    const newEdges=candidate?s.added:s.removed;
    for(let i=1;i<order.length;i++){const a=order[i-1],b=order[i],bound=boundary(a,b,newEdges),color=bound?(candidate?C.teal:C.red):'#adb9cd';content+=`<path d="${edgePath(a,b)}" fill="none" stroke="${color}" stroke-width="${bound?3:1.8}"/>`;}
    if(s.phase==='add'||s.phase==='candidate')s.added.forEach(([a,b])=>{content+=`<path d="${edgePath(a,b)}" fill="none" stroke="${C.teal}" stroke-width="3" ${s.phase==='add'?'stroke-dasharray="5 4"':''}/>`;});
    xy.forEach(([x,y],i)=>{const selected=context.order.indexOf(i)>=context.left&&context.order.indexOf(i)<=context.right;content+=`<circle cx="${x}" cy="${y}" r="14" fill="${i===0?C.ink:selected?C.blueLight:'#fff'}" stroke="${selected?C.blue:'#9aabc4'}" stroke-width="1.5"/>`+text(x,y+4,i,`font-size="15" font-weight="750" style="fill:${i===0?'#fff':C.ink}"`)+text(x,y+29,`(${pts[i][0]},${pts[i][1]})`,'font-size="10" stroke="#fff" stroke-width="6" stroke-linejoin="round" paint-order="stroke"');});
    content+=text(180,flat?222:265,candidate?'뒤집은 후보 경로':'현재 경로',`font-size="11" font-weight="750" fill="${candidate?C.teal:C.ink}"`);
    $('visual').innerHTML=title(`order[${context.left}..${context.right}] 반전 · ${context.right===context.order.length-1?'꼬리 포함':'양쪽 경계 존재'}`)+svg(content,flat?245:280);
    $('legend').innerHTML=legend([[C.blueLight,'뒤집는 구간'],[C.red,'기존 경계'],[C.teal,'새 경계'],['#adb9cd','비용이 보존되는 간선']]);
    $('metrics').innerHTML=metric('기존 전체 비용',s.oldCost)+metric('후보 전체 비용',position>=3?s.newCost:'—',position>=3?'good':'')+metric('기존 경계 합',s.before)+metric('경계 Δ',position>=2?signed(s.delta):'—',position>=2&&s.delta<0?'good':'accent');
    const edgeText=edges=>edges.map(([a,b])=>`${a}–${b}: ${M.manhattan(pts[a],pts[b])}`).join(' + ');
    $('details').innerHTML='<p class="detail-title">방문 순서 · 0 고정</p>'+chips(s.order.map((v,i)=>`${v}${i===0?' 창고':''}`))+'<p class="detail-title">바뀌는 경계만 더합니다</p><div class="formula">before = '+edgeText(s.removed)+'<br>after = '+(position>=2?edgeText(s.added):'다음 단계에서 확인')+'<br>Δ = '+(position>=2?`${s.after} − ${s.before} = ${signed(s.delta)}`:'after − before')+'</div><p class="note">'+(context.right===context.order.length-1?'오른쪽 경계가 없습니다. 마지막 점과 창고를 연결하는 가짜 복귀 간선을 더하지 않습니다.':'뒤집는 구간 내부의 거리는 대칭이므로 그대로입니다. 양쪽 바깥 연결 두 개만 바뀝니다.')+'</p>';
  }
  function renderAnnealing(s) {
    const t=s.temperature,delta=s.delta===null?options.delta:s.delta,p=M.acceptance(delta,t),draw=s.draw;
    let content=text(52,16,'수락 확률 P','font-size="10"');
    const x0=32,y0=32,w=294,h=97,maxDelta=M.annealingPlotMax(options.delta);
    [0,.5,1].forEach(v=>{const y=y0+h-v*h;content+=`<line x1="${x0}" y1="${y}" x2="326" y2="${y}" stroke="#e2e8f2"/>`+text(18,y+3,`${v*100}%`,'font-size="8"');});
    let path='';for(let i=0;i<=120;i++){const d=i/120*maxDelta;path+=`${i?'L':'M'}${x0+d/maxDelta*w},${y0+h-M.acceptance(d,t)*h} `;}
    content+=`<path d="${path}" stroke="${C.blue}" stroke-width="2.4" fill="none"/>`;
    [0,maxDelta/3,maxDelta*2/3,maxDelta].forEach(d=>content+=text(x0+d/maxDelta*w,y0+h+15,Number(d.toFixed(1)),'font-size="10"'));
    const px=x0+Math.max(0,Math.min(delta,maxDelta))/maxDelta*w,py=y0+h-p*h;
    content+=`<line x1="${px}" y1="${py}" x2="${px}" y2="${y0+h}" stroke="${C.orange}" stroke-dasharray="3 3"/><circle cx="${px}" cy="${py}" r="4" fill="${C.orange}"/>`+text(300,155,'악화량 Δ →','font-size="9"');
    const top=191,chartH=93,costY=v=>top+(context.ymax-v)/(context.ymax-context.ymin)*chartH;
    content+=text(76,176,'탐색 비용 · 작을수록 좋음','font-size="10"');
    [context.ymin,Math.round((context.ymin+context.ymax)/2),context.ymax].forEach(v=>{const y=costY(v);content+=`<line x1="32" y1="${y}" x2="326" y2="${y}" stroke="#e2e8f2"/>`+text(17,y+3,v,'font-size="8"');});
    ['current','best'].forEach(key=>{const color=key==='current'?C.blue:C.teal;content+=`<path d="${s.history.map((v,i)=>`${i?'L':'M'}${32+i/12*294},${costY(v[key])}`).join(' ')}" fill="none" stroke="${color}" stroke-width="${key==='best'?3:2}" ${key==='best'?'stroke-dasharray="4 3"':''}/>`;s.history.forEach((v,i)=>{content+=`<circle cx="${32+i/12*294}" cy="${costY(v[key])}" r="${key==='best'?2:3}" fill="${color}"/>`;});});
    [0,3,6,9,12].forEach(n=>content+=text(32+n/12*294,301,n,'font-size="9"'));
    $('visual').innerHTML=title('온도가 내려가면, 악화된 해를 덜 받아들입니다')+svg(content,317);
    $('legend').innerHTML=legend([[C.blue,'current · 현재 비용'],[C.teal,'best · 역대 최저 비용'],[C.orange,'이번 제안의 수락 확률']]);
    $('metrics').innerHTML=metric('current',s.current,'accent')+metric('best',s.best,'good')+metric('현재 온도 T',t.toFixed(2))+metric('제안 Δ',signed(delta));
    $('details').innerHTML='<p class="detail-title">'+(s.phase==='start'?'기본 Δ의 수락 확률 미리 보기':'이번 제안의 수락 판단')+'</p><div class="formula">P = '+(delta<=0?'1':t<=0?'0 (T = 0)':`exp(−${delta} / ${t.toFixed(2)})`)+'<br><span class="live-prob">'+(p*100).toFixed(1)+'%</span>'+(draw===null?'':` · u = ${draw.toFixed(2)}`)+'</div><div class="probability-meter" role="img" aria-label="수락 확률 '+(p*100).toFixed(1)+'%"><b style="width:'+p*100+'%"></b>'+(draw===null?'':`<span class="probability-marker" style="left:${draw*100}%"></span>`)+'</div>'+(s.accepted===null?'':`<span class="outcome ${s.accepted?'':'reject'}">${s.accepted?'수락 · current 이동':'거절 · current 유지'}</span>`)+ '<p class="note">Δ ≤ 0이면 확률 1로 수락합니다. Δ > 0이면 난수 u &lt; P일 때만 수락합니다. best는 늘 별도로 보존합니다.</p>';
  }
  const textAt=(x,y,value,anchor,extra='')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" ${/\bfill=/.test(extra)?'':`fill="${C.ink}"`} ${extra}>${esc(value)}</text>`;
  const f2=v=>(Math.round(v*100)/100).toFixed(2);
  const lPath=(a,b)=>`M${a[0]} ${a[1]} H${b[0]} V${b[1]}`;
  function renderNearest(s) {
    const pts=context.points,xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const scale=Math.min(40,270/Math.max(1,maxX-minX),140/Math.max(1,maxY-minY)),ox=180-(minX+maxX)/2*scale,height=Math.round(Math.max(150,(maxY-minY)*scale+120)),oy=60+maxY*scale;
    const xy=pts.map(([x,y])=>[ox+x*scale,oy-y*scale]),scanning=s.phase==='scan',candidate=new Map(s.candidates.map(c=>[c.v,c.dist]));
    let content='';
    if(scanning)s.candidates.forEach(c=>{const hot=c.v===s.chosen;content+=`<path d="${lPath(xy[s.current],xy[c.v])}" fill="none" stroke="${hot?C.orange:'#9fb2e6'}" stroke-width="${hot?3:1.4}" stroke-dasharray="5 4"/>`;});
    for(let i=1;i<s.order.length;i++){const last=i===s.order.length-1&&s.phase!=='scan';content+=`<path d="${lPath(xy[s.order[i-1]],xy[s.order[i]])}" fill="none" stroke="${last?C.teal:'#9aa9c0'}" stroke-width="${last?3.4:2.2}"/>`;}
    xy.forEach(([x,y],i)=>{const used=s.used[i],now=i===s.current,pick=scanning&&i===s.chosen;
      content+=`<circle cx="${x}" cy="${y}" r="14" fill="${i===0?C.ink:now?C.orangeLight:used?C.tealLight:candidate.has(i)?C.blueLight:'#fff'}" stroke="${now||pick?C.orange:used?C.teal:candidate.has(i)?C.blue:'#9aabc4'}" stroke-width="${now||pick?3:1.5}"/>`+text(x,y+5,i,`font-size="14" font-weight="750" style="fill:${i===0?'#fff':C.ink}"`)+text(x,y+29,`(${pts[i][0]},${pts[i][1]})`,'font-size="10" stroke="#fff" stroke-width="6" stroke-linejoin="round" paint-order="stroke"');
      if(candidate.has(i))content+=text(x,y-21,`d = ${candidate.get(i)}`,`font-size="11" font-weight="750" fill="${pick?C.orange:C.blue}"`);});
    $('visual').innerHTML=title('맨해튼 평면 · 선은 가로 후 세로로 이동한 길')+svg(content,height);
    $('legend').innerHTML=legend([[C.orangeLight,'현재 위치'],[C.tealLight,'방문 완료'],[C.blueLight,'이번 후보와 거리 d'],[C.orange,'가장 가까워 고른 점'],[C.ink,'창고 0']]);
    const total=pts.length;
    $('metrics').innerHTML=metric('누적 비용',s.cost,s.phase==='done'?'good':'accent')+metric('방문한 점',`${s.order.length} / ${total}`)+metric('남은 점',total-s.order.length)+metric('모든 순서의 최적',s.optimal?s.optimal.cost:'—',s.optimal&&s.optimal.cost===s.cost?'good':'');
    const legCosts=s.order.slice(1).map((v,i)=>M.manhattan(pts[s.order[i]],pts[v])),legs=s.order.slice(1).map((v,i)=>`${s.order[i]}→${v} <b>+${legCosts[i]}</b>`);
    $('details').innerHTML='<p class="detail-title">'+(scanning?`점 ${s.current}에서 후보 거리`:'후보 거리 · 비교 단계에서 표시')+'</p>'+(scanning?`<div class="chips">${s.candidates.map(c=>`<span class="chip ${c.v===s.chosen?'current':''}">${c.v}번 · d ${c.dist}${c.v===s.chosen?' · 선택':''}</span>`).join('')}</div>`:'<p class="empty">다음 단계에서 비교</p>')+'<p class="detail-title">방문 순서</p>'+chips(s.order.map((v,i)=>`${v}${i===0?' 창고':''}`))+'<p class="detail-title">이동 비용과 누적</p>'+(legs.length?chips(legs):'<p class="empty">아직 이동 없음</p>')+'<div class="formula">'+(legCosts.length?legCosts.join(' + ')+' = '+s.cost:'0')+'</div>'+(s.optimal?`<p class="note">최적 순서 ${s.optimal.order.join(' → ')}, 비용 ${s.optimal.cost}. ${s.cost>s.optimal.cost?`nearest neighbor가 ${s.cost-s.optimal.cost}만큼 더 깁니다.`:'이 입력에서는 nearest neighbor가 최적입니다.'}</p>`:'<p class="note">매 단계에서 가장 가까운 점만 봅니다. 같은 거리는 번호가 작은 점을 고르고, 마지막 점에서 창고로 돌아오는 비용은 없습니다.</p>');
  }
  const pathText=p=>p.join('-');
  function renderBeam(s) {
    const cw=114,rowH=23;let content='';
    for(let d=1;d<=3;d++){
      const x=6+(d-1)*(cw+4),layer=s.layers[d];
      content+=text(x+cw/2,14,`깊이 ${d}${layer?` · 후보 ${layer.length}`:''}`,'font-size="10" font-weight="750"');
      if(!layer){content+=`<rect x="${x}" y="22" width="${cw}" height="${rowH-3}" rx="6" fill="#fff" stroke="#dfe5ef" stroke-dasharray="3 3"/>`+text(x+cw/2,37,'대기','font-size="10"');continue;}
      [...layer].sort((a,b)=>b.score-a.score||a.path.join('').localeCompare(b.path.join(''))).forEach((c,i)=>{
        const y=22+i*rowH,fill=c.kept===null?C.blueLight:c.kept?C.tealLight:C.redLight,stroke=c.kept===null?'#a7b9f0':c.kept?C.teal:C.red,mark=c.kept===null?'·':c.kept?'✓':'✕';
        content+=`<rect x="${x}" y="${y}" width="${cw}" height="${rowH-3}" rx="6" fill="${fill}" stroke="${stroke}" ${c.kept===false?'stroke-dasharray="3 2"':''}/>`+textAt(x+5,y+14,`${mark} ${pathText(c.path)}`,'start',`font-size="10" font-weight="750"`)+textAt(x+cw-5,y+14,`+${c.gain}=${c.score}`,'end','font-size="10"');
      });
    }
    $('visual').innerHTML=title('깊이별 후보 · 왼쪽 = 선택 번호 경로, 오른쪽 = 이번 이득 = 누적 평가값')+svg(content,250);
    $('legend').innerHTML=legend([[C.blueLight,'· 평가만 한 후보'],[C.tealLight,'✓ 유지한 상위 W개'],[C.redLight,'✕ 버린 후보']]);
    const last=s.layers[s.layers.length-1],decided=last.length&&last.every(c=>c.kept!==null)&&s.depth>0,dropped=s.layers.slice(1).reduce((n,l)=>n+l.filter(c=>c.kept===false).length,0);
    $('metrics').innerHTML=metric('빔 너비 W',s.width,'accent')+metric('깊이',`${s.depth} / 3`)+metric('남은 후보',decided?last.filter(c=>c.kept).length:'—')+metric('지금까지 버린 후보',dropped);
    const keptNow=last.filter(c=>c.kept).sort((a,b)=>b.score-a.score),dropNow=last.filter(c=>c.kept===false).sort((a,b)=>b.score-a.score);
    $('details').innerHTML='<p class="detail-title">남은 후보 · 평가값 큰 순</p>'+(s.depth===0?'<p class="empty">아직 후보 없음</p>':decided?chips(keptNow.map(c=>`${pathText(c.path)} · ${c.score}`),'current'):'<p class="empty">가지치기 단계에서 결정</p>')+'<p class="detail-title">버린 후보</p>'+(dropNow.length?chips(dropNow.map(c=>`${pathText(c.path)} · ${c.score}`),'stale'):'<p class="empty">없음</p>')+(s.best?`<div class="formula">최종 ${pathText(s.best.path)} = ${s.best.score}<br>전수 최적 ${pathText(s.optimum.path)} = ${s.optimum.score}</div><span class="outcome ${s.best.score===s.optimum.score?'':'reject'}">${s.best.score===s.optimum.score?'최적을 찾음':`${s.optimum.score-s.best.score}만큼 놓침`}</span>`:'')+'<p class="note">큰 평가값이 좋습니다. 동점은 선택 번호가 작은 경로를 먼저 남깁니다. W를 바꿔 처음에 낮아 보이던 경로가 살아남는지 확인하세요.</p>';
  }
  const drColor={A:C.blueLight,B:C.tealLight,C:C.orangeLight,D:C.redLight,E:C.gray};
  function renderDestroy(s) {
    const x0=30,cw=30;let content='';
    const strip=(place,y,label)=>{
      let out=text(180,y-9,label,'font-size="11" font-weight="750"');
      for(let i=0;i<M.DR_LENGTH;i++)out+=`<rect x="${x0+i*cw}" y="${y}" width="${cw-2}" height="46" rx="5" fill="#fff" stroke="#e1e7f0" stroke-dasharray="3 3"/>`+text(x0+i*cw+cw/2-1,y+62,i,'font-size="9"');
      for(const [id,at] of Object.entries(place)){const it=M.drItems[id];out+=`<rect x="${x0+at*cw}" y="${y}" width="${it.w*cw-2}" height="46" rx="5" fill="${drColor[id]}" stroke="${C.ink}" stroke-width="1.2"/>`+text(x0+at*cw+it.w*cw/2-1,y+22,id,'font-size="15" font-weight="800"')+text(x0+at*cw+it.w*cw/2-1,y+38,`+${it.v}`,'font-size="10"');}
      return out;
    };
    content+=strip(s.current,28,`채택한 현재 배치 · 점수 ${s.currentScore}`)+strip(s.working,128,`작업 중 배치 · 점수 ${s.workingScore}`);
    $('visual').innerHTML=title(`${M.DR_LENGTH}칸 띠 · 광고 글자 아래 +숫자는 가치, 칸 번호는 0부터`)+svg(content,205);
    $('legend').innerHTML=legend([['#dfe5ef','빈 칸'],[C.blueLight,'A, B: 폭 2 · 가치 3'],[C.orangeLight,'C: 폭 4 · 가치 9'],[C.redLight,'D: 폭 1 · 가치 1'],[C.gray,'E: 폭 3 · 가치 2']]);
    $('metrics').innerHTML=metric('채택한 점수',s.currentScore,'accent')+metric('작업 점수',s.workingScore,s.phase==='repair'&&s.workingScore>s.currentScore?'good':'')+metric('시도',`${s.trial} / ${s.trials}`)+metric('제거한 광고',s.removed.length?s.removed.join(', '):'—');
    const status=id=>s.removed.includes(id)&&s.phase==='destroy'?'제거됨':id in s.working?`${s.working[id]}번 칸`:'미배치';
    $('details').innerHTML='<p class="detail-title">광고 목록</p><ol class="term-list">'+Object.keys(M.drItems).map(id=>{const it=M.drItems[id];return `<li class="${s.removed.includes(id)&&s.phase==='destroy'?'active':id in s.working?'applied':''}"><code>${id} · 폭 ${it.w} · 가치 ${it.v}</code><strong>${status(id)}</strong></li>`;}).join('')+'</ol>'+(s.accepted===undefined?'':`<span class="outcome ${s.accepted?'':'reject'}">${s.accepted?'채택 · 새 배치로 이동':'되돌림 · 제거 전 배치 유지'}</span>`)+'<p class="note">repair 규칙은 고정되어 있습니다. 한 개만 옮기는 작은 이동으로 못 고치는 배치는 여러 개를 제거해야 빈 구간이 합쳐집니다. 점수가 오르지 않으면 되돌립니다.</p>';
  }
  function renderPaired(s) {
    const x0=32,w=294;let content=text(180,14,'입력별 차이 d = A − B (막대가 위면 A가 높음)','font-size="10"');
    const maxAbs=context.maxAbs,zy=80,half=52,bw=Math.min(14,w/context.count*.72);
    content+=`<line x1="${x0}" y1="${zy}" x2="326" y2="${zy}" stroke="#9aabc4"/>`+text(18,zy+3,'0','font-size="9"');
    context.diffs.forEach((d,i)=>{const x=x0+(i+.5)*w/context.count,used=i<s.k,h=Math.abs(d)/maxAbs*half;content+=`<rect x="${x-bw/2}" y="${d>=0?zy-h:zy}" width="${bw}" height="${Math.max(1,h)}" rx="2" fill="${used?(d>=0?C.teal:C.red):'#f3f5f9'}" stroke="${used?'none':'#dfe5ef'}"/>`;});
    const ay=196;content+=text(180,152,'평균 ± 2·표준오차 구간 (0 기준선과 비교)','font-size="10"');
    const sc=v=>x0+(Math.max(-context.axis,Math.min(context.axis,v))+context.axis)/(2*context.axis)*w,zx=sc(0);
    content+=`<line x1="${x0}" y1="${ay}" x2="326" y2="${ay}" stroke="#e2e8f2" stroke-width="6"/><line x1="${zx}" y1="${ay-22}" x2="${zx}" y2="${ay+26}" stroke="${C.red}" stroke-width="2" stroke-dasharray="4 3"/>`+text(zx,ay+42,'0','font-size="10" font-weight="750"');
    const st=s.stats;
    if(st.stderr!==null){const lo=sc(st.low),hi=sc(st.high),mx=sc(st.mean);content+=`<line x1="${lo}" y1="${ay}" x2="${hi}" y2="${ay}" stroke="${st.verdict==='better'?C.teal:st.verdict==='worse'?C.red:C.orange}" stroke-width="7" stroke-linecap="round"/><circle cx="${mx}" cy="${ay}" r="5" fill="#fff" stroke="${C.ink}" stroke-width="2"/>`+text(Math.max(50,Math.min(310,mx)),ay-13,`평균 ${f2(st.mean)}`,'font-size="10" font-weight="750" stroke="#fff" stroke-width="3" paint-order="stroke"')+textAt(Math.max(lo-4,70),ay+19,`하한 ${f2(st.low)}`,'end','font-size="10" stroke="#fff" stroke-width="3" paint-order="stroke"')+textAt(Math.min(hi+4,290),ay+19,`상한 ${f2(st.high)}`,'start','font-size="10" stroke="#fff" stroke-width="6" stroke-linejoin="round" paint-order="stroke"');}
    else content+=text(180,ay+4,st.n===0?'표본을 추가하세요':'표본 2개부터 표준오차를 계산합니다','font-size="11"');
    $('visual').innerHTML=title(`입력 ${s.k} / ${context.count}개 사용 · 큰 점수가 좋은 문제`)+svg(content,255);
    $('legend').innerHTML=legend([[C.teal,'A가 높은 입력'],[C.red,'B가 높은 입력'],[C.orange,'0을 포함한 구간'],['#f3f5f9','아직 쌓지 않은 입력']]);
    const verdict={better:'A 개선 근거',worse:'A 악화 근거',unclear:'확정 불가',insufficient:'계산 불가',empty:'—'}[st.verdict];
    $('metrics').innerHTML=metric('표본 수 n',st.n,'accent')+metric('평균 차이',st.mean===null?'—':f2(st.mean))+metric('표준오차',st.stderr===null?'—':f2(st.stderr))+`<div class="metric ${st.verdict==='better'?'good':''}"><small>0 기준 판정</small><strong style="font-size:16px">${verdict}</strong></div>`;
    $('details').innerHTML='<p class="detail-title">계산식</p><div class="formula">mean = Σd / n'+(st.mean===null?'':` = ${f2(st.mean)}`)+'<br>stderr = std / √n'+(st.stderr===null?'':` = ${f2(st.std)} / √${st.n} = ${f2(st.stderr)}`)+'<br>구간 = mean ± 2·stderr'+(st.stderr===null?'':`<br>= [${f2(st.low)}, ${f2(st.high)}]`)+'</div>'+(st.stderr===null?'':`<span class="outcome ${st.verdict==='better'?'':'reject'}">${st.low>0?'하한 > 0':st.high<0?'상한 < 0':'구간이 0을 포함'}</span>`)+'<p class="detail-title">최근 차이 d</p>'+chips(s.diffs.slice(-6).map(d=>signed(d)))+'<p class="note">표본을 늘리면 표준오차가 줄어 구간이 좁아집니다. 독립 표본과 충분한 표본 수를 가정한 근사 구간입니다.</p>';
  }
  function forestLayout(parent) {
    const children=parent.map(()=>[]);parent.forEach((p,v)=>{if(p!==v)children[p].push(v);});
    const pos={};let slot=0;
    const walk=(v,d)=>{const kids=children[v];if(!kids.length)pos[v]={x:slot++,d};else{kids.forEach(k=>walk(k,d+1));pos[v]={x:(pos[kids[0]].x+pos[kids.at(-1)].x)/2,d};}};
    parent.forEach((p,v)=>{if(p===v)walk(v,0);});
    return pos;
  }
  function renderUnion(s) {
    const n=s.plain.length,step=28,top=40,panelH=top+context.rows*step+4,slotW=Math.min(40,300/n);let content='';
    const draw=(parent,y0,label,path)=>{
      const pos=forestLayout(parent),onPath=new Set(path||[]);
      let out=textAt(10,y0+14,label,'start','font-size="11" font-weight="750"');
      const px=v=>(360-(n-1)*slotW)/2+pos[v].x*slotW,py=v=>y0+top+pos[v].d*step;
      parent.forEach((p,v)=>{if(p!==v){const hot=onPath.has(v)&&onPath.has(p);out+=`<line x1="${px(v)}" y1="${py(v)}" x2="${px(p)}" y2="${py(p)}" stroke="${hot?C.orange:'#9aa9c0'}" stroke-width="${hot?3:1.6}"/>`;}});
      parent.forEach((p,v)=>{const root=p===v;out+=`<circle cx="${px(v)}" cy="${py(v)}" r="11" fill="${onPath.has(v)?C.orangeLight:root?C.tealLight:'#fff'}" stroke="${onPath.has(v)?C.orange:root?C.teal:'#9aabc4'}" stroke-width="${root||onPath.has(v)?2.4:1.4}"/>`+text(px(v),py(v)+4,v,'font-size="11" font-weight="750"');});
      return out;
    };
    content+=draw(s.plain,0,`경로 압축 없음 · 최대 깊이 ${s.plainDepth}`,s.path&&s.path.plain)+`<line x1="10" y1="${panelH}" x2="350" y2="${panelH}" stroke="#e2e8f2"/>`+draw(s.packed,panelH+2,`경로 압축 있음 · 최대 깊이 ${s.packedDepth}`,s.path&&s.path.packed);
    $('visual').innerHTML=title('부모를 따라 올라가면 대표(루트)가 나옵니다 · 위쪽이 루트')+svg(content,panelH*2+6);
    $('legend').innerHTML=legend([[C.tealLight,'대표(루트)'],[C.orangeLight,'이번 연산이 지난 원소'],['#c9d3e3','일반 원소']]);
    const roots=s.plain.filter((p,v)=>p===v).length,o=s.op===null?null:context.ops[s.op-1],opText=o?`${o[0]}(${o.slice(1).join(', ')})`:'시작';
    $('metrics').innerHTML=metric('연산',`${s.op||0} / ${context.ops.length}`,'accent')+metric('집합 수',roots)+metric('깊이 · 압축 없음',s.plainDepth)+metric('깊이 · 압축 있음',s.packedDepth,s.packedDepth<s.plainDepth?'good':'');
    const prev=states[Math.max(0,position-1)],table=(label,arr,before)=>`<p class="detail-title">${label}</p><table class="data-table"><thead><tr><th>원소</th>${arr.map((_,i)=>`<th>${i}</th>`).join('')}</tr></thead><tbody><tr><th>parent</th>${arr.map((p,i)=>`<td class="${p!==before[i]?'highlight':''}">${p}</td>`).join('')}</tr></tbody></table>`;
    $('details').innerHTML=`<p class="detail-title">현재 연산 · ${opText}</p>`+table('parent 배열 · 압축 없음',s.plain,prev.plain)+table('parent 배열 · 압축 있음',s.packed,prev.packed)+'<p class="note">강조한 칸은 이전 단계에서 값이 바뀐 parent입니다. 경로 압축은 find가 지나온 원소의 parent를 대표로 바꾸며 집합 구성은 바꾸지 않습니다.</p>';
  }
  const segKind={outside:'겹치지 않음',inside:'완전 포함',partial:'일부 겹침'},segMark={outside:'×',inside:'✓',partial:'△'};
  function renderSegment(s) {
    const n=s.array.length,sx=i=>24+i*44,level=node=>Math.floor(Math.log2(node)),cx=nd=>(sx(nd.lo)+sx(nd.hi))/2,cy=nd=>30+level(nd.node)*58,byId={};
    s.nodes.forEach(nd=>byId[nd.node]=nd);
    const kinds={};(s.visited||[]).forEach(v=>kinds[v.node]=v.kind);
    const pathSet=new Set(s.path||[]),redone=new Set(states.slice(0,position+1).filter(x=>x.phase==='recalc'||x.phase==='point').map(x=>x.current));
    let content='';
    s.nodes.forEach(nd=>{if(nd.node>1){const p=byId[nd.node>>1],on=kinds[nd.node]!==undefined||pathSet.has(nd.node);content+=`<line x1="${cx(p)}" y1="${cy(p)+17}" x2="${cx(nd)}" y2="${cy(nd)-17}" stroke="${on?C.orange:'#c4cedd'}" stroke-width="${on?2.2:1.2}"/>`;}});
    s.nodes.forEach(nd=>{
      const k=kinds[nd.node],isNow=s.current===nd.node,x=cx(nd),y=cy(nd);
      let fill='#fff',stroke='#aab8cf',mark='';
      if(s.kind==='query'&&k){fill=k==='inside'?C.tealLight:k==='partial'?C.orangeLight:'#eef1f6';stroke=k==='inside'?C.teal:k==='partial'?C.orange:'#9aa8bd';mark=segMark[k];}
      if(s.kind==='update'&&pathSet.has(nd.node)){fill=redone.has(nd.node)?C.tealLight:C.orangeLight;stroke=redone.has(nd.node)?C.teal:C.orange;mark=redone.has(nd.node)?'✓':'↓';}
      content+=`<rect x="${x-19}" y="${y-17}" width="38" height="34" rx="6" fill="${fill}" stroke="${isNow?C.blue:stroke}" stroke-width="${isNow?3:1.4}" ${k==='outside'?'stroke-dasharray="3 2"':''}/>`+text(x-3,y-4,nd.lo===nd.hi?`[${nd.lo}]`:`${nd.lo}-${nd.hi}`,'font-size="9"')+text(x,y+10,s.tree[nd.node],'font-size="13" font-weight="800"');
      if(mark)content+=text(x+13,y-7,mark,`font-size="10" font-weight="800" fill="${C.ink}"`);
    });
    if(s.kind==='query'){const a=sx(s.left)-19,b=sx(s.right)+19;content+=`<path d="M${a} 232 v6 H${b} v-6" fill="none" stroke="${C.teal}" stroke-width="2.4"/>`+text((a+b)/2,254,`질의 [${s.left}, ${s.right}]`,`font-size="11" font-weight="750" fill="${C.teal}"`);}
    else content+=`<path d="M${sx(s.index)} 236 v6" stroke="${C.orange}" stroke-width="3"/>`+text(sx(s.index),256,`a[${s.index}] 갱신`,`font-size="11" font-weight="750" fill="${C.orange}"`);
    for(let i=0;i<n;i++)content+=text(sx(i),228,i,'font-size="9"');
    $('visual').innerHTML=title('노드 안: 담당 구간과 저장된 합 · 기호 ✓ 포함 △ 일부 × 무관')+svg(content,268);
    $('legend').innerHTML=s.kind==='query'?legend([[C.tealLight,'✓ 완전 포함'],[C.orangeLight,'△ 일부 겹침'],['#eef1f6','× 겹치지 않음'],['#e1e7f0','방문 안 함']]):legend([[C.orangeLight,'↓ 갱신 경로'],[C.tealLight,'✓ 다시 계산함'],['#e1e7f0','그대로']]);
    const vis=s.visited||[];
    if(s.kind==='query'){
      $('metrics').innerHTML=metric('누적 합',s.total,s.phase==='done'?'good':'accent')+metric('방문한 노드',vis.length)+metric('완전 포함 노드',vis.filter(v=>v.kind==='inside').length)+metric('질의 구간',`[${s.left}, ${s.right}]`);
      $('details').innerHTML='<p class="detail-title">방문 순서</p>'+(vis.length?'<ol class="term-list">'+vis.map((v,i)=>{const nd=byId[v.node];return `<li class="${i===vis.length-1&&s.phase!=='done'?'active':'applied'}"><code>노드 ${v.node} [${nd.lo}, ${nd.hi}]</code><strong>${segKind[v.kind]}${v.kind==='inside'?` +${s.tree[v.node]}`:''}</strong></li>`;}).join('')+'</ol>':'<p class="empty">아직 방문 전</p>')+'<p class="note">완전히 포함된 노드의 저장된 합만 더하고, 일부만 겹치면 아래로 내려갑니다. 겹치지 않는 노드는 0을 돌려줍니다.</p>';
    } else {
      const path=s.path||[];
      $('metrics').innerHTML=metric('갱신 위치',`a[${s.index}]`,'accent')+metric('경로 노드',path.length)+metric('다시 계산한 노드',redone.size)+metric('루트 합',s.tree[1],s.phase==='done'?'good':'');
      $('details').innerHTML='<p class="detail-title">갱신 경로 · 위에서 아래</p>'+(path.length?'<ol class="term-list">'+path.map(node=>{const nd=byId[node];return `<li class="${s.current===node?'active':redone.has(node)?'applied':''}"><code>노드 ${node} [${nd.lo}, ${nd.hi}]</code><strong>${redone.has(node)?'합 '+s.tree[node]:'대기'}</strong></li>`;}).join('')+'</ol>':'<p class="empty">아직 내려가기 전</p>')+'<p class="note">리프를 바꾼 뒤 돌아오면서 지나온 노드만 두 자식의 합으로 다시 계산합니다. 경로 밖의 노드는 값이 그대로입니다.</p>';
    }
  }
  // ---- five practical-lesson demos: assignment-moves, route-insertion, bucket-search, boundary-delta, mirror-policy ----
  const rowTable=(head,rows,cls=[])=>`<table class="data-table"><thead><tr>${head.map((h,i)=>`<th class="${i===0?'left':''}">${h}</th>`).join('')}</tr></thead><tbody>${rows.map((r,ri)=>`<tr class="${cls[ri]||''}">${r.map((c,i)=>`<td class="${i===0?'left':''}">${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  function renderAssignment(s) {
    const time=context.time,m=time[0].length,x0=66,scale=11,rowH=36,barH=26,y0=24;
    const bars=(assign,loads,top,h,bh,hot)=>{let out='';for(let k=0;k<m;k++){const y=top+k*h;let x=x0;out+=textAt(x0-8,y+bh/2+4,`기계 ${k}`,'end','font-size="11" font-weight="700"');assign.forEach((mm,j)=>{if(mm!==k)return;const w=time[j][k]*scale;out+=`<rect x="${x}" y="${y}" width="${w-1.5}" height="${bh}" rx="3" fill="${hot.includes(j)?C.orangeLight:C.blueLight}" stroke="${hot.includes(j)?C.orange:'#a7b9f0'}"/>`+text(x+(w-1.5)/2,y+bh/2+4,j,'font-size="11" font-weight="800"');x+=w;});out+=textAt(x+4,y+bh/2+4,loads[k],'start','font-size="11" font-weight="800"');}return out;};
    let content=textAt(8,14,'현재 배정 · 칸 안 숫자 = 작업 번호, 폭 = 처리 시간','start','font-size="11"')+bars(s.assign,s.loads,y0,rowH,barH,s.changed);
    const yb=y0+m*rowH+10,mx=x0+s.makespan*scale,ox=x0+s.optimum*scale;
    content+=`<line x1="${mx}" y1="${y0-4}" x2="${mx}" y2="${yb-2}" stroke="${C.orange}" stroke-width="2" stroke-dasharray="4 3"/>`+text(mx,yb+10,`최대 ${s.makespan}`,`font-size="11" font-weight="800" fill="${C.orange}"`);
    content+=`<line x1="${ox}" y1="${y0-4}" x2="${ox}" y2="${yb+16}" stroke="${C.teal}" stroke-width="1.6" stroke-dasharray="2 3"/>`+text(ox,yb+26,`전수 최적 ${s.optimum}`,`font-size="11" font-weight="700" fill="${C.teal}"`);
    const nb=s.current===null?null:s.neighbors[s.current];
    if(nb){const top=yb+56;content+=textAt(8,top-8,`평가 중인 이웃 · ${nb.label}`,'start','font-size="11" font-weight="700"')+bars(nb.assign,nb.loads,top,24,18,nb.changed);}
    $('visual').innerHTML=title('기계별 부하 막대 · 점선 = 최대 부하')+svg(content,236);
    $('legend').innerHTML=legend([[C.blueLight,'배정된 작업'],[C.orangeLight,'이동·교환으로 자리가 바뀐 작업'],[C.orange,'현재 최대 부하'],[C.teal,'전수 탐색의 최솟값']]);
    const now=Math.max(...amLoadsOf(s.assign)),seen=s.neighbors.slice(0,s.evaluated),better=seen.filter(n=>n.makespan<now).length;
    $('metrics').innerHTML=metric('현재 최대 부하',s.makespan,s.phase==='done'&&s.makespan===s.optimum?'good':'accent')+metric('평가한 이웃',`${s.evaluated} / ${s.neighbors.length||'—'}`)+metric('더 낮은 이웃',seen.length?better:'—',better?'good':'')+metric('전수 최솟값',s.optimum);
    const rows=s.neighbors.map((n,i)=>i<s.evaluated?[n.label,...n.loads,n.makespan]:[n.label,...n.loads.map(()=>'—'),'—']),cls=s.neighbors.map((n,i)=>i===s.picked?'pick':i===s.current?'hot':i>=s.evaluated?'dim':'');
    $('details').innerHTML=`<p class="detail-title">이웃 ${s.neighbors.length||11}개의 평가값 · 현재 최대 ${s.makespan}</p>`+(s.neighbors.length?rowTable(['이웃',...time[0].map((_,k)=>`기계 ${k}`),'최대'],rows,cls):'<p class="empty">아직 평가 전</p>')+`<p class="note">이동은 두 기계의 부하만, 교환은 두 기계의 부하만 바뀝니다. 새 최댓값 = max(바뀐 두 기계, 나머지 기계). 모드 · ${s.mode==='allow'?'개선만 받다가 멈추면 한 번 나빠지는 이동을 허용':'개선만 받기'}.</p>`;
  }
  const amLoadsOf=assign=>M.amLoads(context.time,assign);
  function renderRoute(s) {
    const x0=58,scale=6.6,rowH=66,top=44,barH=26,maxLoad=Math.max(...s.loads.map(l=>l.total));
    let content=textAt(8,14,'기사별 이동 거리 · 파랑 = 탑승 구간, 주황 = 빈 차 구간','start','font-size="11"');
    s.routes.forEach((route,d)=>{
      const y=top+d*rowH,load=s.loads[d];let x=x0;
      content+=textAt(x0-8,y+barH/2-2,`기사 ${d}`,'end','font-size="11" font-weight="700"')+textAt(x0-8,y+barH/2+13,load.total,'end',`font-size="13" font-weight="800" fill="${load.total===maxLoad?C.orange:C.ink}"`);
      load.segments.forEach(seg=>{const w=seg.length*scale,ride=seg.kind==='ride',mine=seg.passenger===s.passenger;
        content+=`<rect x="${x}" y="${y}" width="${Math.max(w-1,1)}" height="${barH}" rx="3" fill="${ride?C.blueLight:C.orangeLight}" stroke="${mine?C.red:ride?'#a7b9f0':C.orange}" stroke-width="${mine?2.2:1}"/>`;
        if(w>=String(seg.length).length*7+3)content+=text(x+w/2,y+barH/2+4,seg.length,'font-size="11" font-weight="800"');
        if(ride)content+=text(x+w/2,y-5,`승객 ${seg.passenger}`,`font-size="11" font-weight="700" fill="${mine?C.red:C.muted}"`);
        x+=w;});
      content+=textAt(x0+2,y+barH+14,route.length?route.join(' → '):'경로 없음','start','font-size="11"');
    });
    const sx=x0+s.startMax*scale,yEnd=top+2*rowH-14;
    content+=`<line x1="${sx}" y1="${top-6}" x2="${sx}" y2="${yEnd}" stroke="${C.red}" stroke-width="1.6" stroke-dasharray="4 3"/>`+text(Math.min(sx,330),yEnd+14,`처음 최대 ${s.startMax}`,`font-size="11" font-weight="700" fill="${C.red}"`);
    $('visual').innerHTML=title(`승객 ${s.passenger} · 기사 ${s.owner}에서 기사 ${s.other}로 옮기기`)+svg(content,214);
    $('legend').innerHTML=legend([[C.blueLight,'탑승 구간(승객을 태운 거리)'],[C.orangeLight,'빈 차 구간(다음 승객에게 가는 거리)'],[C.red,'옮기는 승객 · 처음 최대']]);
    const mx=Math.max(...s.loads.map(l=>l.total));
    $('metrics').innerHTML=metric('기사 0 부하',s.loads[0].total)+metric('기사 1 부하',s.loads[1].total)+metric('두 기사의 최대',mx,mx<s.startMax?'good':'accent')+metric('처음 최대',s.startMax);
    const rows=s.candidates.map(c=>[c.label,c.routes[0].join('→')+' / '+c.routes[1].join('→'),c.max]),cls=s.candidates.map((c,i)=>i===s.candidate?(s.phase==='done'&&s.improved?'pick':'hot'):'');
    $('details').innerHTML='<p class="detail-title">거리 분해 · 탑승 + 빈 차</p>'+chips(s.loads.map((l,d)=>`기사 ${d}: 탑승 <b>${l.ride}</b> + 빈 차 <b>${l.empty}</b> = <b>${l.total}</b>`))+'<p class="detail-title">시도한 이웃</p>'+(rows.length?rowTable(['이웃','경로 0 / 1','최대'],rows,cls):'<p class="empty">아직 시도 전</p>')+'<p class="note">삽입 위치가 달라지면 빈 차 구간이 바뀌어도 탑승 구간은 담당자와 함께 움직입니다. 승객을 옮겨서 나빠져도 두 승객을 바꾸면 좋아질 수 있습니다.</p>';
  }
  function renderBucket(s) {
    const ex=context,u=20,x0=20,y0=18,side=ex.side,cell=ex.cell,G=side/cell;
    const viewed=new Set(s.viewedCells.map(c=>c[0]*G+c[1])),ringSet=new Set(s.ringCells.map(c=>c[0]*G+c[1])),aliveSet=new Set(s.alive),pickedIds=new Set(s.history.map(h=>h.id));
    let content='';
    for(let gy=0;gy<G;gy++)for(let gx=0;gx<G;gx++){const k=gy*G+gx;content+=`<rect x="${x0+gx*cell*u}" y="${y0+gy*cell*u}" width="${cell*u}" height="${cell*u}" fill="${ringSet.has(k)?C.orangeLight:viewed.has(k)?C.blueLight:'#fff'}" stroke="#9aabc4" stroke-width="1.4"/>`;}
    for(let i=0;i<=side;i++){const major=i%cell===0;if(!major)content+=`<line x1="${x0+i*u}" y1="${y0}" x2="${x0+i*u}" y2="${y0+side*u}" stroke="#eef1f6"/><line x1="${x0}" y1="${y0+i*u}" x2="${x0+side*u}" y2="${y0+i*u}" stroke="#eef1f6"/>`;}
    for(let c=0;c<side;c+=2)content+=text(x0+c*u+u/2,y0-5,c,'font-size="11"');
    for(let r=0;r<side;r+=2)content+=textAt(x0-4,y0+r*u+u/2+4,r,'end','font-size="11"');
    ex.deliveries.forEach(([y,x,type],i)=>{
      const cx=x0+x*u+u/2,cy=y0+y*u+u/2,gone=pickedIds.has(i),ok=s.stock[type]>0||gone,best=s.best&&s.best.id===i&&!gone;
      content+=`<circle cx="${cx}" cy="${cy}" r="8.5" fill="${gone?C.teal:type==='A'?C.tealLight:type==='B'?'#dfe7ff':'#eef1f6'}" stroke="${best?C.orange:gone?C.teal:type==='C'?'#9aa8bd':'#7f93c9'}" stroke-width="${best?3:1.4}" ${type==='C'&&!gone?'stroke-dasharray="3 2"':''}/>`+text(cx,cy+4,i,`font-size="11" font-weight="800" fill="${gone?'#fff':C.ink}"`);
    });
    const ax=x0+s.at[1]*u+u/2,ay=y0+s.at[0]*u+u/2;
    content+=`<path d="M${ax} ${ay-12} l12 12 l-12 12 l-12 -12 z" fill="none" stroke="${C.red}" stroke-width="2.2"/>`;
    $('visual').innerHTML=title(`${pickText(s)} · 칸 한 변 ${cell} · 다이아몬드 = 출발점 (${s.at[0]},${s.at[1]})`)+svg(content,y0+side*u+8);
    $('legend').innerHTML=legend([[C.orangeLight,'이번에 본 링'],[C.blueLight,'이미 본 링'],[C.tealLight,'A 배송'],['#dfe7ff','B 배송'],['#eef1f6','C 배송(재고 없음)'],[C.teal,'이미 고른 배송']]);
    const last=s.history.at(-1);
    $('metrics').innerHTML=metric('검사한 후보 / 남은 배송',`${s.inspected} / ${s.remaining}`,'accent')+metric('본 링',s.ring===null?'—':s.phase==='stop'?`0–${s.ring-1}`:`0–${s.ring}`)+metric('최선 거리',s.best?s.best.dist:'—')+metric('센터 재고',`A ${s.stock.A} · B ${s.stock.B}`);
    const rows=s.ringItems.map(it=>[`배송 ${it.id} (${it.y},${it.x}) ${it.type}`,it.ok?'가능':'재고 없음',it.ok?it.dist:'—']),cls=s.ringItems.map(it=>s.best&&it.id===s.best.id?'pick':it.ok?'':'dim');
    $('details').innerHTML=`<p class="detail-title">${s.ring===null?'링 검사':`링 ${s.ring}에서 검사한 후보`}</p>`+(rows.length?rowTable(['후보','싣기','거리'],rows,cls):`<p class="empty">${s.phase==='stop'||s.phase==='pick'||s.phase==='done'?'이번 단계에서 새로 검사한 후보 없음':'아직 검사 전'}</p>`)+'<p class="detail-title">고른 배송 · 전수 탐색과 대조</p>'+(s.history.length?'<ol class="term-list">'+s.history.map(h=>`<li class="${h.correct?'applied':'active'}"><code>${h.pick}번째 배송 ${h.id} ${h.type}</code><strong>거리 ${h.dist} · 최솟값 ${h.min} ${h.correct?'일치':'불일치'}</strong></li>`).join('')+'</ol>':'<p class="empty">아직 고르기 전</p>')+`<p class="note">종료 조건: ${s.early?'bestDist ≤ r × 칸 크기 (한 겹 일찍)':'bestDist ≤ (r − 1) × 칸 크기'}. 링 r의 칸은 출발 칸에서 칸 거리가 r이며, 그 안의 후보는 모두 (r − 1) × 칸 크기 + 1 이상 떨어져 있습니다.${last&&!last.correct?' 불일치한 고르기는 더 가까운 배송이 아직 보지 않은 링에 있었기 때문입니다.':''}</p>`;
  }
  const pickText=s=>s.pick?`${s.pick}번째 고르기`:'시작';
  const bdDirLabel=['위','오른쪽','아래','왼쪽'];
  function renderBoundary(s) {
    const u=52,x0=22,y0=34,W=s.W,H=s.H,ch=s.call&&s.call.ok?s.call:null;
    let content='';
    for(let r=0;r<H;r++)for(let c=0;c<W;c++)content+=`<rect x="${x0+c*u}" y="${y0+r*u}" width="${u}" height="${u}" fill="#fff" stroke="#c9d3e3"/>`;
    for(let c=0;c<W;c++)content+=text(x0+c*u+u/2,y0-18,c,'font-size="10"');
    for(let r=0;r<H;r++)content+=textAt(x0-6,y0+r*u+u/2+4,r,'end','font-size="10"');
    s.bounds.col.forEach(b=>{const hot=ch&&ch.axis==='col'&&ch.boundary===b.index,x=x0+(b.index+1)*u;content+=`<line x1="${x}" y1="${y0}" x2="${x}" y2="${y0+H*u}" stroke="${hot?C.orange:'#7f93c9'}" stroke-width="${hot?3:1.4}" stroke-dasharray="${hot?'':'4 3'}"/>`+text(x,y0-5,`${b.left}×${b.right}`,`font-size="11" font-weight="${hot?800:600}" fill="${hot?C.orange:C.blue}"`);});
    s.bounds.row.forEach(b=>{const hot=ch&&ch.axis==='row'&&ch.boundary===b.index,y=y0+(b.index+1)*u;content+=`<line x1="${x0}" y1="${y}" x2="${x0+W*u}" y2="${y}" stroke="${hot?C.orange:'#7f93c9'}" stroke-width="${hot?3:1.4}" stroke-dasharray="${hot?'':'4 3'}"/>`+textAt(x0+W*u+8,y+4,`${b.left}×${b.right}`,'start',`font-size="11" font-weight="${hot?800:600}" fill="${hot?C.orange:C.blue}"`);});
    s.particles.forEach(([name,y,x])=>{const cx=x0+x*u+u/2,cy=y0+y*u+u/2,moved=s.call&&s.call.name===name;content+=`<circle cx="${cx}" cy="${cy}" r="15" fill="${moved&&s.call.ok?C.orangeLight:moved?C.redLight:C.blueLight}" stroke="${moved&&s.call.ok?C.orange:moved?C.red:'#a7b9f0'}" stroke-width="${moved?2.6:1.5}"/>`+text(cx,cy+5,name,'font-size="14" font-weight="800"');});
    if(s.call){
      const dirs=[[-1,0],[0,1],[1,0],[0,-1]][s.call.dir],p=s.particles.find(q=>q[0]===s.call.name),sy=s.call.ok?p[1]-dirs[0]:p[1],sx=s.call.ok?p[2]-dirs[1]:p[2],fx=x0+sx*u+u/2,fy=y0+sy*u+u/2,tx=fx+dirs[1]*u*.62,ty=fy+dirs[0]*u*.62;
      content+=`<line x1="${fx+dirs[1]*17}" y1="${fy+dirs[0]*17}" x2="${tx}" y2="${ty}" stroke="${s.call.ok?C.orange:C.red}" stroke-width="3" ${s.call.ok?'':'stroke-dasharray="4 3"'} marker-end="url(#${s.call.ok?'arrow-hot':'arrow'})"/>`;
      if(!s.call.ok)content+=text(tx+dirs[1]*8,ty+dirs[0]*8+4,'✕',`font-size="14" font-weight="800" fill="${C.red}"`);
    }
    $('visual').innerHTML=title('열 경계는 위, 행 경계는 오른쪽에 (한쪽 개수 × 반대쪽 개수)')+svg(content,y0+H*u+10);
    $('legend').innerHTML=legend([[C.orangeLight,'이번 호출로 옮긴 입자'],[C.redLight,'실패한 호출(횟수만 사용)'],[C.orange,'값이 바뀐 경계'],[C.blue,'그대로인 경계']]);
    const sc=s.score;
    $('metrics').innerHTML=metric('엔트로피 E',s.entropy,'accent')+metric('사용 횟수',`${s.used} / ${s.limit}`)+metric('차분식 Δ',ch?signed(ch.formula):'—',ch?'good':'')+metric('점수',sc.ratioPart+sc.bonus);
    const rows=[...s.bounds.col.map(b=>[`열 경계 c${b.index}`,`${b.left} × ${b.right}`,b.value]),...s.bounds.row.map(b=>[`행 경계 r${b.index}`,`${b.left} × ${b.right}`,b.value])],cls=[...s.bounds.col.map(b=>ch&&ch.axis==='col'&&ch.boundary===b.index?'hot':''),...s.bounds.row.map(b=>ch&&ch.axis==='row'&&ch.boundary===b.index?'hot':'')];
    rows.push(['합 · 열 + 행',`${s.colSum} + ${s.rowSum}`,s.boundSum]);cls.push('pick');
    let calc='';
    if(s.call&&s.call.ok)calc=`<div class="formula">차분식: ${s.call.axis==='col'?'열':'행'} 경계 ${s.call.boundary}의 pre = ${s.call.pre}<br>${s.call.dir===1||s.call.dir===2?`2·${s.call.pre} − 1 − ${s.particles.length}`:`${s.particles.length} − 1 − 2·${s.call.pre}`} = ${signed(s.call.formula)}<br>전체 재계산: ${s.entropy} − ${s.call.eBefore} = ${signed(s.call.full)}${s.call.formula===s.call.full?' (일치)':' (불일치!)'}</div>`;
    else if(s.call)calc=`<div class="formula">${s.call.reason==='out'?'목적지가 격자 밖':'목적지에 이미 입자'}: 이동 없음<br>E 그대로 ${s.entropy}, 횟수 +1</div>`;
    $('details').innerHTML='<p class="detail-title">경계별 값 · E = 합</p>'+rowTable(['경계','왼쪽×반대쪽','값'],rows,cls)+calc+`<p class="detail-title">점수식</p><div class="formula">⌊10⁶ × (${sc.improvement}/${s.e0})²⌋ = ${sc.ratioPart}<br>+ ⌊(${s.limit} − ${s.used}) / 100⌋ = ${sc.bonus}<br>= ${sc.ratioPart+sc.bonus}</div><p class="note">입자를 한 칸 옮기면 그 방향의 경계 하나의 값만 바뀝니다. 경계 값의 합은 모든 쌍의 거리 합과 항상 같습니다.</p>`;
  }
  function renderMirror(s) {
    const ex=context,u=40,x0=30,top=20,gh=ex.rows*u,panel=gh+top+34;
    let content='';
    s.policies.forEach((v,i)=>{
      const y0=i*panel+top+8,seen=new Set(v.seen),path=new Set(v.path.map(p=>p[0]*ex.cols+p[1])),vals={};ex.cells.forEach(([y,x,val])=>{vals[y*ex.cols+x]=val;});
      content+=textAt(8,i*panel+14,`정책 ${i+1} · ${i===0?'가장 가까운 값 있는 칸':'이동당 이득 평가식'} · ${v.score}점 · 남은 이동 ${v.left}`,'start','font-size="11" font-weight="800"');
      for(let r=0;r<ex.rows;r++)for(let c=0;c<ex.cols;c++){
        const k=r*ex.cols+c,isAt=v.at[0]===r&&v.at[1]===c,isTarget=v.target&&v.target[0]===r&&v.target[1]===c,val=vals[k];
        content+=`<rect x="${x0+c*u}" y="${y0+r*u}" width="${u-2}" height="${u-2}" rx="5" fill="${isAt?C.orangeLight:seen.has(r*30+c)?'#e9eef6':'#fff'}" stroke="${isAt?C.orange:isTarget?C.teal:path.has(k)?C.teal:'#d8e0ec'}" stroke-width="${isAt||isTarget?3:path.has(k)?2:1}"/>`;
        const mark=ex.start[0]===r&&ex.start[1]===c?'S':'';
        if(val!==undefined)content+=text(x0+c*u+(u-2)/2,y0+r*u+(u-2)/2+4,seen.has(r*30+c)?`✓${val}`:val,`font-size="${String(val).length>1&&seen.has(r*30+c)?11:13}" font-weight="800" ${seen.has(r*30+c)?`fill="${C.muted}"`:''}`);
        else if(mark)content+=text(x0+c*u+(u-2)/2,y0+r*u+(u-2)/2+4,mark,'font-size="13" font-weight="800"');
        if(isAt)content+=text(x0+c*u+(u-2)/2,y0+r*u+11,'나',`font-size="10" font-weight="800" fill="${C.orange}"`);
      }
      for(let c=0;c<ex.cols;c++)if(i===0)content+=text(x0+c*u+(u-2)/2,top+5,c,'font-size="10"');
    });
    $('visual').innerHTML=title('왼쪽 위 3×7 칸 · 숫자 = 광물 가치, ✓ = 거울의 seen, 나 = 현재 위치')+svg(content,panel*2);
    $('legend').innerHTML=legend([[C.orangeLight,'현재 위치'],['#e9eef6','밟은 칸(seen)'],[C.teal,'목표와 가는 길'],['#f3f5f9','아직 안 밟음']]);
    const [p1,p2]=s.policies;
    $('metrics').innerHTML=metric('정책 1 점수',p1.score,p1.score>=p2.score?'good':'')+metric('정책 2 점수',p2.score,p2.score>p1.score?'good':'')+metric('정책 1 남은 이동',p1.left)+metric('정책 2 남은 이동',p2.left);
    const t2=p2.lastPick,t1=p1.lastPick,sel=(pick,y,x)=>pick&&pick.target[0]===y&&pick.target[1]===x;
    $('details').innerHTML='<p class="detail-title">정책 2 · 마지막 목표 선택의 키 = (g + '+s.weight+' × h) / (d + 1)</p>'+(t2?rowTable(['후보','d','g','h','키'],t2.candidates.map(c=>[`(${c.y},${c.x})`,c.d,c.g,c.h,M.fmtKey(c.key)]),t2.candidates.map(c=>sel(t2,c.y,c.x)?'pick':'')):'<p class="empty">후보 없음</p>')+'<p class="detail-title">정책 1 · 마지막 목표 선택의 후보</p>'+(t1?rowTable(['후보','d','g'],t1.candidates.map(c=>[`(${c.y},${c.x})`,c.d,c.g]),t1.candidates.map(c=>sel(t1,c.y,c.x)?'pick':'')):'<p class="empty">후보 없음</p>')+'<p class="detail-title">거울 seen · 밟은 순서</p>'+[p1,p2].map((v,i)=>`<p class="note">정책 ${i+1}: ${v.seen.map(k=>`(${Math.floor(k/30)},${k%30})`).join(' ')}</p>`).join('')+'<p class="note">g = 가는 길에서 새로 얻는 점수, h = 목표 주변 반경 3의 안 밟은 칸 가치 합입니다. 초록 행이 고른 목표입니다.</p>';
  }
  const renderers={'assignment-moves':renderAssignment,'route-insertion':renderRoute,'bucket-search':renderBucket,'boundary-delta':renderBoundary,'mirror-policy':renderMirror,'nearest-neighbor':renderNearest,'beam-search':renderBeam,'destroy-repair':renderDestroy,'paired-compare':renderPaired,'union-find':renderUnion,'segment-tree':renderSegment,'binary-search':renderBinary,bfs:renderBfs,dijkstra:renderDijkstra,'prefix-sum':renderPrefix,'two-opt':renderTwoOpt,annealing:renderAnnealing};
  function render() {
    const s=states[position];renderers[id](s);
    $('phase').textContent=phaseNames[s.phase]||s.phase;$('message').textContent=s.message;
    $('timeline').value=position;$('timeline').setAttribute('aria-valuetext',`${position+1} / ${states.length} 단계`);$('counter').textContent=`${position+1} / ${states.length}`;
    $('previous').disabled=position===0;$('reset').disabled=position===0&&!timer;$('next').disabled=position===states.length-1;
    if(position===states.length-1)stop();
    sendHeight();
  }
  function stop() {if(timer)clearInterval(timer);timer=null;$('play').textContent='▶ 재생';$('play').setAttribute('aria-pressed','false');$('play').setAttribute('aria-label','자동 재생');}
  function seek(value){stop();position=Math.max(0,Math.min(states.length-1,value));render();}
  $('reset').addEventListener('click',()=>seek(0));$('previous').addEventListener('click',()=>seek(position-1));$('next').addEventListener('click',()=>seek(position+1));$('timeline').addEventListener('input',e=>seek(Number(e.target.value)));
  $('play').addEventListener('click',()=>{
    if(timer){stop();return;}
    if(position===states.length-1){position=0;render();}
    $('play').textContent='Ⅱ 일시정지';$('play').setAttribute('aria-pressed','true');$('play').setAttribute('aria-label','재생 일시정지');$('reset').disabled=false;
    timer=setInterval(()=>{if(document.hidden){stop();return;}position++;render();},reduced.matches?1800:1200);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  window.addEventListener('pagehide',stop);
  let heightFrame=null,lastHeight=0;
  function sendHeight(){if(heightFrame!==null)return;heightFrame=requestAnimationFrame(()=>{heightFrame=null;const height=Math.ceil(document.body.getBoundingClientRect().height);if(height!==lastHeight){lastHeight=height;parent.postMessage({type:'hcontest-lesson-demo-resize',height},'*');}});}
  new ResizeObserver(sendHeight).observe(document.body);
  window.addEventListener('resize',sendHeight);
  window.lessonDemo={getState:()=>({id,position,count:states.length,playing:!!timer,state:JSON.parse(JSON.stringify(states[position]))}),seek};
  setup();
})();
