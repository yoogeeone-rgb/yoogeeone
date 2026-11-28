from pathlib import Path
import json, math, re
import fitz
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = Path(__file__).resolve().parent
TMP = ROOT/'editorial'
PAGES = {p['page']: p for p in json.loads((TMP/'translated_all.json').read_text())}
ASSETS = {p['page']: p['images'] for p in json.loads((TMP/'asset_manifest.json').read_text())}
EDITORIAL = json.loads((TMP/'client_editorial.json').read_text())
FONTS = TMP/'fonts'
FONTS.mkdir(exist_ok=True)

# Keep original CFF glyph IDs: this is necessary for reliable CJK PDF rendering.
alphabet = ''.join(chr(i) for i in range(0xAC00, 0xD7A4))
alphabet += ''.join(chr(i) for i in range(0x20, 0x300))
alphabet += ''.join(chr(i) for i in range(0x2000, 0x2070))
alphabet += '가나다라마바사아자차카타파하·©→–—“”‘’'
for weight in ['Regular', 'Bold']:
    target = FONTS/f'Korean-{weight}.otf'
    face = TTFont(f'/usr/share/fonts/opentype/noto/NotoSansCJK-{weight}.ttc', fontNumber=1)
    sub = subset.Subsetter(options=subset.Options(retain_gids=True))
    sub.populate(text=alphabet)
    sub.subset(face)
    face.save(target)

REG = fitz.Font(fontfile=str(FONTS/'Korean-Regular.otf'))
BOLD = fitz.Font(fontfile=str(FONTS/'Korean-Bold.otf'))
W, H, M = 960, 720, 40
BLACK = (0.035, 0.035, 0.035)
GRAY = (0.39, 0.39, 0.39)
LIGHT = (0.91, 0.91, 0.91)
STATUS = {'good': ('좋은 예시', (0.21, .43, .22)),
          'adjust': ('개선이 필요한 예시', (.65, .16, .18)),
          'caution': ('주의해서 적용할 예시', (.59, .39, .04)),
          'none': ('', GRAY)}

def wrap(text, width, size, bold=False):
    font = BOLD if bold else REG
    result=[]
    for line in text.split('\n'):
        if not line.strip():
            result.append('')
            continue
        current=''
        # Break Korean at natural word boundaries where possible, long runs by character.
        for word in re.findall(r'\S+\s*', line):
            if font.text_length(current+word, fontsize=size) <= width:
                current += word
            else:
                if current.strip(): result.append(current.rstrip())
                current=''
                for ch in word:
                    if current and font.text_length(current+ch, fontsize=size)>width:
                        result.append(current.rstrip()); current=''
                    current += ch
        if current.strip(): result.append(current.rstrip())
    return result

def height(text, width, size=11.5, leading=None, bold=False):
    return len(wrap(text,width,size,bold))*(leading or size*1.52)

def text(page, value, x, y, width, size=11.5, leading=None, bold=False, color=BLACK):
    step=leading or size*1.52
    for line in wrap(value,width,size,bold):
        if line:
            page.insert_text((x,y+size), line, fontname='KRB' if bold else 'KR', fontsize=size, color=color)
        y += step
    return y

def paragraphs_height(paras, width, size):
    return sum(height(p['text'],width,size)+9 for p in paras if p['text'])

def paragraphs(page, paras, x, y, width, size=11.5):
    for p in paras:
        if not p['text']: continue
        is_heading=p['kind']=='heading'
        y=text(page,p['text'],x,y,width,size if not is_heading else size+1,bold=is_heading)
        y+=9
    return y

def image(page, asset, rect):
    p=ROOT/asset['jpg']
    page.insert_image(fitz.Rect(rect), filename=str(p), keep_proportion=True)

def new_page(doc, chapter, source=None, title=None, continuation=None):
    p=doc.new_page(width=W,height=H)
    p.insert_font(fontname='KR',fontfile=str(FONTS/'Korean-Regular.otf'))
    p.insert_font(fontname='KRB',fontfile=str(FONTS/'Korean-Bold.otf'))
    p.insert_image(fitz.Rect(M,25,M+180,64), filename=str(ROOT/'assets/wordmark.png'))
    text(p,'촬영 가이드 / '+chapter,665,36,255,11,bold=True)
    p.draw_line((M,82),(W-M,82),color=BLACK,width=.7)
    if title:
        label=title+(f' · {continuation}' if continuation else '')
        size=25
        while BOLD.text_length(label,fontsize=size)>W-2*M and size>18: size-=.5
        text(p,label,M,102,W-2*M,size,bold=True)
    bottom='원저자·사진 © 2023 Jerry Ghionis  /  한국어 번역·편집 시안'
    text(p,bottom,M,H-31,650,8.2,color=GRAY)
    if source is not None:
        text(p,f'원문 {source:03d}  /  {len(doc):03d}',W-190,H-31,150,8.2,color=GRAY)
    else:
        text(p,f'{len(doc):03d}',W-85,H-31,45,8.2,color=GRAY)
    return p

def tip(page, value, y):
    if not value: return y
    h=height(value,820,11.5)+18
    page.draw_rect(fitz.Rect(M,y,W-M,y+h),color=None,fill=(.966,.966,.966))
    page.draw_rect(fitz.Rect(M,y,M+2,y+h),color=None,fill=BLACK)
    text(page,value,M+14,y+7,820,11.5)
    return y+h+19

def cover(doc, key, chapter, sourcepage):
    p=new_page(doc,chapter,sourcepage)
    a=ASSETS[sourcepage][0]
    image(p,a,(425,103,920,650))
    text(p,chapter,M,142,365,54,bold=True)
    text(p,'촬영 전, 가볍게 읽는\n포즈 가이드',M,226,350,24,bold=True)
    text(p,'자세를 외우기보다\n마음에 드는 분위기를 찾아보세요.',M,322,340,14)
    text(p,'원저자·사진  Jerry Ghionis\n한국어 번역·재편집  YOOGEEONE',M,407,350,11.7)
    text(p,'검토용 시안\n고객 배포 및 홈페이지 공개를 위한\n원저자의 이용 허락은 확인되지 않았습니다.',M,517,350,10.5,color=GRAY)
    text(p,'원서: 여성·남성·커플을 위한 포즈 가이드\n100쪽 이상의 전자책 · 2023',M,598,350,9.5,color=GRAY)

def intro(doc, chapter):
    p=new_page(doc,chapter,3,'읽기 전에')
    text(p,'촬영을 앞둔 손님께',M,150,390,14,bold=True)
    text(p,EDITORIAL['intro'],M,183,390,12)
    text(p,'이 가이드 읽는 방법',M,414,390,14,bold=True)
    text(p,'각 페이지 위의 회색 안내는 촬영할 때 따라 해 볼 수 있도록 덧붙인 문장입니다. 사진 옆이나 아래의 본문은 원문의 전체 설명을 번역했습니다.\n\n사진 1, 사진 2는 해당 페이지의 사진을 구분하는 번호입니다. 원문의 색상 표시는 같은 의미의 글자 표시로 옮겼습니다.\n\n목차는 PDF의 책갈피에서 확인하실 수 있습니다.',M,446,390,11.5)
    rp=PAGES[3]['paragraphs']
    size=11.3
    while paragraphs_height(rp,440,size)>500 and size>10: size-=.2
    text(p,'원문 서문',480,150,440,14,bold=True)
    paragraphs(p,rp,480,183,440,size)

def about(doc, chapter):
    p=new_page(doc,chapter,2,'저자 소개')
    image(p,ASSETS[2][0],(M,153,455,651))
    text(p,'Jerry Ghionis',505,151,415,25,bold=True)
    text(p,'포토그래퍼 / 교육자 / 니콘 앰배서더',505,196,415,11.2,color=GRAY)
    paragraphs(p,PAGES[2]['paragraphs'],505,235,415,11.8)
    text(p,'약력은 2023년 원문에 수록된 내용을 번역했습니다.',505,625,415,9.3,color=GRAY)

def badge(page, asset, num, x, y, width, multi):
    label,color=STATUS[asset['status']]
    parts=([f'사진 {num}'] if multi else [])+([label] if label else [])
    if parts:text(page,' · '.join(parts),x,y,width,10.2,bold=True,color=color)

def topic(doc, chapter, sourcepage, assets_subset=None, continuation=None):
    item=PAGES[sourcepage]
    all_assets=ASSETS[sourcepage]
    assets=assets_subset or all_assets
    p=new_page(doc,chapter,sourcepage,item['title'],continuation)
    top=tip(p,item.get('client_tip',''),149)
    bottom=650
    allowed={a['xref'] for a in assets}
    all_xrefs={a['xref'] for a in all_assets}
    paras=[]
    for para in item['paragraphs']:
        if not para['text']: continue
        if para['kind']=='heading' and para['text']==item['title']:continue
        refs=set(para['image_xrefs'])
        if refs and refs <= all_xrefs and not refs & allowed: continue
        paras.append(para)
    if len(assets)==1:
        a=assets[0]
        if not paras:
            badge(p,a,1,340,top,400,False)
            image(p,a,(250,top+25,710,bottom))
        else:
            badge(p,a,1,M,top,445,False)
            image(p,a,(M,top+27,490,bottom))
            text(p,'원문 해설',535,top,385,10.5,bold=True,color=GRAY)
            size=12
            while paragraphs_height(paras,385,size)>bottom-top-29 and size>10:
                size-=.2
            y=paragraphs(p,paras,535,top+29,385,size)
            if y>bottom+5: raise ValueError(f'Text overflow page {sourcepage}: {y}')
    elif assets:
        n=len(assets); gap=18; cw=(W-2*M-gap*(n-1))/n
        unique={a['xref']:[] for a in assets}
        common=[]
        for para in paras:
            refs=para['image_xrefs']
            if len(refs)==1 and refs[0] in unique:unique[refs[0]].append(para)
            else:common.append(para)
        csize=11.2
        common_h=paragraphs_height(common,W-2*M,11.5) if common else 0
        caption_h=max(paragraphs_height(unique[a['xref']],cw,csize) for a in assets)
        image_h=min(385,bottom-top-25-caption_h-common_h-(18 if common else 0)-10)
        if image_h<155: raise ValueError(f'Photo too small on {sourcepage}: {image_h}')
        for i,a in enumerate(assets):
            x=M+i*(cw+gap)
            idx=next(j+1 for j,v in enumerate(all_assets) if v['xref']==a['xref'])
            badge(p,a,idx,x,top,cw,True)
            image(p,a,(x,top+25,x+cw,top+25+image_h))
            y=paragraphs(p,unique[a['xref']],x,top+25+image_h+10,cw,csize)
            if y>bottom+5:raise ValueError(f'Caption overflow {sourcepage}')
        common_y=top+25+image_h+10+caption_h+9
        if common:
            p.draw_line((M,common_y-8),(W-M,common_y-8),color=LIGHT,width=.7)
            y=paragraphs(p,common,M,common_y,W-2*M,11.5)
            if y>bottom+8:raise ValueError(f'Common overflow {sourcepage}: {y}')
    else:
        paragraphs(p,paras,M,top,W-2*M,12)
    return len(doc)

def credits(doc, chapter):
    p=new_page(doc,chapter,114,'연습과 경험, 그리고 이용 안내')
    image(p,ASSETS[114][0],(M,150,430,650))
    y=paragraphs(p,PAGES[114]['paragraphs'],480,156,440,12)
    p.draw_line((480,y+6),(920,y+6),color=LIGHT,width=.7)
    text(p,'편집 안내',480,y+22,440,13,bold=True)
    text(p,'첨부된 원서를 한국어로 번역하고, 홈페이지의 흰 배경·검정 타이포그래피·사진 중심 구성에 맞춰 재배치한 검토용 파일입니다. 촬영 안내와 탐색용 제목은 편집 과정에서 추가했습니다.\n\n원저자의 사진을 YOOGEEONE의 촬영 결과물로 표시하지 않았습니다. 고객에게 제공하거나 홈페이지에 공개할 때에는 구매 시 받은 별도 이용 조건 또는 저자의 서면 허락을 확인해 주세요.',480,y+53,440,10.5,color=GRAY)

def build_book(key, chapter, source_cover, source_pages):
    doc=fitz.open()
    cover(doc,key,chapter,source_cover)
    toc=[[1,chapter,1]]
    intro(doc,chapter);toc.append([1,'읽기 전에 · 원문 서문',len(doc)])
    about(doc,chapter);toc.append([1,'저자 소개',len(doc)])
    for sp in source_pages:
        first=len(doc)+1
        assets=ASSETS[sp]
        if len(assets)>5:
            groups=[assets[i:i+5] for i in range(0,len(assets),5)]
            for i,g in enumerate(groups):topic(doc,chapter,sp,g,f'{i+1}/{len(groups)}')
        else:topic(doc,chapter,sp)
        toc.append([1,f'{PAGES[sp]["title"]} (원문 {sp}쪽)',first])
    credits(doc,chapter);toc.append([1,'연습과 경험 · 저작권 안내',len(doc)])
    doc.set_toc(toc)
    doc.set_metadata({'title':f'YOOGEEONE 포즈 가이드 · {chapter} · 한국어 검토본',
                      'author':'Jerry Ghionis (original author and photographs)',
                      'subject':'User-supplied book translated into Korean and reformatted for private review; redistribution permission not verified.',
                      'keywords':'한국어, 포즈, 촬영 가이드, YOOGEEONE, Jerry Ghionis',
                      'creator':'Korean translation and editorial layout'})
    path=ROOT/f'yoogeeone-posing-{key}-ko.pdf'
    doc.save(path,garbage=4,deflate=True)
    count=len(doc);doc.close()
    check=fitz.open(path)
    missing=[]
    for pg in check:
        t=pg.get_text()
        if '�' in t:missing.append(pg.number+1)
    print(json.dumps({'file':str(path),'pages':count,'bytes':path.stat().st_size,'replacement_character_pages':missing},ensure_ascii=False))
    qa=TMP/'qa';qa.mkdir(exist_ok=True)
    for idx in sorted({0,1,2,3, min(5,count-1), min(10,count-1),count-1}):
        check[idx].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(str(qa/f'{key}-{idx+1:03d}.png'))
    return {'file':str(path),'pages':count,'bytes':path.stat().st_size}

if __name__=='__main__':
    result=[build_book('women','여자편',4,range(5,28)),
            build_book('men','남자편',28,range(29,51)),
            build_book('couples','커플편',51,range(52,114))]
    (TMP/'pdf_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
