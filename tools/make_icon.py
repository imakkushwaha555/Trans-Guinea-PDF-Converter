"""Render assets/logo.svg geometry to app.ico and static PNGs (Pillow only)."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
BURGUNDY, WHITE, GOLD = "#6f1738", "#ffffff", "#f2b632"
SCALE = 4  # supersampling for smooth edges


def render(size: int) -> Image.Image:
    px = size * SCALE
    k = px / 256
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def poly(points, fill):
        d.polygon([(x * k, y * k) for x, y in points], fill=fill)

    def rect(x0, y0, x1, y1, fill):
        d.rectangle([x0 * k, y0 * k, x1 * k - 1, y1 * k - 1], fill=fill)

    d.rounded_rectangle([0, 0, px - 1, px - 1], radius=56 * k, fill=BURGUNDY)
    poly([(64, 48), (150, 48), (192, 90), (192, 208), (64, 208)], WHITE)
    poly([(150, 48), (192, 90), (150, 90)], GOLD)
    rect(88, 106, 168, 126, BURGUNDY)
    rect(118, 126, 138, 184, BURGUNDY)
    rect(118, 164, 160, 184, BURGUNDY)
    poly([(160, 150), (186, 174), (160, 198)], GOLD)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    render(256).save(assets / "app.ico", sizes=[(s, s) for s in sizes])
    render(512).save(assets / "app.icns")
    render(256).save(assets / "logo.png")
    render(64).save(ROOT / "static" / "logo.png")
    render(32).save(ROOT / "static" / "favicon.png")


if __name__ == "__main__":
    main()
