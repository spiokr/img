"""keywords/common.json -> keywords/common.svg
SORAM 공통 키워드 이미지를 그립니다. 외부 패키지 없이 파이썬만 있으면 됩니다.
사용법: python keywords/render.py  (GitHub Actions가 자동으로 실행합니다)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts"))
from embed import style_block, FONT_STACK
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "common.json"), encoding="utf-8"))

# ---- 통일 테마 (SORAM 차콜 · 아이보리 · 더스티 로즈) ----
BG, CARD, ROW = "#0f0d10", "#171418", "#1f1a20"
LINE, ROSE, ROSE_DIM = "#2e262d", "#c9a3ab", "#8c7f86"
IVORY, TEXT, SUB, NOTE = "#efe9e2", "#d9d2cb", "#9a8f96", "#e0a27e"
FONT = FONT_STACK
MARKS = ["◆", "✦", "◉", "✧"]

W, PAD, IN = 360, 12, 10           # 전체 폭, 바깥 여백, 카드 안쪽 여백
TW = W - PAD * 2 - IN * 2 - 14      # 설명 글 줄 폭 (왼쪽 띠 몫 제외)

def text_w(s, size):
    w = 0
    for ch in s:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3000 <= o <= 0x9FFF: w += 1.0
        elif ch == " ": w += 0.3
        elif ch in "il.,:!|'": w += 0.32
        elif ch.isupper() or ch in "mwMW@": w += 0.68
        else: w += 0.56
    return w * size

def wrap(s, size, width):
    lines, cur = [], ""
    for word in s.split(" "):
        test = (cur + " " + word).strip()
        if text_w(test, size) <= width: cur = test; continue
        if cur: lines.append(cur)
        cur = word
        while text_w(cur, size) > width:          # 아주 긴 낱말은 글자 단위로 자르기
            i = len(cur)
            while i > 1 and text_w(cur[:i], size) > width: i -= 1
            lines.append(cur[:i]); cur = cur[i:]
    if cur: lines.append(cur)
    return lines

out, y = [], 0
def t(x, y, s, size, fill, weight=400, anchor="start", ls=0):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{escape(s)}</text>')

# 헤더
y = 30
t(W / 2, y, "COMMON KEYWORDS", 10, ROSE, 700, "middle", 4); y += 26
t(W / 2, y, data["title"], 22, IVORY, 800, "middle", 1); y += 20
t(W / 2, y, data["subtitle"], 13, SUB, 400, "middle"); y += 22

for si, sec in enumerate(data["sections"]):
    # 섹션 제목
    y += 8
    out.append(f'<rect x="{PAD}" y="{y}" width="{W - PAD*2}" height="30" rx="8" fill="{ROW}"/>')
    out.append(f'<rect x="{PAD}" y="{y}" width="3" height="30" rx="1.5" fill="{ROSE}"/>')
    t(PAD + 14, y + 20, f"{MARKS[si % len(MARKS)]}  {sec['name']}", 15.5, IVORY, 700)
    y += 38
    card_top = y; body = []
    yy = y + IN
    for item in sec["items"]:
        name, en, desc = item[0], item[1], item[2]
        note = item[3] if len(item) > 3 else ""
        dl = wrap(desc, 14.5, TW); nl = wrap("※ " + note, 13, TW) if note else []
        h = 10 + 20 + len(dl) * 20 + len(nl) * 17 + 8
        x0 = PAD + IN
        body.append(f'<rect x="{x0}" y="{yy}" width="{W - PAD*2 - IN*2}" height="{h}" rx="8" fill="{ROW}"/>')
        body.append(f'<rect x="{x0}" y="{yy}" width="2" height="{h}" rx="1" fill="{ROSE_DIM}"/>')
        ty = yy + 10 + 15
        nw = text_w(name, 16.5)
        body.append(f'<text x="{x0+12}" y="{ty}" font-size="16.5" font-weight="800" fill="{IVORY}">{escape(name)}</text>')
        body.append(f'<text x="{x0+12+nw+7}" y="{ty}" font-size="12.5" fill="{SUB}">{escape(en)}</text>')
        ty += 20
        for ln in dl:
            body.append(f'<text x="{x0+12}" y="{ty}" font-size="14.5" fill="{TEXT}">{escape(ln)}</text>'); ty += 20
        for ln in nl:
            body.append(f'<text x="{x0+12}" y="{ty}" font-size="13" fill="{NOTE}">{escape(ln)}</text>'); ty += 17
        yy += h + 6
    card_h = yy - card_top + IN - 6
    out.append(f'<rect x="{PAD}" y="{card_top}" width="{W - PAD*2}" height="{card_h}" rx="12" fill="{CARD}" stroke="{LINE}"/>')
    out.extend(body)
    y = card_top + card_h + 6

y += 14
t(W / 2, y, "made by SORAM", 10, ROSE_DIM, 400, "middle", 2); y += 16
H = int(y)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{escape(FONT)}">'
       + style_block("".join(out)) + f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>' + "".join(out) + "</svg>")
open(os.path.join(HERE, "common.svg"), "w", encoding="utf-8").write(svg)
print(f"common.svg  {W}x{H}")
