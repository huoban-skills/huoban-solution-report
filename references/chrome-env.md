# Chrome 渲染环境（内置分卷，零下载）

PDF 渲染用的 chrome-headless-shell（Chrome for Testing 152.0.7977.54，Linux x64）以分卷形式
内置在兄弟 skill `huoban-image-design/assets/chrome/`（`chs_vol_aa`＋`chs_vol_ab`，
单文件均小于 100MB）。两个 skill 一起分发时，渲染环境随文件走，不依赖资源库，也不需要下载。

## 自动引导（默认，无需人工）

`scripts/make_pdf.py` 按以下顺序自动找 Chrome，全部落空且在 Linux 上时，
自动把分卷合并→解压到 `~/chrome-headless-shell-linux64/`→chmod，然后直接可用：

1. 环境变量 `CHROME_BIN`
2. macOS 本机 Chrome：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
3. 已解压的 chrome-headless-shell：`./chrome-headless-shell-linux64/`、`./work/…`、`~/chrome-headless-shell-linux64/`
4. PATH 里的 `chrome-headless-shell` / `google-chrome` / `chromium` / `chromium-browser`
5. **内置分卷自动解压**（仅 Linux；先找本 skill `assets/chrome/`，再找兄弟 skill `huoban-image-design/assets/chrome/`）

手动引导（不走脚本时）等价操作：

```bash
cat ../huoban-image-design/assets/chrome/chs_vol_aa ../huoban-image-design/assets/chrome/chs_vol_ab > /tmp/chs.zip
unzip -q -o /tmp/chs.zip -d ~
chmod +x ~/chrome-headless-shell-linux64/chrome-headless-shell
~/chrome-headless-shell-linux64/chrome-headless-shell --version
# 应输出：Google Chrome for Testing 152.0.7977.54
```

## 注意

- 运行时若报 dbus 相关 ERROR 属正常（无头环境无 dbus），不影响渲染结果。
- 分卷完整性校验：`cat chs_vol_aa chs_vol_ab | shasum -a 256` 应为
  `11cedb5568cd374a76eb738e40bd434cd0c9956820fb406b8bd9edca53428d3e`。
- 若 huoban-image-design 未随行且需要单独分发本 skill：把两个分卷复制到本 skill `assets/chrome/` 即可，脚本会优先找到。
- 分卷缺失时的备用直下地址：
  https://storage.googleapis.com/chrome-for-testing-public/152.0.7977.54/linux64/chrome-headless-shell-linux64.zip
