#!/usr/bin/env python3
"""Offline static roadmap. Public builds accept generic reviewed data only."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import math
import re
from datetime import date
from pathlib import Path

TOP={'schema','visibility','version','as_of','title','intro','stage','target','rules','tasks','routes','maneuvers','sources','publication_review'}
TASK={'id','title','start','end','hours','owner','state','depends','deliverable','gate','fallback','lane'}
ROUTE={'id','name','state','next','stop','amount_note','source_note'}
MANEUVER={'trigger','action','stop'}
SOURCE={'label','kind','date','scope'}

def canon(d): return (json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(b): return hashlib.sha256(b).hexdigest()
def e(x): return html.escape(str(x),quote=True)
def keys(obj,allowed):
    if not isinstance(obj,dict) or set(obj)!=allowed: raise ValueError('missing or unexpected fields')

def validate(d,private=False):
    keys(d,TOP)
    expected='private' if private else 'public'
    if d['visibility']!=expected or d['schema']!='roadmap.'+expected+'.v1': raise ValueError('visibility mismatch')
    date.fromisoformat(d['as_of'])
    if not d['publication_review']: raise ValueError('publication review missing')
    if not private:
        if d['publication_review']!='GENERIC_PUBLIC_EXAMPLE_NO_CAMPAIGN_RECORDS': raise ValueError('only reviewed generic example may be public')
        text=json.dumps(d,ensure_ascii=False)
        if re.search(r'mail\.google\.com|link_[a-f0-9]{12,}|sk-proj-|BEGIN [A-Z ]*PRIVATE KEY|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text): raise ValueError('possible private material')
    if not d['tasks']: raise ValueError('empty tasks')
    tasks={}
    for t in d['tasks']:
        keys(t,TASK)
        if not re.fullmatch(r'T\d{2}',t['id']) or t['id'] in tasks: raise ValueError('task id invalid or duplicate')
        if t['state'] not in {'PLANNED','READY','WAITING','BLOCKED','PARKED'}: raise ValueError('planning schema cannot certify completion')
        if t['lane'] not in {'cash','pending','decision','later'}: raise ValueError('invalid lane')
        if type(t['hours']) not in (int,float) or not math.isfinite(t['hours']) or not 0<=t['hours']<=40: raise ValueError('invalid effort cap')
        if date.fromisoformat(t['start'])>date.fromisoformat(t['end']): raise ValueError('reversed dates')
        if not isinstance(t['depends'],list) or not all(isinstance(v,str) for v in t['depends']): raise ValueError('invalid dependencies')
        for name in ('title','owner','deliverable','gate','fallback'):
            if not isinstance(t[name],str) or not t[name].strip(): raise ValueError('missing task text')
        tasks[t['id']]=t
    visiting=set();seen=set()
    def walk(k):
        if k in visiting: raise ValueError('dependency cycle')
        if k not in tasks: raise ValueError('unknown dependency')
        if k in seen:return
        visiting.add(k)
        for dep in tasks[k]['depends']:walk(dep)
        visiting.remove(k);seen.add(k)
    for k in tasks:walk(k)
    ids=set()
    for r in d['routes']:
        keys(r,ROUTE)
        if r['id'] in ids:raise ValueError('duplicate route')
        ids.add(r['id'])
    for m in d['maneuvers']:keys(m,MANEUVER)
    for s in d['sources']:keys(s,SOURCE);date.fromisoformat(s['date'])
    if not isinstance(d['rules'],list) or not all(isinstance(x,str) for x in d['rules']):raise ValueError('invalid rules')
    return d

CSS='''
:root{--ink:#142d39;--muted:#526974;--line:#d6e3e5;--green:#126751}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#f4f8f8;font:16px/1.55 system-ui,-apple-system,sans-serif}header{background:#142d39;color:white;padding:38px max(22px,calc((100vw - 1160px)/2))}header p{max-width:950px;color:#d5e6eb}h1{font-size:clamp(30px,4vw,48px);line-height:1.15;margin:12px 0;max-width:900px}h2{font-size:28px;line-height:1.25}h3{font-size:19px;margin:0 0 10px}.meta,small,.caption{font-size:13px;color:var(--muted)}header .meta{color:#b6d2da}.target{font-size:20px;border-left:3px solid #90d7b8;padding-left:16px}nav{position:sticky;top:0;z-index:1;display:flex;gap:22px;overflow:auto;background:white;border-bottom:1px solid var(--line);padding:12px 20px}nav a{white-space:nowrap;text-decoration:none;color:var(--green);font-weight:650}main{max-width:1200px;margin:auto;padding:24px}section{margin-bottom:36px;scroll-margin-top:75px}.notice{border-left:4px solid #bc8c2b;background:#fff4dc;padding:18px}.flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;list-style:none;padding:0;counter-reset:n}.flow li{position:relative;background:#e2f1eb;border:1px solid #bcd9ce;padding:16px;border-radius:7px;min-height:110px;counter-increment:n}.flow li:before{content:counter(n)' · ';font-weight:750;color:var(--green)}.flow li:after{content:'→';position:absolute;right:-21px;top:35px;font-size:23px}.flow li:nth-child(4n):after,.flow li:last-child:after{content:''}.flow span{display:block;font-size:14px;margin-top:8px;color:var(--muted)}.toolbar{display:flex;gap:10px;flex-wrap:wrap}button,input,select{font:inherit;padding:10px 12px;border:1px solid #aec3c9;border-radius:5px;background:white;color:var(--ink)}input{flex:1;min-width:210px}button{cursor:pointer}.task{background:white;border:1px solid var(--line);border-radius:8px;margin:12px 0}.task summary{cursor:pointer;padding:18px}.task summary strong{color:var(--green)}.task .body{padding:0 20px 18px;border-top:1px solid var(--line)}dl{display:grid;grid-template-columns:150px 1fr;gap:12px}dt{font-weight:700}dd{margin:0}.branches{display:grid;grid-template-columns:1fr 1fr;gap:16px}.branch{background:white;padding:20px;border-left:4px solid var(--green)}.stop{color:#875d0b;font-size:14px}.scroll{overflow:auto;background:white;border:1px solid var(--line);border-radius:8px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:#eaf1f2}.routes{min-width:880px}.timeline{min-width:920px;padding:20px}.time-row,.axis{display:grid;grid-template-columns:290px 1fr;gap:12px;align-items:center;min-height:42px;font-size:13px}.axis{font-weight:700}.days{display:flex;justify-content:space-between}.track{position:relative;height:14px;background:#eef3f4}.bar{height:14px;position:absolute;border-radius:3px;background:#388c75}.bar.pending{background:#b5934f}.bar.decision{background:#5871a0}pre{padding:20px;background:#173540;color:#e4eff2;overflow:auto;border-radius:7px;font:13px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace}.source{background:white;padding:14px 18px;margin:10px 0}.hidden{display:none!important}.rules li{margin:12px 0}footer{font-size:12px;color:var(--muted);padding:24px;border-top:1px solid var(--line);overflow-wrap:anywhere}:focus-visible{outline:3px solid #d69a2e;outline-offset:3px}
@media(max-width:760px){main{padding:18px}.branches{grid-template-columns:1fr}.flow{grid-template-columns:repeat(2,minmax(0,1fr))}.flow li:nth-child(2n):after{content:''}dl{grid-template-columns:1fr;gap:5px}dd{margin-bottom:10px}h2{font-size:25px}}
@media(max-width:430px){.flow{grid-template-columns:1fr;gap:22px}.flow li:after{content:'↓'!important;top:auto;bottom:-25px;right:50%}.flow li:last-child:after{content:''!important}.toolbar input,.toolbar select{width:100%}header{padding:28px 20px}}
@media print{nav,.toolbar{display:none}body{background:white;font-size:11px}header{background:white;color:#142d39;padding:0}header p,header .meta{color:#142d39}main{padding:0}.task,.branch{break-inside:avoid}.flow{grid-template-columns:repeat(4,1fr)}details:not([open])>*:not(summary){display:block!important}.scroll{overflow:visible}.timeline{min-width:0}}
'''
JS='''
const q=document.querySelector('#query'),lane=document.querySelector('#lane');
function filter(){let n=0;document.querySelectorAll('.task').forEach(t=>{const ok=t.textContent.toLowerCase().includes(q.value.toLowerCase())&&(!lane.value||lane.value===t.dataset.lane);t.classList.toggle('hidden',!ok);if(ok)n++});document.querySelector('#count').textContent=n}
q.addEventListener('input',filter);lane.addEventListener('change',filter);document.querySelector('#expand').onclick=()=>document.querySelectorAll('.task:not(.hidden)').forEach(t=>t.open=true);document.querySelector('#collapse').onclick=()=>document.querySelectorAll('.task').forEach(t=>t.open=false);document.querySelector('#print').onclick=()=>{document.querySelectorAll('.task').forEach(t=>t.open=true);window.print()};filter();
'''

def flow(nodes):return '<ol class="flow">'+''.join('<li><b>'+e(a)+'</b><span>'+e(b)+'</span></li>' for a,b in nodes)+'</ol>'

def build(d,out,private=False,revision='unrecorded'):
    validate(d,private)
    if not re.fullmatch(r'[A-Za-z0-9._/-]{1,100}',revision):raise ValueError('invalid revision')
    source=canon(d);parts=[]
    parts.append('<header><div class="meta">'+e(d['version'])+' · '+e(d['as_of'])+' · '+e(d['visibility'].upper())+'</div><h1>'+e(d['title'])+'</h1><p>'+e(d['intro'])+'</p><p class="target">'+e(d['target'])+'</p></header>')
    parts.append('<nav aria-label="Разделы"><a href="#start">Старт</a><a href="#cash">До денег</a><a href="#plan">Дорожная карта</a><a href="#forks">Манёвры</a><a href="#routes">Очереди</a><a href="#git">Обновление</a></nav><main>')
    parts.append('<section id="start"><h2>Состояние и первый шаг</h2><p class="notice">'+e(d['stage'])+'</p><p>Сначала один ясный результат, один воспроизводимый образец и несколько подходящих покупателей. Не новая платформа и не обещание найти уязвимость. Даты ниже — плановые окна, не обязательства контрагента.</p></section>')
    parts.append('<section id="cash"><h2>Диаграмма 1 · Восемь переходов до денег</h2>'+flow([('Потребность','Человек, проблема и решение'),('Образец','Один воспроизводимый вывод'),('Предложение','Результат, цена и исключения'),('Scope','Встречное письменное согласие'),('Расчёт','Invoice, этапы и допустимая оплата'),('Исполнение','Только согласованная работа'),('Приёмка','Явное принятие по критериям'),('Зачисление','Получено, заработано, доступно')])+'<p class="caption">Каждый переход имеет отдельное доказательство. Аванс может быть возвратным; целевой грант и credits не автоматически личный доход.</p></section>')
    parts.append('<section id="plan"><h2>Диаграмма 2 · Плановые окна</h2><div class="scroll" tabindex="0" aria-label="Временная шкала"><div class="timeline">')
    start=min(date.fromisoformat(t['start']) for t in d['tasks']);end=max(date.fromisoformat(t['end']) for t in d['tasks']);span=(end-start).days+1
    parts.append('<div class="axis"><span>Задача</span><div class="days"><span>'+start.isoformat()+'</span><span>'+end.isoformat()+'</span></div></div>')
    for t in d['tasks']:
        left=(date.fromisoformat(t['start'])-start).days/span*100;width=((date.fromisoformat(t['end'])-date.fromisoformat(t['start'])).days+1)/span*100
        parts.append('<div class="time-row"><span>'+e(t['id'])+' · '+e(t['title'])+'</span><div class="track" aria-label="'+e(t['start']+' — '+t['end'])+'"><div class="bar '+e(t['lane'])+'" style="left:'+f'{left:.5f}'+'%;width:'+f'{width:.5f}'+'%"></div></div></div>')
    parts.append('</div></div><p class="caption">Полосы — оценки. Реальный delivery начинается после выполнения условий, не автоматически по дате.</p><div class="toolbar"><input id="query" aria-label="Поиск задачи" placeholder="Найти задачу или препятствие"><select id="lane" aria-label="Направление"><option value="">Все</option value="cash">Первый платёж</option><option value="pending">Ожидающие</option><option value="decision">Развилки</option><option value="later">Позже</option></select><button id="expand">Раскрыть</button><button id="collapse">Свернуть</button><button id="print">Печать</button></div><p class="caption">Задач: <span id="count"></span> · <a href="snapshot.json" download>Данные снимка</a></p>')
    for i,t in enumerate(d['tasks']):
        parts.append('<details class="task" id="'+e(t['id'])+'" data-lane="'+e(t['lane'])+'" '+('open' if i<2 else '')+'><summary><strong>'+e(t['id'])+'</strong> · '+e(t['title'])+'<div class="caption">'+e(t['start']+' — '+t['end'])+' · до '+e(t['hours'])+' ч · '+e(t['owner'])+' · '+e(t['state'])+'</div></summary><div class="body"><dl>')
        for label,value in [('Зависимости',', '.join(t['depends']) or 'Нет'),('Выход',t['deliverable']),('Условие перехода',t['gate']),('Запасной ход',t['fallback'])]:parts.append('<dt>'+label+'</dt><dd>'+e(value)+'</dd>')
        parts.append('</dl></div></details>')
    parts.append('</section><section id="forks"><h2>Диаграмма 3 · Препятствие → манёвр → STOP</h2><div class="branches">')
    for m in d['maneuvers']:parts.append('<article class="branch"><h3>'+e(m['trigger'])+'</h3><p>→ '+e(m['action'])+'</p><p class="stop">STOP: '+e(m['stop'])+'</p></article>')
    parts.append('</div></section><section id="routes"><h2>Очереди и границы</h2><div class="scroll"><table class="routes"><thead><tr><th>Маршрут</th><th>Состояние / деньги</th><th>Следующий шаг</th><th>Ограничение</th></tr></thead><tbody>')
    for r in d['routes']:parts.append('<tr><td><b>'+e(r['name'])+'</b><p class="caption">'+e(r['source_note'])+'</p></td><td>'+e(r['state'])+'<p>'+e(r['amount_note'])+'</p></td><td>'+e(r['next'])+'</td><td>'+e(r['stop'])+'</td></tr>')
    parts.append('</tbody></table></div></section><section><h2>Правила</h2><ol class="rules">'+''.join('<li>'+e(x)+'</li>' for x in d['rules'])+'</ol></section><section id="git"><h2>Диаграмма 4 · Git → ручная сборка → сайт</h2>')
    parts.append(flow([('Источник','Прочитать факт и определить режим доступа'),('JSON','Изменить данные и дату проверки'),('Тесты и diff','Проверить поля, зависимости и приватность'),('Сборка','HTML + snapshot + manifest; публикация отдельно')]))
    cmd='python3 sites/money-roadmap/build.py --input sites/money-roadmap/example.json --out reports/money-roadmap --revision "$(git rev-parse HEAD)"'
    if private:cmd='python3 sites/money-roadmap/build.py --private --input /private/roadmap.private.json --out /private/site --revision "$(git rev-parse HEAD)"'
    parts.append('<pre>'+e(cmd)+'</pre><p>Страница не читает почту, не меняет Git и не отправляет заявки. Дата сборки не заменяет дату источника. Приватные снимки запрещены в публичной сборке.</p></section><section><h2>Основания</h2>')
    for s in d['sources']:parts.append('<div class="source"><b>'+e(s['label'])+'</b><small> · '+e(s['kind'])+' · '+e(s['date'])+'</small><p>'+e(s['scope'])+'</p></div>')
    parts.append('</section></main><footer>Revision: '+e(revision)+'<br>Input SHA-256: '+digest(source)+'<br>Идентичность байтов не доказывает правильность прогноза или факт оплаты.</footer>')
    output='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><title>'+e(d['title'])+'</title><style>'+CSS+'</style></head><body>'+''.join(parts)+'<script>'+JS+'</script></body></html>'
    out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(output,encoding='utf-8');(out/'snapshot.json').write_bytes(source)
    receipt={'schema':'roadmap.build.v1','visibility':d['visibility'],'source_as_of':d['as_of'],'revision':revision,'input_sha256':digest(source),'html_sha256':digest(output.encode()),'task_count':len(d['tasks']),'network_calls':0,'automatic_actions':False,'hosting_verified':False}
    (out/'manifest.json').write_bytes(canon(receipt));return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--private',action='store_true');p.add_argument('--revision',default='unrecorded');a=p.parse_args()
    if a.input.resolve().is_relative_to(a.out.resolve()):p.error('input must be outside output directory')
    print(json.dumps(build(json.loads(a.input.read_text(encoding='utf-8')),a.out,a.private,a.revision),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
