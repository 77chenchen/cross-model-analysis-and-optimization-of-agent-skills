const NS = 'http://www.w3.org/2000/svg';
const palette = {
  'qwen3.5:9b': '#d66a31', gemma4: '#197d74', 'gemma4:26b': '#197d74',
  'qwen3.8:27b': '#4477ba', 'qwen3-coder-next': '#8161b3',
  'llama3.1:8b': '#ad628e', 'gpt-5.6-sol': '#31343a', C0: '#a1a6ae', C1: '#197d74'
};
const labels = {steps: 'Steps / run', assistant_turns: 'Assistant turns / run',
  validated_after_last_edit_intent: 'Validation after edit',
  validated_after_last_edit_success: 'Successful validation after edit',
  write_file_rewrite_count: 'Write-file rewrites', loop_count: 'Loop count'};
const state = {split: 'all', models: 'controlled'};

const by = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function svg(el, tag, attrs = {}, text = null) { const node = document.createElementNS(NS, tag); Object.entries(attrs).forEach(([k,v]) => node.setAttribute(k, v)); if (text !== null) node.textContent = text; el.append(node); return node; }
function makeSvg(container, height, width = 960) { container.replaceChildren(); const el = svg(container, 'svg', {viewBox: `0 0 ${width} ${height}`, width: '100%', height: '100%', role: 'img'}); return {el, width, height}; }
function tip(event, html) { const t = by('tooltip'); t.innerHTML = html; t.hidden = false; t.style.left = `${event.clientX + 15}px`; t.style.top = `${event.clientY + 15}px`; }
function hideTip(){ by('tooltip').hidden = true; }
function modelName(model){ return model.replace('qwen3.5:9b','Qwen 3.5 9B').replace('qwen3.8:27b','Qwen 3.8 27B').replace('gpt-5.6-sol','GPT-5.6 Sol').replace('qwen3-coder-next','Qwen3 Coder Next').replace('gemma4:26b','Gemma 4 26B').replace('llama3.1:8b','Llama 3.1 8B'); }

function drawPerformance(data) {
  const rows = data.summary.filter(r => r.split === state.split && (state.models === 'all' || r.model !== 'gpt-5.6-sol') && ['C0','C1'].includes(r.condition));
  const models = [...new Set(rows.map(r => r.model))].sort((a,b) => {
    const av = rows.find(r=>r.model===a&&r.condition==='C0')?.verifier_pass_rate || 0;
    const bv = rows.find(r=>r.model===b&&r.condition==='C0')?.verifier_pass_rate || 0;
    return bv-av;
  });
  const {el,width,height} = makeSvg(by('performance-chart'), 430); const m={l:160,r:42,t:22,b:50}, iw=width-m.l-m.r, ih=height-m.t-m.b;
  for(let tick=0;tick<=1;tick+=.2){ const x=m.l+tick*iw; svg(el,'line',{x1:x,y1:m.t,x2:x,y2:m.t+ih,class:'gridline'}); svg(el,'text',{x,y:height-18,class:'axis','text-anchor':'middle'},`${Math.round(tick*100)}%`); }
  svg(el,'text',{x:m.l+iw/2,y:height-2,class:'axis','text-anchor':'middle'},'Verifier pass rate (95% Wilson interval)');
  models.forEach((model,idx) => { const y=m.t+(idx+.5)*ih/models.length; const rs=rows.filter(r=>r.model===model); const c0=rs.find(r=>r.condition==='C0'), c1=rs.find(r=>r.condition==='C1');
    svg(el,'line',{x1:m.l,y1:y,x2:m.l+iw,y2:y,stroke:'#f0f1f2'}); svg(el,'text',{x:m.l-14,y:y+4,class:'model','text-anchor':'end'},modelName(model));
    if(c0&&c1) svg(el,'line',{x1:m.l+c0.verifier_pass_rate*iw,y1:y,x2:m.l+c1.verifier_pass_rate*iw,y2:y,stroke:model==='gpt-5.6-sol'?palette[model]:'#c4c8ce','stroke-dasharray':model==='gpt-5.6-sol'?'4 3':'none'});
    [c0,c1].filter(Boolean).forEach(r=>{const x=m.l+r.verifier_pass_rate*iw, lo=m.l+r.wilson_low*iw, hi=m.l+r.wilson_high*iw, fill=r.condition==='C0'?palette.C0:palette.C1, g=svg(el,'g',{style:'cursor:pointer'}); svg(g,'line',{x1:lo,y1:y,x2:hi,y2:y,stroke:fill,'stroke-width':2}); svg(g,'line',{x1:lo,y1:y-4,x2:lo,y2:y+4,stroke:fill}); svg(g,'line',{x1:hi,y1:y-4,x2:hi,y2:y+4,stroke:fill}); svg(g,'circle',{cx:x,cy:y,r:6,fill:model==='gpt-5.6-sol'?'#fff':fill,stroke:fill,'stroke-width':2}); g.addEventListener('mouseenter',e=>tip(e,`<strong>${esc(modelName(r.model))} · ${r.condition}</strong><br>Pass: ${(r.verifier_pass_rate*100).toFixed(1)}% (${r.verifier_pass}/${r.primary_n})<br>95% CI: ${(r.wilson_low*100).toFixed(1)}–${(r.wilson_high*100).toFixed(1)}%<br>Provider errors excluded: ${r.provider_error_protocol}`));g.addEventListener('mousemove',e=>tip(e,by('tooltip').innerHTML));g.addEventListener('mouseleave',hideTip); });
    const n=c0?.primary_n ?? c1?.primary_n; svg(el,'text',{x:width-3,y:y+4,class:'annot','text-anchor':'end'},`n=${n ?? '–'}`);
  });
}

function drawProcess(data) {
  const rows=data.metrics.filter(r=>['steps','assistant_turns'].includes(r.metric)&&['C0','C1'].includes(r.condition)&&r.model!=='gpt-5.6-sol'); const models=[...new Set(rows.map(r=>r.model))]; const {el,width,height}=makeSvg(by('process-chart'),300); const m={l:150,r:22,t:25,b:35},iw=width-m.l-m.r,ih=height-m.t-m.b; const max=Math.max(...rows.map(r=>r.q3));
  for(let x=0;x<=max;x+=5){const px=m.l+x/max*iw;svg(el,'line',{x1:px,y1:m.t,x2:px,y2:m.t+ih,class:'gridline'});svg(el,'text',{x:px,y:height-14,class:'axis','text-anchor':'middle'},x)}
  models.forEach((model,i)=>{const y=m.t+(i+.5)*ih/models.length;svg(el,'text',{x:m.l-12,y:y+4,class:'model','text-anchor':'end'},modelName(model));['steps','assistant_turns'].forEach((metric,j)=>{const r=rows.find(x=>x.model===model&&x.condition==='C1'&&x.metric===metric);if(!r)return;const offset=j?7:-7,x=v=>m.l+v/max*iw;svg(el,'line',{x1:x(r.q1),y1:y+offset,x2:x(r.q3),y2:y+offset,stroke:j?palette[model]:palette.C1,'stroke-width':3});svg(el,'circle',{cx:x(r.median),cy:y+offset,r:4,fill:j?palette[model]:palette.C1});});});
  svg(el,'text',{x:m.l,y:15,class:'annot'},'● steps (C1)   ● assistant turns (C1; model color)');
}

function drawFlags(data) {
  const flags=['final_empty','no_edit','timeout','max_steps_reached']; const rows=data.summary.filter(r=>r.split===state.split&&['C0','C1'].includes(r.condition)&&r.model!=='gpt-5.6-sol'); const {el,width,height}=makeSvg(by('flags-chart'),300);const m={l:125,r:16,t:50,b:12},iw=width-m.l-m.r,ih=height-m.t-m.b;const labelsRows=rows.map(r=>`${modelName(r.model)} · ${r.condition}`);
  flags.forEach((f,i)=>svg(el,'text',{x:m.l+(i+.5)*iw/flags.length,y:27,class:'axis','text-anchor':'middle'},f.replace('_','\n')));
  rows.forEach((r,ri)=>{const y=m.t+ri*ih/rows.length;svg(el,'text',{x:m.l-8,y:y+12,class:'axis','text-anchor':'end'},labelsRows[ri]);flags.forEach((f,i)=>{const v=r[f]/r.primary_n, x=m.l+i*iw/flags.length, color=`rgba(25,125,116,${.12+.76*v})`,g=svg(el,'g',{style:'cursor:pointer'});svg(g,'rect',{x:x+2,y:y+2,width:iw/flags.length-4,height:ih/rows.length-4,rx:3,fill:color});svg(g,'text',{x:x+iw/flags.length/2,y:y+15,class:'cell-text','text-anchor':'middle',fill:v<.4?'#344':'#fff'},`${Math.round(v*100)}%`);g.addEventListener('mouseenter',e=>tip(e,`<strong>${labelsRows[ri]}</strong><br>${f}: ${r[f]} / ${r.primary_n}`));g.addEventListener('mousemove',e=>tip(e,by('tooltip').innerHTML));g.addEventListener('mouseleave',hideTip);});});
}

function drawPaired(data){const rows=data.paired.filter(r=>r.model==='qwen3.5:9b'&&r.scope==='all'&&r.contrast==='C1-C0');by('paired-table').innerHTML=`<table><thead><tr><th>Process metric</th><th>Task unit</th><th class="num">C1 − C0</th><th class="num">95% paired bootstrap interval</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${labels[r.metric]||r.metric}</td><td>${r.n_tasks} matched tasks</td><td class="num ${r.mean_difference>=0?'positive':'negative'}">${r.mean_difference>=0?'+':''}${(r.mean_difference*100).toFixed(1)} pp</td><td class="num">${(r.bootstrap_low*100).toFixed(1)} to ${(r.bootstrap_high*100).toFixed(1)} pp</td></tr>`).join('')}</tbody></table>`;}

fetch('./data.json').then(r=>r.json()).then(data=>{const redraw=()=>{drawPerformance(data);drawProcess(data);drawFlags(data);drawPaired(data)};by('split').addEventListener('change',e=>{state.split=e.target.value;redraw()});by('models').addEventListener('change',e=>{state.models=e.target.value;redraw()});redraw();}).catch(err=>{by('performance-chart').textContent=`Unable to load public aggregate data: ${err.message}`;});
