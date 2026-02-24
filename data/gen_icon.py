"""OKXUS 앱 아이콘 PNG 생성"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def find_content_bounds(img):
    """이미지에서 실제 콘텐츠(투명 아닌 부분)의 바운딩 박스를 찾는다."""
    arr = np.array(img)
    alpha = arr[:, :, 3] if arr.shape[2] == 4 else np.ones(arr.shape[:2]) * 255
    rows = np.where(alpha.any(axis=1))[0]
    cols = np.where(alpha.any(axis=0))[0]
    if len(rows) == 0:
        return 0, 0, img.width, img.height
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1

def create_icon(size, output_path, is_adaptive=False):
    bg_color = (13, 17, 23, 255)
    text_color = (204, 255, 0, 255)

    font_size = int(size * 0.18) if is_adaptive else int(size * 0.25)
    try:
        font = ImageFont.truetype("segoeuib.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()

    text = "OKXUS"

    # 큰 캔버스에 텍스트 그리기
    big = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
    big_draw = ImageDraw.Draw(big)
    big_draw.text((size // 2, size // 2), text, fill=text_color, font=font)

    # 실제 텍스트 영역 크롭
    x1, y1, x2, y2 = find_content_bounds(big)
    text_cropped = big.crop((x1, y1, x2, y2))

    # 세로 1.35배 늘리기
    tw, th = text_cropped.size
    new_h = int(th * 1.35)
    text_stretched = text_cropped.resize((tw, new_h), Image.LANCZOS)

    # 배경 이미지
    img = Image.new('RGBA', (size, size), bg_color)

    # 정중앙 배치
    px = (size - text_stretched.width) // 2
    py = (size - text_stretched.height) // 2
    img.paste(text_stretched, (px, py), text_stretched)

    if not is_adaptive:
        r = int(size * 0.21)
        mask = Image.new('L', (size, size), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
        result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        result.paste(img, mask=mask)
        result.save(output_path)
    else:
        img.save(output_path)

    print(f"  {output_path} ({size}x{size})")

if __name__ == "__main__":
    print("Generating icons...")
    os.makedirs("okxus/mobile/assets", exist_ok=True)
    create_icon(1024, "okxus/mobile/assets/icon.png")
    create_icon(1024, "okxus/mobile/assets/adaptive-icon.png", is_adaptive=True)
    create_icon(512, "okxus/mobile/assets/splash-icon.png")
    create_icon(192, "okxus/mobile/assets/favicon.png")
    print("Done!")
