#!/usr/bin/env python3
import argparse
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from PIL import Image, ImageEnhance, ImageFilter


# -------------------- core --------------------
DEFAULT_CHARS_SIMPLE = "@#*."
DEFAULT_CHARS_GRADIENT = "@%#*+=-:. "  # dark -> light


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def map_pixel_to_char(value_0_255: int, chars: str) -> str:
    # 0 = black -> first char; 255 = white -> last char
    if not chars:
        chars = DEFAULT_CHARS_GRADIENT
    idx = int((value_0_255 / 255) * (len(chars) - 1))
    return chars[idx]


def resize_keep_aspect(img: Image.Image, width: Optional[int], scale: Optional[float]) -> Image.Image:
    w, h = img.size

    if scale is not None:
        scale = clamp(scale, 0.05, 5.0)
        new_w = max(1, int(w * scale))
    elif width is not None:
        new_w = max(1, width)
    else:
        new_w = 80  # default

    # ASCII characters are taller than wide in terminal -> compensate height (~0.5–0.6)
    aspect = h / w
    new_h = max(1, int(aspect * new_w * 0.55))

    return img.resize((new_w, new_h), Image.BICUBIC)


def apply_filters(
    img: Image.Image,
    grayscale: bool,
    invert: bool,
    contrast: Optional[float],
    blur: Optional[float],
) -> Image.Image:
    out = img

    if grayscale:
        out = out.convert("L")  # 8-bit gray
    else:
        out = out.convert("RGB")

    if invert:
        if out.mode == "L":
            out = Image.eval(out, lambda p: 255 - p)
        else:
            # invert each channel
            r, g, b = out.split()
            r = Image.eval(r, lambda p: 255 - p)
            g = Image.eval(g, lambda p: 255 - p)
            b = Image.eval(b, lambda p: 255 - p)
            out = Image.merge("RGB", (r, g, b))

    if contrast is not None:
        contrast = clamp(contrast, 0.1, 5.0)
        out = ImageEnhance.Contrast(out).enhance(contrast)

    if blur is not None and blur > 0:
        blur = clamp(blur, 0.1, 10.0)
        out = out.filter(ImageFilter.GaussianBlur(radius=blur))

    return out


def image_to_ascii(img: Image.Image, chars: str) -> str:
    if img.mode != "L":
        img = img.convert("L")

    w, h = img.size
    pix = img.load()

    lines = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(map_pixel_to_char(pix[x, y], chars))
        lines.append("".join(row))
    return "\n".join(lines)


# -------------------- text banner (simple 5x7) --------------------
FONT_5X7 = {
    "A": ["  #  ", " # # ", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["#####", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "# #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["#   #", "#   #", "#   #", "#####", "    #", "    #", "    #"],
    "5": ["#####", "#    ", "#    ", "#### ", "    #", "    #", "#### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
}


def text_to_banner(text: str, spacing: int = 1) -> str:
    text = text.upper()
    rows = [""] * 7
    for ch in text:
        glyph = FONT_5X7.get(ch, FONT_5X7[" "])
        for i in range(7):
            rows[i] += glyph[i] + (" " * spacing)
    return "\n".join(rows)


# -------------------- CLI --------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="ascii_art")

    p.add_argument("input", nargs="?", help="input image (png/jpg). Optional if using --text.")
    p.add_argument("--output", type=str, default=None, help="export to text file")
    p.add_argument("--preview", action="store_true", help="print result to terminal")

    p.add_argument("--width", type=int, default=None, help="ASCII width in characters (e.g. 80)")
    p.add_argument("--scale", type=float, default=None, help="scale factor (e.g. 0.5)")

    p.add_argument("--chars", type=str, default=None, help='charset e.g. "@#*+=-:. "')
    p.add_argument("--charset", type=str, default=None, help='simple | gradient (shortcut)')

    # filters
    p.add_argument("--filter", type=str, default=None, help="grayscale | invert | contrast | blur (single)")
    p.add_argument("--grayscale", action="store_true")
    p.add_argument("--invert", action="store_true")
    p.add_argument("--contrast", type=float, default=None)
    p.add_argument("--blur", type=float, default=None)

    # text banner
    p.add_argument("--text", type=str, default=None, help='convert text to ASCII banner, e.g. "HELLO"')
    p.add_argument("--font", type=str, default="banner", help="banner (default)")

    return p.parse_args()


def resolve_chars(args: argparse.Namespace) -> str:
    if args.chars is not None:
        return args.chars
    if args.charset == "simple":
        return DEFAULT_CHARS_SIMPLE
    return DEFAULT_CHARS_GRADIENT


def main() -> None:
    args = parse_args()
    chars = resolve_chars(args)

    # support --filter single flag
    if args.filter:
        f = args.filter.lower()
        if f == "grayscale":
            args.grayscale = True
        elif f == "invert":
            args.invert = True
        elif f.startswith("contrast"):
            args.contrast = args.contrast if args.contrast is not None else 1.5
        elif f.startswith("blur"):
            args.blur = args.blur if args.blur is not None else 1.0

    # TEXT MODE
    if args.text is not None:
        if args.font != "banner":
            raise SystemExit("Only --font banner is supported right now.")
        art = text_to_banner(args.text)

    # IMAGE MODE
    else:
        if not args.input:
            raise SystemExit("Provide an image path or use --text.")
        if not os.path.exists(args.input):
            raise SystemExit(f"File not found: {args.input}")

        img = Image.open(args.input)

        # filters default: grayscale true for ASCII
        grayscale = True if (args.grayscale or True) else False  # always grayscale by default
        img = resize_keep_aspect(img, width=args.width, scale=args.scale)
        img = apply_filters(
            img,
            grayscale=grayscale,
            invert=args.invert,
            contrast=args.contrast,
            blur=args.blur,
        )
        # ensure grayscale
        img = img.convert("L")
        art = image_to_ascii(img, chars=chars)

        w, h = img.size
        print(f"Procesare imagine: {args.input} ({w}x{h}px)")
        if args.width:
            print(f"Conversie la ASCII (width={args.width})...")
        elif args.scale:
            print(f"Conversie la ASCII (scale={args.scale})...")
        else:
            print("Conversie la ASCII (width=80 default)...")

    # output / preview
    if args.preview or (args.output is None):
        print(art)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(art + "\n")
        print(f"Salvat în {args.output}")


if __name__ == "__main__":
    main()
