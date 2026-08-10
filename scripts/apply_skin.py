#!/usr/bin/env python3
"""给报告 HTML 换皮肤：用 assets/skins/<名>.css 的 token 值替换报告里的四个 :root 块。

用法：python3 scripts/apply_skin.py 报告.html navy-gold
可反复执行（换皮肤、换回默认都行）。皮肤清单见 assets/skins/，与 hb-system-mockup 同名同气质。
"""
import re
import sys
from pathlib import Path

SKINS = Path(__file__).resolve().parent.parent / "assets" / "skins"


def parse_skin(name):
    css = (SKINS / f"{name}.css").read_text(encoding="utf-8")
    blocks = re.findall(r'(:root(?:\[data-theme="dark"\])?)\s*\{([^}]*)\}', css)
    out = {}
    for sel, body in blocks:
        mode = "dark" if "dark" in sel else "light"
        out[mode] = dict(re.findall(r"--([\w-]+):\s*([^;]+);", body))
    assert "light" in out and "dark" in out, f"{name}.css 需同时含亮/暗两个 :root 块"
    return out


def apply(html_path, skin_name):
    tokens = parse_skin(skin_name)
    s = Path(html_path).read_text(encoding="utf-8")
    n = 0

    def repl(m):
        nonlocal n
        sel, body = m.group(1), m.group(2)
        # 判明暗：data-theme="dark" 或落在 prefers-color-scheme: dark 的 @media 里
        before = s[max(0, m.start() - 160):m.start()]
        dark = 'data-theme="dark"' in sel or "prefers-color-scheme: dark" in before
        mode = "dark" if dark else "light"
        indent = "  "
        new_body = "\n" + "".join(
            f"{indent}--{k}: {v};\n" for k, v in tokens[mode].items()
        )
        n += 1
        return sel + " {" + new_body + "}"

    s2 = re.sub(r'(:root(?:\[data-theme="(?:dark|light)"\])?)\s*\{([^}]*)\}', repl, s)
    Path(html_path).write_text(s2, encoding="utf-8")
    print(f"已应用皮肤 {skin_name}：替换 {n} 个 :root 块")
    if n < 2:
        print("警告：替换块数异常，检查报告文件是否为本 skill 模板产出")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        avail = ", ".join(p.stem for p in sorted(SKINS.glob("*.css")))
        print(__doc__)
        print("可用皮肤：", avail)
        sys.exit(2)
    apply(sys.argv[1], sys.argv[2])
