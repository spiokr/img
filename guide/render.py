"""guide/guide.json -> guide/guide.svg
SORAM 설정 가이드(STEP 1~3) 이미지를 그립니다. 외부 패키지 없이 파이썬만 있으면 됩니다.
사용법: python guide/render.py  (GitHub Actions가 자동으로 실행합니다)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts"))
from embed import style_block, FONT_STACK
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "guide.json"), encoding="utf-8"))

# ---- 티팟 UI 톤 ----
BG, CARD, SOFT, LINE = "#f4f5f6", "#ffffff", "#f4f5f6", "#eeeeee"
INK, GREY, LIGHT, GREEN, GREEN_D = "#1a1a1a", "#8b8b8b", "#a3a3a3", "#13c46c", "#13a35c"
BADGE = {"green": ("#e7f8ef", "#13a35c"), "orange": ("#fbeee8", "#c25a3a"), "black": ("#1a1a1a", "#ffffff")}
FONT = FONT_STACK

W, PAD, IN = 360, 10, 14
CW = W - PAD * 2           # 카드 폭
TX = PAD + IN               # 카드 안 글 시작
TW = CW - IN * 2            # 카드 안 글 폭

def text_w(s, size):
    w = 0
    for ch in s:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3000 <= o <= 0x9FFF: w += 1.0
        elif o > 0x2000: w += 1.1
        elif ch == " ": w += 0.3
        elif ch in "il.,:!|'·": w += 0.32
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
        while text_w(cur, size) > width:
            i = len(cur)
            while i > 1 and text_w(cur[:i], size) > width: i -= 1
            lines.append(cur[:i]); cur = cur[i:]
    if cur: lines.append(cur)
    return lines

out = []
def T(x, y, s, size, fill, weight=400, anchor="start"):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(str(s))}</text>')
def R(x, y, w, h, r, fill, extra=""):
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" {extra}/>')
def para(x, y, s, size, fill, width, lh):
    for ln in wrap(s, size, width):
        T(x, y, ln, size, fill); y += lh
    return y
def pill(xr, yc, label, bg, fg, size=10.5):
    w = text_w(label, size) + 16
    R(xr - w, yc - 10, w, 20, 10, bg); T(xr - w / 2, yc + 3.8, label, size, fg, 700, "middle")
def slider(x, y, w, pct):
    R(x, y, w, 6, 3, "#e8e8e8"); R(x, y, max(6, w * pct / 100), 6, 3, GREEN)
    cx = x + w * pct / 100
    out.append(f'<circle cx="{cx:.1f}" cy="{y+3}" r="7.5" fill="#ffffff" stroke="{GREEN}" stroke-width="3"/>')
def segmented(x, y, w, a, b, on, dark=False):
    R(x, y, w, 36, 12, SOFT)
    hw = (w - 6) / 2
    R(x + 3 + hw * on, y + 3, hw, 30, 10, "#222222" if dark else GREEN)
    for i, lab in enumerate([a, b]):
        T(x + 3 + hw * i + hw / 2, y + 23, lab, 13, "#ffffff" if i == on else GREY, 700 if i == on else 400, "middle")
def check(xr, yc):
    R(xr - 22, yc - 11, 22, 22, 6, GREEN); T(xr - 11, yc + 5, "✓", 13, "#ffffff", 700, "middle")
def step_head(y, n, title):
    w = text_w(f"STEP {n}", 10.5) + 16
    R(TX, y - 13, w, 18, 9, INK); T(TX + w / 2, y, f"STEP {n}", 10.5, "#ffffff", 800, "middle")
    T(TX + w + 7, y, title, 14, INK, 800)
def setting(y, name, value, desc, width=TW, x=TX):
    T(x, y, name, 14, INK, 700)
    if value: T(x + width, y, value, 13, GREEN_D, 700, "end")
    return para(x, y + 19, desc, 12, GREY, width, 18)

# ---- 헤더 ----
y = 26
T(PAD + 4, y, D["eyebrow"], 12.5, GREEN_D, 700); y += 24
T(PAD + 4, y, D["title"], 19, INK, 800); y += 20
y = para(PAD + 4, y, D["subtitle"], 12.5, GREY, CW - 8, 18) + 6

def section(builder):
    global y
    top = y; mark = len(out)
    y = builder(y + IN + 14) + IN - 4
    out.insert(mark, f'<rect x="{PAD}" y="{top}" width="{CW}" height="{y-top}" rx="16" fill="{CARD}"/>')
    y += 10

# ---- STEP 1 ----
def s1(y):
    M = D["models"]
    step_head(y, 1, "모델 고르기"); y += 20
    y = para(TX, y, M["hint"], 11.5, LIGHT, TW, 16) + 2
    for icon, col, name, cost, badge, kind in M["list"]:
        R(TX, y, TW, 48, 12, SOFT)
        T(TX + 14, y + 29, icon, 15, col)
        T(TX + 34, y + 21, name, 14.5, INK, 700)
        T(TX + 34, y + 37, cost, 11.5, GREY)
        bg, fg = BADGE[kind]; pill(TX + TW - 10, y + 24, badge, bg, fg)
        y += 54
    y += 4
    for n in M["notes"]:
        y = para(TX, y + 4, "· " + n, 11.5, GREY, TW, 16)
    y += 8
    lines = wrap(M["tip_body"], 12, TW - 24)
    h = 20 + 20 + len(lines) * 18
    R(TX, y, TW, h, 12, "#fbeee8")
    T(TX + 12, y + 22, M["tip_title"], 12, "#c25a3a", 700)
    yy = y + 42
    for ln in lines: T(TX + 12, yy, ln, 12, "#7a3b26"); yy += 18
    return y + h
section(s1)

# ---- STEP 2 ----
def s2(y):
    L = D["llm"]
    step_head(y, 2, "LLM 설정"); y += 20
    y = para(TX, y, L["hint"], 11.5, LIGHT, TW, 16) + 4
    a, b, on = L["plan"]; segmented(TX, y, TW, a, b, on); y += 56
    R(TX, y - 8, TW, 1, 0, LINE); y += 12
    n, v, d, pct = L["max_tokens"]; y = setting(y, n, v, d); slider(TX + 8, y + 2, TW - 16, pct); y += 32
    n, d, a, b, on = L["reasoning"]; y = setting(y, n, "", d); segmented(TX, y, TW, a, b, on, dark=True); y += 64
    n, d, lo, hi = L["length"]; T(TX, y, n, 14, INK, 700); check(TX + TW, y - 5)
    y = para(TX, y + 19, d, 12, GREY, TW, 18) + 4
    bw = (TW - 70) / 2
    R(TX, y, bw, 34, 8, SOFT); T(TX + bw / 2, y + 22, lo, 13, INK, 400, "middle")
    T(TX + bw + 12, y + 22, "~", 13, GREY, 400, "middle")
    R(TX + bw + 24, y, bw, 34, 8, SOFT); T(TX + bw * 1.5 + 24, y + 22, hi, 13, INK, 400, "middle")
    T(TX + TW, y + 22, "(단어)", 11, LIGHT, 400, "end"); y += 58
    n, d = L["web"]; T(TX, y, n, 14, INK, 700); check(TX + TW, y - 5)
    y = para(TX, y + 19, d, 12, GREY, TW, 18) + 8
    R(TX, y, TW, 1, 0, LINE); y += 24
    n, v, d, pct = L["lorebook"]; y = setting(y, n, v, d); slider(TX + 8, y + 2, TW - 16, pct); y += 14
    return y
section(s2)

# ---- STEP 3 ----
def s3(y):
    M = D["memory"]
    step_head(y, 3, "단기 기억 설정"); y += 20
    y = para(TX, y, M["hint"], 11.5, LIGHT, TW, 16) + 8
    n, v, d, pct = M["recent"]; y = setting(y, n, v, d); slider(TX + 8, y + 2, TW - 16, pct); y += 30
    T(TX, y, M["choose"], 12.5, INK, 700); y += 12
    for p in M["presets"]:
        top = y; mark = len(out)
        iy = y + 24
        T(TX + 12, iy + 4, p["icon"], 17, INK)
        T(TX + 40, iy, p["title"], 14, INK, 800)
        T(TX + 40, iy + 17, p["sub"], 11.5, GREY)
        iy += 34
        itop = iy; imark = len(out); iy += 24
        for n, v, d, pct in p["items"]:
            iy = setting(iy, n, v, d, TW - 44, TX + 22)
            slider(TX + 30, iy + 2, TW - 60, pct); iy += 34
        out.insert(imark, f'<rect x="{TX+8}" y="{itop}" width="{TW-16}" height="{iy-itop-12}" rx="12" fill="#ffffff"/>')
        y = iy - 4
        out.insert(mark, f'<rect x="{TX}" y="{top}" width="{TW}" height="{y-top}" rx="14" fill="{SOFT}"/>')
        y += 10
    for kind, title, body in M["tips"]:
        bg, tc, bc = ("#e7f8ef", GREEN_D, "#1f6b45") if kind == "green" else (SOFT, INK, "#5f5f5f")
        lines = wrap(body, 12, TW - 24)
        h = 20 + 20 + len(lines) * 18
        R(TX, y, TW, h, 12, bg)
        T(TX + 12, y + 22, title, 12, tc, 700)
        yy = y + 42
        for ln in lines: T(TX + 12, yy, ln, 12, bc); yy += 18
        y += h + 8
    return y - 8
section(s3)

H = int(y + 4)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{escape(FONT)}">'
       + style_block("".join(out)) + f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>' + "".join(out) + "</svg>")
open(os.path.join(HERE, "guide.svg"), "w", encoding="utf-8").write(svg)
print(f"guide.svg  {W}x{H}")
