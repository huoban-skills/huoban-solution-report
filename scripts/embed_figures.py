#!/usr/bin/env python3
"""按 alt 名把 PNG 嵌入报告 HTML 的 data URI。

用法: python3 embed_figures.py 报告.html "图名1=path1.png" "图名2=path2.png" ...
图名须与报告中 <img alt="..."> 完全一致（即模块 h3 标题）。
"""
import sys, re, base64, pathlib


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    report = pathlib.Path(sys.argv[1])
    s = report.read_text(encoding='utf-8')
    for pair in sys.argv[2:]:
        alt, _, path = pair.partition('=')
        b64 = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
        pat = re.compile(r'(<img alt="' + re.escape(alt) + r'" src=")[^"]*(")')
        s, n = pat.subn(lambda m: m.group(1) + 'data:image/png;base64,' + b64 + m.group(2), s)
        print(f'{alt}: {"已嵌入" if n else "!! 未找到对应 <img alt>，检查图名是否与 h3 一致"}')
    report.write_text(s, encoding='utf-8')
    left = s.count('class="figph"')
    if left:
        print(f'提示: 还有 {left} 个 figph 占位待补图')


if __name__ == '__main__':
    main()
