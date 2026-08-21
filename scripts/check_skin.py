#!/usr/bin/env python3
"""校验皮肤 CSS 是否满足审美底线与可读性（WCAG）。

用法：python3 scripts/check_skin.py assets/skins/<名>.css
全部通过输出 PASS；任一不过输出 FAIL 与修复方向，退出码 1。
"""
import re
import sys
from pathlib import Path


def hexes(v):
    """取值里的全部 hex（渐变含多个 stop，逐个都要过检）。"""
    return re.findall(r"#[0-9a-fA-F]{6}", v)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def lum(h):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse(css):
    blocks = re.findall(r'(:root(?:\[data-theme="dark"\])?)\s*\{([^}]*)\}', css)
    out = {}
    for sel, body in blocks:
        mode = "dark" if "dark" in sel else "light"
        out[mode] = dict(re.findall(r"--([\w-]+):\s*([^;]+);", body))
    return out


def check(path):
    tokens = parse(Path(path).read_text(encoding="utf-8"))
    errs = []
    lt = tokens.get("light", {})

    # 1. 底色干净：每个渐变 stop 都要近白、低饱和、不偏黄
    for h in hexes(lt.get("paper", "")):
        r, g, b = rgb(h)
        if min(r, g, b) < 236:
            errs.append(f"paper {h} 不够亮（有通道 < #EC）：底色发闷发浊，整体提亮")
        if max(r, g, b) - min(r, g, b) > 12:
            errs.append(f"paper {h} 饱和度过高（通道差 > 12）：向白靠拢")
        if r - b > 10:
            errs.append(f"paper {h} 偏黄（R-B > 10）：属米黄/大地浊底，降暖")

    # 2. 正文近黑但非纯黑，对比达标
    ink = hexes(lt.get("ink", ""))[0] if hexes(lt.get("ink", "")) else None
    surface = hexes(lt.get("surface", ""))[0] if hexes(lt.get("surface", "")) else "#FFFFFF"
    if ink:
        if ink.upper() == "#000000":
            errs.append("ink 是纯黑：改用带色相倾向的近黑（如藏青黑/炭黑）")
        if contrast(ink, surface) < 7:
            errs.append(f"ink/surface 对比 {contrast(ink, surface):.1f} < 7:1：正文加深")

    # 3. 强调色可做标题字色（≥4.5），辅助强调可做小标签（≥3）
    for key, floor, fix in (("accent", 4.5, "accent 加深"), ("gold", 3.0, "gold 加深")):
        hs = hexes(lt.get(key, ""))
        if hs and contrast(hs[0], surface) < floor:
            errs.append(f"{key}/surface 对比 {contrast(hs[0], surface):.1f} < {floor}:1：{fix}")

    # 4. dark 块存在且正文可读
    dk = tokens.get("dark", {})
    if not dk:
        errs.append("缺 dark 块：light/dark 两个 :root 都必须写全")
    else:
        dink = hexes(dk.get("ink", ""))
        dsurf = hexes(dk.get("surface", ""))
        if dink and dsurf and contrast(dink[0], dsurf[0]) < 7:
            errs.append(f"dark ink/surface 对比 {contrast(dink[0], dsurf[0]):.1f} < 7:1")

    return errs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    errs = check(sys.argv[1])
    if errs:
        print("FAIL", sys.argv[1])
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("PASS", sys.argv[1])
