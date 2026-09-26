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
    annealing:{title:'나빠진 현재 해, 보존되는 최고 해',subtitle:'온도와 악화 제안 크기를 바꾸며 수락 확률과 current / best의 차이를 실험합니다.',footnote:'최소화 예제입니다. T는 매 시도마다 0.88배로 냉각됩니다. 비교를 위해 제안 패턴과 난수 u는 고정했으며, 실제 탐색에서는 이웃 해와 난수를 생성합니다.'}
  };
  let id = new URLSearchParams(location.search).get('demo') || 'binary-search';
  if (!config[id]) id = 'binary-search';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let position=0, states=[], timer=null, context={}, options={target:4,example:0,source:0,rectangle:0,temperature:8,delta:6};
  const phaseNames={start:'준비',compare:'비교',move:'구간 축소',done:'완료',pop:'꺼내기',enqueue:'발견',stale:'오래된 항목',relax:'거리 갱신',skip:'유지',term:'포함배제',remove:'기존 경계',add:'새 경계',candidate:'후보 확인',trial:'수락 판단'};
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
    xy.forEach(([x,y],i)=>{const selected=context.order.indexOf(i)>=context.left&&context.order.indexOf(i)<=context.right;content+=`<circle cx="${x}" cy="${y}" r="14" fill="${i===0?C.ink:selected?C.blueLight:'#fff'}" stroke="${selected?C.blue:'#9aabc4'}" stroke-width="1.5"/>`+text(x,y+4,i,`font-size="15" font-weight="750" style="fill:${i===0?'#fff':C.ink}"`)+text(x,y+29,`(${pts[i][0]},${pts[i][1]})`,'font-size="10"');});
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
  const renderers={'binary-search':renderBinary,bfs:renderBfs,dijkstra:renderDijkstra,'prefix-sum':renderPrefix,'two-opt':renderTwoOpt,annealing:renderAnnealing};
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
