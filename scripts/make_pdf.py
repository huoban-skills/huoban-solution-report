#!/usr/bin/env python3
"""报告 HTML 出 PDF。

默认出单页长版（无分页留白，适合微信/手机阅读）：页高按内容实测二分收紧。
--paged 出 A4 分页版（适合打印），走报告自带的 @media print 分页规则。

用法: python3 make_pdf.py 报告.html [--paged] [-o 输出.pdf]
"""
import re, subprocess, tempfile, pathlib, argparse, sys, os, shutil


def _bootstrap_bundled_chrome():
    """Linux 下从 skill 内置分卷解压 chrome-headless-shell 到 ~，成功返回二进制路径。
    分卷随 huoban-image-design skill 分发（assets/chrome/chs_vol_*），零下载。"""
    if not sys.platform.startswith('linux'):
        return None
    import zipfile
    here = pathlib.Path(__file__).resolve()
    vol_dirs = [here.parents[1] / 'assets' / 'chrome',
                here.parents[2] / 'huoban-image-design' / 'assets' / 'chrome']
    dest = pathlib.Path(os.path.expanduser('~/chrome-headless-shell-linux64'))
    binp = dest / 'chrome-headless-shell'
    for d in vol_dirs:
        vols = sorted(d.glob('chs_vol_*'))
        if not vols:
            continue
        tmpzip = pathlib.Path(tempfile.mkdtemp()) / 'chs.zip'
        with open(tmpzip, 'wb') as w:
            for v in vols:
                with open(v, 'rb') as r:
                    shutil.copyfileobj(r, w)
        with zipfile.ZipFile(tmpzip) as z:
            z.extractall(dest.parent)
        tmpzip.unlink()
        for root, _, files in os.walk(dest):
            for f in files:
                os.chmod(os.path.join(root, f), 0o755)
        if binp.exists():
            return str(binp)
    return None


def find_chrome():
    """按顺序找可用 Chrome；都没有时自动解压 skill 内置分卷（见 references/chrome-env.md）。"""
    cands = [
        os.environ.get('CHROME_BIN'),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        'chrome-headless-shell-linux64/chrome-headless-shell',
        'work/chrome-headless-shell-linux64/chrome-headless-shell',
        os.path.expanduser('~/chrome-headless-shell-linux64/chrome-headless-shell'),
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    for name in ('chrome-headless-shell', 'google-chrome', 'chromium', 'chromium-browser'):
        p = shutil.which(name)
        if p:
            return p
    c = _bootstrap_bundled_chrome()
    if c:
        return c
    sys.exit('!! 找不到 Chrome，且未找到 skill 内置分卷。'
             '请确认 huoban-image-design/assets/chrome/chs_vol_* 随 skill 一起分发，'
             '或按 references/chrome-env.md 的备用方案处理，或设 CHROME_BIN 环境变量。')


CHROME = find_chrome()
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
