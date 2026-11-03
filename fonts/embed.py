"""SVG에 Pretendard 글꼴을 심어 줍니다.
<img>로 불러온 SVG는 바깥 글꼴을 못 쓰기 때문에, 그림에 실제로 쓰인 글자만 골라
작은 글꼴 파일로 잘라(subset) SVG 안에 넣습니다.
Pretendard: SIL Open Font License 1.1 (fonts/LICENSE.txt)
"""
import base64, io, os, re
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = {400: "Pretendard-Regular.woff2", 700: "Pretendard-Bold.woff2", 800: "Pretendard-ExtraBold.woff2"}
FAMILY = "SoramPretendard"

def _subset(path, text):
    font = TTFont(path)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
    sub = subset.Subsetter(opts); sub.populate(text=text); sub.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()

def style_block(svg_body):
    """svg_body에 들어간 글자를 모아 굵기별 @font-face <style>을 만든다."""
    texts = re.findall(r">([^<>]+)</text>", svg_body)
    chars = "".join(sorted(set("".join(texts)))) + "0123456789"
    chars = chars.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    faces = []
    for w, fn in WEIGHTS.items():
        b64 = _subset(os.path.join(HERE, fn), chars)
        faces.append(f"@font-face{{font-family:{FAMILY};font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "<defs><style>" + "".join(faces) + "</style></defs>"

FONT_STACK = f"{FAMILY}, Pretendard, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
