#!/usr/bin/env python3
"""Build the local website integration files and an offline, self-contained guide."""
import base64
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
SOURCE = OUT / 'editorial'
DIST = OUT / 'site' / 'dist'
ASSETS = OUT / 'assets'


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def data_uri(path):
    mime = 'image/png' if path.suffix == '.png' else 'image/webp'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


TEMPLATE = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta name="description" content="촬영 전에 가볍게 살펴보는 여자편·남자편·커플편 한글 포즈 가이드. 원저자와 사진 Jerry Ghionis.">
<title>포즈 가이드 — yoogeeone</title>
<style>
:root { --ink:#111; --muted:#5e5e5e; --line:#dedede; --soft:#f4f4f4; --good:#385d2e; --adjust:#a62222; --caution:#806000; color-scheme:light; }
* { box-sizing:border-box; }
html { font-size:16px; scroll-behavior:smooth; }
body { margin:0; color:var(--ink); background:#fff; font-family:Pretendard,"Inter Tight",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans CJK KR","Noto Sans KR",Arial,sans-serif; line-height:1.65; word-break:keep-all; overflow-wrap:anywhere; }
body.dialog-open { overflow:hidden; }
button,input,summary { font:inherit; }
button,a,input,summary { -webkit-tap-highlight-color:transparent; }
button { border:0; padding:0; background:none; color:inherit; cursor:pointer; }
a { color:inherit; }
button:focus-visible,a:focus-visible,input:focus-visible,summary:focus-visible { outline:2px solid #111; outline-offset:5px; }
[hidden] { display:none !important; }
.skip { position:fixed; top:10px; left:14px; z-index:10; padding:10px 16px; background:#111; color:#fff; transform:translateY(-180%); }
.skip:focus { transform:none; }
.shell { width:min(100%,1680px); margin:auto; padding:30px 42px 0; }
.header { display:flex; align-items:flex-start; justify-content:space-between; gap:40px; }
.home { display:inline-block; width:min(410px,42vw); line-height:0; flex:none; }
.wordmark { width:100%; height:auto; display:block; }
.header-note { padding-top:8px; text-align:right; font-size:.875rem; line-height:1.7; color:var(--muted); }
.header-note p { margin:0; }
.about-open { margin-top:7px; color:#111; text-decoration:underline; text-underline-offset:4px; }
.intro { margin:58px 0 0; max-width:720px; }
.eyebrow { font-size:.875rem; line-height:1.5; margin:0 0 12px; }
h1 { margin:0 0 12px; font-size:clamp(1.625rem,2.5vw,2.125rem); line-height:1.35; letter-spacing:-.055em; font-weight:800; }
.intro p { margin:0; font-size:1rem; color:#444; line-height:1.8; }
.chapter-nav { display:flex; flex-wrap:wrap; gap:14px 36px; margin:47px 0 30px; }
.chapter-nav button { position:relative; font-weight:850; letter-spacing:-.065em; font-size:clamp(2.25rem,4.1vw,3.25rem); line-height:1.3; padding-bottom:6px; color:#666; }
.chapter-nav button[aria-pressed="true"] { color:#111; }
.chapter-nav button[aria-pressed="true"]::after { content:""; height:4px; position:absolute; left:0; bottom:0; width:100%; background:#111; }
.chapter-nav button:hover { color:#111; }
.toolbar { display:flex; justify-content:space-between; align-items:center; gap:20px; margin:0 0 28px; padding:20px 0; border-top:1px solid #111; border-bottom:1px solid var(--line); }
.chapter-context { min-width:0; }
.chapter-context h2 { margin:0; font-size:1rem; font-weight:650; line-height:1.5; }
.chapter-context p { margin:3px 0 0; font-size:.875rem; color:var(--muted); }
.search { display:flex; align-items:center; gap:12px; width:min(350px,45%); border-bottom:1px solid #777; padding:4px 0; }
.search-label { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; }
.search input { border:0; border-radius:0; min-width:0; width:100%; padding:6px 0; background:transparent; color:#111; font-size:1rem; outline-offset:3px; }
.clear-search { flex:none; text-decoration:underline; text-underline-offset:3px; font-size:.875rem; padding:7px 0 7px 8px; }
.grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); column-gap:42px; row-gap:52px; }
.pose-card { min-width:0; }
.card-open { display:block; width:100%; text-align:left; }
.thumb { width:100%; aspect-ratio:2/3; background:#f4f4f4; overflow:hidden; }
.thumb img { display:block; width:100%; height:100%; object-fit:contain; }
.thumb.duo { display:grid; grid-template-columns:1fr 1fr; gap:6px; background:#fff; }
.card-open:hover .thumb { outline:1px solid #111; outline-offset:5px; }
.card-meta { display:flex; justify-content:space-between; flex-wrap:wrap; gap:4px 10px; margin:15px 0 5px; color:var(--muted); font-size:.875rem; }
.card-title { display:block; font-size:1.2rem; font-weight:750; line-height:1.5; letter-spacing:-.035em; }
.card-tip { margin:8px 0 0; font-size:1rem; line-height:1.7; color:#444; }
.card-open:hover .card-title { text-decoration:underline; text-underline-offset:5px; }
.empty { padding:70px 20px 95px; text-align:center; }
.empty h3 { font-size:1.375rem; margin:0 0 10px; }
.empty p { margin:0 0 20px; color:var(--muted); }
.text-button { text-decoration:underline; text-underline-offset:5px; padding:6px 0; }
footer { display:flex; justify-content:space-between; gap:30px; margin-top:100px; padding:28px 0 32px; border-top:1px solid #111; font-size:.875rem; }
footer p { margin:0; }
footer .muted { color:var(--muted); margin-top:3px; }
footer a { text-underline-offset:4px; }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
dialog { color:var(--ink); width:min(1120px,calc(100vw - 40px)); max-height:calc(100dvh - 40px); margin:auto; padding:0; border:1px solid #111; border-radius:0; background:#fff; overflow:auto; }
dialog::backdrop { background:rgba(0,0,0,.65); }
.dialog-head { position:sticky; top:0; z-index:2; display:flex; justify-content:space-between; align-items:flex-start; gap:24px; padding:24px 32px 21px; border-bottom:1px solid var(--line); background:#fff; }
.dialog-kicker { margin:0 0 4px; font-size:.875rem; color:var(--muted); }
.dialog-head h2 { margin:0; font-size:clamp(1.375rem,2.6vw,1.875rem); letter-spacing:-.045em; line-height:1.4; }
.close-button { flex:none; font-size:1rem; padding:4px 0 5px 12px; text-decoration:underline; text-underline-offset:5px; }
.dialog-body { padding:28px 32px 32px; }
.client-tip { border-left:3px solid #111; padding:0 0 0 18px; margin:0 0 28px; }
.client-tip h3 { margin:0 0 5px; font-size:.875rem; font-weight:750; }
.client-tip p { margin:0; font-size:1.125rem; line-height:1.75; }
.photo-gallery { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:26px; margin-bottom:30px; }
.photo-gallery.single { display:block; }
.photo-gallery figure { margin:0; min-width:0; }
.photo-gallery .photo-frame { background:#f4f4f4; width:100%; aspect-ratio:2/3; }
.photo-gallery img { width:100%; height:100%; object-fit:contain; display:block; }
.photo-gallery.single .photo-frame { max-height:none; aspect-ratio:auto; background:#fff; }
.photo-gallery.single img { width:auto; height:auto; max-height:76vh; max-width:100%; margin:auto; object-fit:contain; }
.photo-gallery figcaption { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:5px 12px; font-size:.875rem; padding-top:9px; }
.status { font-size:.875rem; display:inline-flex; align-items:center; gap:7px; line-height:1.5; }
.status::before { content:""; width:9px; height:9px; flex:none; background:currentColor; }
.status-good { color:var(--good); }
.status-adjust { color:var(--adjust); }
.status-caution { color:var(--caution); }
.explanation { border-top:1px solid #111; border-bottom:1px solid var(--line); padding:18px 0; }
.explanation summary { font-size:1.125rem; font-weight:750; cursor:pointer; padding:1px 0; }
.explanation[open] summary { margin-bottom:20px; }
.explanation p,.book-section p { font-size:1rem; margin:0 0 15px; white-space:pre-line; line-height:1.85; }
.explanation p:last-child,.book-section p:last-child { margin-bottom:0; }
.source-heading { font-size:1.1rem !important; font-weight:750; }
.source-credit { color:#555; }
.photo-only-note { margin:0 0 4px; font-size:1rem; color:var(--muted); }
.dialog-footer { display:flex; justify-content:space-between; align-items:center; gap:20px; padding-top:26px; }
.topic-nav { display:flex; gap:24px; }
.topic-nav button { text-decoration:underline; text-underline-offset:5px; font-size:1rem; padding:6px 0; }
.topic-nav button:disabled { color:#999; text-decoration:none; cursor:default; }
.photo-credit { margin:0; font-size:.875rem; color:var(--muted); }
.book-section { border-top:1px solid #111; margin-top:42px; padding-top:24px; }
.book-section:first-child { border:0; margin-top:0; padding-top:0; }
.book-section h3 { margin:0 0 6px; font-size:1.375rem; letter-spacing:-.035em; }
.book-section .source-page { margin:0 0 20px; color:var(--muted); font-size:.875rem; }
.book-section .photo-gallery { margin:0 0 25px; }
.book-section .photo-gallery.single img { max-height:56vh; }
.about-preface { margin:0 0 28px; padding-bottom:22px; border-bottom:1px solid var(--line); }
.about-preface p { margin:0 0 10px; line-height:1.8; }
.about-preface p:last-child { margin-bottom:0; }
noscript p { padding:25px; margin:25px 0; border:1px solid #111; }
@media (min-width:1500px) { .grid { column-gap:52px; row-gap:64px; } }
@media (max-width:1000px) { .shell { padding:25px 28px 0; } .grid { column-gap:28px; row-gap:40px; } .card-title { font-size:1.125rem; } .header { gap:25px; } .header-note { font-size:.875rem; } .dialog-head { padding:22px 25px 19px; } .dialog-body { padding:25px; } }
@media (max-width:700px) { .shell { padding:22px 20px 0; } .header { display:block; } .home { width:min(310px,80vw); } .header-note { text-align:left; padding-top:24px; display:flex; flex-wrap:wrap; gap:4px 20px; } .header-note p { width:100%; } .about-open { margin-top:0; } .intro { margin-top:35px; } .intro p { line-height:1.8; } .chapter-nav { gap:25px; margin:33px 0 24px; } .chapter-nav button { font-size:2.25rem; } .chapter-nav button[aria-pressed="true"]::after { height:3px; } .toolbar { align-items:flex-start; flex-direction:column; gap:16px; margin-bottom:25px; padding:17px 0; } .search { width:100%; } .grid { grid-template-columns:minmax(0,1fr); gap:42px; } .card-title { font-size:1.25rem; } .card-tip { font-size:1rem; } .thumb { max-height:none; } footer { margin-top:70px; display:block; padding:25px 0; } footer > div+div { margin-top:18px; } dialog { width:calc(100vw - 20px); max-height:calc(100dvh - 20px); } .dialog-head { padding:18px 18px 16px; gap:15px; } .dialog-body { padding:22px 18px; } .photo-gallery { grid-template-columns:minmax(0,1fr); gap:25px; } .photo-gallery .photo-frame { aspect-ratio:auto; background:#fff; } .photo-gallery img { width:auto; height:auto; max-width:100%; max-height:76vh; margin:auto; } .client-tip p { font-size:1rem; } .dialog-footer { flex-direction:column; align-items:flex-start; gap:16px; } .topic-nav { width:100%; justify-content:space-between; } .photo-gallery.single img { max-height:72vh; } .book-section { margin-top:32px; } }
@media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
</style>
</head>
<body>
<a class="skip" href="#guide">포즈 가이드로 이동</a>
<div class="shell">
<header class="header">
<a class="home" href="https://yoogeeone.kr/" aria-label="yoogeeone 홈페이지"><img class="wordmark" src="__WORDMARK__" width="782" height="167" alt="yoogeeone"></a>
<div class="header-note"><p>검토용 시안 · 배포 허락 확인 전</p><button class="about-open" type="button" id="aboutOpen">책 소개와 이용 안내</button></div>
</header>
<section class="intro" aria-labelledby="pageTitle">
<p class="eyebrow">원저자·사진 Jerry Ghionis</p>
<h1 id="pageTitle">촬영 전에 살펴보는 포즈 가이드</h1>
<p>사진 속 자세를 외우실 필요는 없습니다. 마음에 드는 분위기를 골라 오시면, 촬영하면서 하나씩 함께 맞춰 드릴게요. 어느 편이든 원하는 분위기와 몸에 편한 동작을 기준으로 살펴봐 주세요.</p>
</section>
<nav class="chapter-nav" aria-label="포즈 가이드 편 선택">
<button type="button" data-chapter="women" aria-pressed="true">여자편</button>
<button type="button" data-chapter="men" aria-pressed="false">남자편</button>
<button type="button" data-chapter="couples" aria-pressed="false">커플편</button>
</nav>
<main id="guide">
<div class="toolbar">
<div class="chapter-context"><h2 id="chapterSummary">여자편</h2><p id="resultCount" aria-live="polite"></p></div>
<div class="search"><label class="search-label" for="searchInput">현재 편에서 포즈 찾기</label><input id="searchInput" type="search" placeholder="여자편에서 포즈 찾기" autocomplete="off"><button class="clear-search" id="clearSearch" type="button" hidden>지우기</button></div>
</div>
<div class="grid" id="poseGrid" aria-label="포즈 목록"></div>
<div class="empty" id="emptyState" hidden><h3>찾으시는 포즈가 없어요.</h3><p>‘손’, ‘앉기’, ‘체중’처럼 짧은 단어로 찾아보세요.</p><button type="button" class="text-button" id="showAll">검색 지우고 전체 보기</button></div>
<noscript><p>이 가이드의 사진과 번역문을 보려면 브라우저에서 JavaScript를 켜 주세요. 별도의 앱이나 인터넷 연결은 필요하지 않습니다.</p></noscript>
</main>
<footer><div><p>원저자·사진 Jerry Ghionis</p><p class="muted">Copyright © 2023 Jerry Ghionis. 원문 114쪽의 한글 번역·편집 시안.</p></div><div><p><a href="https://yoogeeone.kr/">yoogeeone.kr</a></p><p class="muted">촬영 가이드 · 내부 검토용</p></div></footer>
</div>
<dialog id="poseDialog" aria-labelledby="dialogTitle">
<div class="dialog-head"><div><p class="dialog-kicker" id="dialogKicker"></p><h2 id="dialogTitle" tabindex="-1"></h2></div><button type="button" class="close-button" id="closePose" aria-label="포즈 설명 닫기">닫기</button></div>
<div class="dialog-body"><div id="poseContent"></div><div class="dialog-footer"><nav class="topic-nav" aria-label="주제 이동"><button type="button" id="prevTopic">이전 주제</button><button type="button" id="nextTopic">다음 주제</button></nav><p class="photo-credit">원저자·사진 Jerry Ghionis</p></div></div>
</dialog>
<dialog id="aboutDialog" aria-labelledby="aboutTitle">
<div class="dialog-head"><div><p class="dialog-kicker">원문 소개와 출처</p><h2 id="aboutTitle" tabindex="-1">책 소개와 이용 안내</h2></div><button type="button" class="close-button" id="closeAbout" aria-label="책 소개와 이용 안내 닫기">닫기</button></div>
<div class="dialog-body"><div class="about-preface"><p>이 시안은 Jerry Ghionis의 포즈 가이드를 한글로 번역하고 사진을 다시 배치한 자료입니다. 원문의 해설과, 촬영 전에 읽기 편하도록 덧붙인 ‘촬영할 때’ 안내를 구분했습니다.</p><p>원문의 ‘날씬하게’, ‘남성적·여성적’, ‘좋은 예·개선이 필요한 예’는 저자가 각 사진에서 의도한 시각적 효과를 설명합니다. 원하는 분위기와 편안한 동작을 기준으로 살펴봐 주세요.</p><p>고객 배포와 홈페이지 게시 전에는 저자의 이용 허락 범위를 확인해 주세요. 원문의 전체 저작권 안내는 아래에 함께 실었습니다.</p></div><div id="aboutContent"></div></div>
</dialog>
<script id="guideData" type="application/json">__DATA__</script>
<script>
'use strict';
(() => {
  const payload=JSON.parse(document.getElementById('guideData').textContent);
  const pages=payload.pages;
  const byPage=new Map(pages.map(page=>[page.page,page]));
  const chapters={women:{label:'여자편',start:5,end:27,summary:'서 있는 자세부터 앉은 자세까지'},men:{label:'남자편',start:29,end:50,summary:'체중, 손, 작은 동작으로 만드는 자세'},couples:{label:'커플편',start:52,end:113,summary:'두 사람의 거리와 손끝이 만드는 분위기'}};
  const statusText={good:'좋은 예',caution:'주의해서 적용',adjust:'개선이 필요한 예'};
  const asset=(path)=>payload.embedded&&payload.embedded[path]||path;
  const $=(id)=>document.getElementById(id);
  const grid=$('poseGrid'), search=$('searchInput'), poseDialog=$('poseDialog'), aboutDialog=$('aboutDialog');
  let chapter='women',shown=[],activePage=null;
  let focusBeforeDialog=null;
  const node=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;};
  const badge=(status)=>{if(!statusText[status])return null;return node('span','status status-'+status,statusText[status]);};
  function sourceText(page){return page.paragraphs.map(p=>p.text).filter(Boolean).join(' ');}
  function photo(image,page,index,multi,lazy=true){
    const img=document.createElement('img');img.src=asset(image.webp);img.width=image.width;img.height=image.height;
    img.alt=page.title+(multi?' · 사진 '+(index+1):'')+' · 원문 '+page.page+'쪽';
    if(lazy)img.loading='lazy';img.decoding='async';return img;
  }
  function gallery(page){
    const wrap=node('div','photo-gallery'+(page.images.length===1?' single':''));
    page.images.forEach((im,i)=>{const f=node('figure');const frame=node('div','photo-frame');frame.append(photo(im,page,i,page.images.length>1));f.append(frame);const caption=node('figcaption');if(page.images.length>1)caption.append(node('span','photo-number','사진 '+(i+1)));const b=badge(im.status);if(b)caption.append(b);if(caption.childNodes.length)f.append(caption);wrap.append(f);});
    return wrap;
  }
  function renderParagraphs(page,container){
    for(const paragraph of page.paragraphs){if(!paragraph.text)continue;const cls=paragraph.kind==='heading'?'source-heading':paragraph.kind==='credit'?'source-credit':'';container.append(node('p',cls,paragraph.text));}
  }
  function render(){
    const c=chapters[chapter],query=search.value.trim().toLocaleLowerCase();
    const term=({"앉기":"앉","서기":"서 있는"})[query]||query;
    const pool=pages.filter(p=>p.page>=c.start&&p.page<=c.end);
    shown=pool.filter(p=>(p.title+' '+p.client_tip+' '+sourceText(p)+' '+p.page).toLocaleLowerCase().includes(term));
    document.querySelectorAll('[data-chapter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.chapter===chapter)));
    search.placeholder=c.label+'에서 포즈 찾기';$('chapterSummary').textContent=c.label+' · '+c.summary;
    $('resultCount').textContent=query?shown.length+'개 주제 · 전체 '+pool.length+'개':pool.length+'개 주제 · 원문 '+c.start+'–'+c.end+'쪽';
    $('clearSearch').hidden=!query;$('emptyState').hidden=shown.length!==0;grid.replaceChildren();
    for(const p of shown){
      const card=node('article','pose-card');const button=node('button','card-open');button.type='button';button.setAttribute('aria-label',p.title+' 보기 · 원문 '+p.page+'쪽');
      const isSteps=p.page===5&&p.images.length===10;const frame=node('div','thumb'+(isSteps?' duo':''));
      if(isSteps){frame.append(photo(p.images[0],p,0,true),photo(p.images[8],p,8,true));}
      else {const im=p.images.find(i=>i.status==='good')||p.images[0];if(im)frame.append(photo(im,p,p.images.indexOf(im),p.images.length>1));}
      button.append(frame);const meta=node('div','card-meta');meta.append(node('span','', '원문 '+p.page+'쪽'));if(p.images.length>1)meta.append(node('span','',p.images.length+'장 비교'));
      else if(p.images[0]&&statusText[p.images[0].status])meta.append(badge(p.images[0].status));
      button.append(meta,node('span','card-title',p.title));if(p.client_tip)button.append(node('p','card-tip',p.client_tip));
      button.addEventListener('click',()=>openPose(p.page));card.append(button);grid.append(card);
    }
  }
  function setHash(value){try{history.replaceState(null,'','#'+value);}catch(e){/* File viewers may restrict history; navigation still works. */}}
  function chooseChapter(key){if(!chapters[key])return;chapter=key;search.value='';activePage=null;setHash(chapter);render();}
  function fillPose(pageNumber){
    activePage=pageNumber;const p=byPage.get(pageNumber);if(!p)return;
    $('dialogKicker').textContent=chapters[chapter].label+' · 원문 '+p.page+'쪽';$('dialogTitle').textContent=p.title;
    const body=$('poseContent');body.replaceChildren();
    if(p.client_tip){const tip=node('aside','client-tip');tip.append(node('h3','', '촬영할 때'),node('p','',p.client_tip));body.append(tip);}
    body.append(gallery(p));
    if(p.paragraphs.some(t=>t.text)){const detail=node('details','explanation');detail.append(node('summary','','원문 해설'));const paragraphs=node('div');renderParagraphs(p,paragraphs);detail.append(paragraphs);body.append(detail);}
    else body.append(node('p','photo-only-note','원문에서 사진으로만 제시한 포즈 예시입니다.'));
    const pos=shown.findIndex(item=>item.page===pageNumber);$('prevTopic').disabled=pos<=0;$('nextTopic').disabled=pos<0||pos===shown.length-1;
    setHash(chapter+'-p'+pageNumber);poseDialog.scrollTop=0;
  }
  function openPose(pageNumber){focusBeforeDialog=document.activeElement;fillPose(pageNumber);poseDialog.showModal();document.body.classList.add('dialog-open');$('dialogTitle').focus({preventScroll:true});}
  function advance(delta){const index=shown.findIndex(p=>p.page===activePage),next=shown[index+delta];if(next){fillPose(next.page);$('dialogTitle').focus({preventScroll:true});}}
  function makeAbout(){const target=$('aboutContent');if(target.childNodes.length)return;[1,2,3,4,28,51,114].forEach(n=>{const p=byPage.get(n),s=node('section','book-section');s.append(node('h3','',p.title),node('p','source-page','원문 '+p.page+'쪽'));if(p.images.length)s.append(gallery(p));renderParagraphs(p,s);target.append(s);});}
  document.querySelectorAll('[data-chapter]').forEach(button=>button.addEventListener('click',()=>chooseChapter(button.dataset.chapter)));
  search.addEventListener('input',render);
  const clear=()=>{search.value='';render();search.focus();};$('clearSearch').addEventListener('click',clear);$('showAll').addEventListener('click',clear);
  $('closePose').addEventListener('click',()=>poseDialog.close());$('prevTopic').addEventListener('click',()=>advance(-1));$('nextTopic').addEventListener('click',()=>advance(1));
  $('aboutOpen').addEventListener('click',()=>{focusBeforeDialog=document.activeElement;makeAbout();aboutDialog.showModal();document.body.classList.add('dialog-open');$('aboutTitle').focus({preventScroll:true});});
  $('closeAbout').addEventListener('click',()=>aboutDialog.close());
  [poseDialog,aboutDialog].forEach(dialog=>{dialog.addEventListener('close',()=>{document.body.classList.remove('dialog-open');if(dialog===poseDialog)setHash(chapter);if(focusBeforeDialog&&document.contains(focusBeforeDialog))focusBeforeDialog.focus({preventScroll:true});});dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});});
  const match=location.hash.match(/^#(women|men|couples)(?:-p(\d+))?$/);if(match)chapter=match[1];render();
  if(match&&match[2]){const p=byPage.get(Number(match[2]));const c=chapters[chapter];if(p&&p.page>=c.start&&p.page<=c.end)openPose(p.page);}
})();
</script>
</body>
</html>'''


def main():
    pages = json.loads((SOURCE/'translated_all.json').read_text())
    manifest = json.loads((SOURCE/'asset_manifest.json').read_text())
    images = {p['page']: p['images'] for p in manifest}
    for p in pages:
        p['images'] = [dict(x) for x in images[p['page']]]
    assert len(pages)==114
    assert sum(len(p['images']) for p in pages)==161
    paths = sorted({im['webp'] for p in pages for im in p['images']})
    assert all((OUT/path).is_file() for path in paths)
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST/'assets').mkdir(exist_ok=True)
    for path in paths:
        shutil.copy2(OUT/path, DIST/path)
    shutil.copy2(ASSETS/'wordmark.png', DIST/'assets'/'wordmark.png')
    static=TEMPLATE.replace('__WORDMARK__','assets/wordmark.png').replace('__DATA__',script_json({'pages':pages,'embedded':{}}))
    (DIST/'index.html').write_text(static)
    embedded={path:data_uri(OUT/path) for path in paths}
    offline=TEMPLATE.replace('__WORDMARK__',data_uri(ASSETS/'wordmark.png')).replace('__DATA__',script_json({'pages':pages,'embedded':embedded}))
    (OUT/'yoogeeone-posing-guide-ko.html').write_text(offline)
    config=OUT/'site'/'.openai'
    config.mkdir(exist_ok=True)
    (config/'hosting.json').write_text(json.dumps({'static':{'directory':'dist'}},indent=2)+'\n')
    report={'source_pages':len(pages),'image_placements':sum(len(p['images']) for p in pages),'unique_photo_assets':len(paths),'chapter_topics':{'women':23,'men':22,'couples':62},'source_html_bytes':len(static.encode()),'offline_html_bytes':len(offline.encode()),'reachable_about_pages':[1,2,3,4,28,51,114]}
    (SOURCE/'web_build_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
