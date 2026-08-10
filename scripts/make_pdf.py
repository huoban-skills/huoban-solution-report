#!/usr/bin/env python3
"""报告 HTML 出 PDF。

默认出单页长版（无分页留白，适合微信/手机阅读）：页高按内容实测二分收紧。
--paged 出 A4 分页版（适合打印），走报告自带的 @media print 分页规则。

用法: python3 make_pdf.py 报告.html [--paged] [-o 输出.pdf]
"""
import re, subprocess, tempfile, pathlib, argparse, sys

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PAGE_W = 794   # A4 宽 210mm @ 96dpi
A4_H = 1123    # A4 高 297mm @ 96dpi


def page_count(pdf: pathlib.Path) -> int:
    return len(re.findall(rb'/Type\s*/Page[^s]', pdf.read_bytes()))


def print_pdf(src: pathlib.Path, out: pathlib.Path):
    subprocess.run(
        [CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
         f'--print-to-pdf={out}', src.resolve().as_uri()],
        check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report')
    ap.add_argument('--paged', action='store_true', help='出 A4 分页版')
    ap.add_argument('-o', '--out')
    a = ap.parse_args()
    src = pathlib.Path(a.report)
    out = pathlib.Path(a.out) if a.out else src.with_suffix('.pdf')

    if a.paged:
        print_pdf(src, out)
        print(f'{out.name}: {page_count(out)} 页（A4 分页版）')
        return

    # 单页长版：报告 HTML 没有 </body> 结束标签，覆盖样式直接拼在文件末尾
    base = src.read_text(encoding='utf-8')
    tmp = pathlib.Path(tempfile.mkdtemp()) / 'long.html'

    def build(h: int):
        tmp.write_text(base + f'''
<style>@media print{{
@page{{size:{PAGE_W}px {h}px;margin:0}}
.feat{{break-before:auto;break-inside:auto}}
h2,h3,.feat .fn{{break-after:auto}}
.pains .pn,.figph,.phase .p,table,.value .v,.note,.feat .fig.shot{{break-inside:auto}}
}}</style>
''', encoding='utf-8')

    # 先按分页印一次取页数做上界（分页版含强制分页留白，必为连续排版高度的上界）
    print_pdf(src, out)
    hi = page_count(out) * A4_H + 200
    lo = 512
    while hi - lo > 24:
        mid = (lo + hi) // 2
        build(mid)
        print_pdf(tmp, out)
        if page_count(out) == 1:
            hi = mid
        else:
            lo = mid
    build(hi)
    print_pdf(tmp, out)
    if page_count(out) != 1:
        sys.exit('!! 收敛失败，请检查报告是否含超长不可分元素')
    print(f'{out.name}: 单页长版，页高 {hi}px')


if __name__ == '__main__':
    main()
