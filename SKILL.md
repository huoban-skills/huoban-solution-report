---
name: hb-digital-proposal
description: 生成面向客户的《数字化建议报告》：输入需求沟通记录/纪要，产出九章结构的报告 HTML（诊断→目标→方案配图→实施路径→报价→行动清单）＋单页长版 PDF。当用户提到"数字化建议报告""建议报告""数字化方案报告""数字化转型建议"，或跟客户聊完需求要出一份带报价、带系统示意图、拿去向客户/领导汇报的方案报告时，必须使用本 skill。修改已有的数字化建议报告（改内容、换图、重出 PDF）也进入本 skill。不用于：行业科普分析（hb-industry-report）、服务记录（hb-service-note-main）、需求拆解表（hb-solution）。
---

# 数字化建议报告

把一次客户需求沟通转化为可直接发给客户决策层的建议报告：HTML 是源文件，PDF 是交付物。

## 工作流

1. **素材盘点**。从沟通记录抽五要素：行业与业务模式、组织与协作结构、数字化现状、痛点、诉求。缺哪块直接问用户，不猜。
2. **落位**。在当前工作目录建 `{客户简称}/` 文件夹，复制 assets/template.html 为 `{客户简称}数字化建议报告.html`。
   2.5 **选皮肤**。按客户行业气质推荐一套（给建议＋一句理由，不罗列清单），用户点头后执行 `python3 scripts/apply_skin.py 报告.html 皮肤名`；默认藏蓝金（navy-gold）则跳过。七套皮肤及适用行业见 assets/skins/ 各文件头注释。**与 hb-system-mockup 的皮肤同名同气质：报告选定后，配图必须用同名皮肤，报告与图自动同色系。**
3. **成文**。按 references/report-spec.md 逐章填充，方案模块只写文字，不放图也不留占位。写完跑一遍该文末尾的交付前自检。写报价章前必读 references/platform-pricing.md 与 references/service-package.md，数字只从这两处取。成文交付时问用户是否需要配图。
4. **配图（可选，用户确认要才做）**。每个方案模块开一张图需求单（页面类型＋要呈现的字段与数据＋浮层要突出什么），跳 hb-system-mockup 产图；拿到 PNG 后在模块末尾追加 `<div class="fig shot"><img alt="模块标题" src=""></div>`，再执行：
   `python3 scripts/embed_figures.py 报告.html "模块标题=图.png" ...`
   用户不需要配图则跳过本步，直接出 PDF。
5. **出 PDF**。`python3 scripts/make_pdf.py 报告.html`（默认单页长版，适合微信与手机阅读）；用户要打印版时加 `--paged`。两版可并存，打印版文件名加「打印版」后缀。
6. **修改循环**。任何内容修改都落在 HTML 上，改完重出 PDF；图有变动先重嵌再出 PDF。

## 边界

- 报告只呈现结论与方案，不写方案比较、论证过程与"原来是 X"式的修订痕迹。
- 图的绘制不在本 skill：只开图需求单，画图归 hb-system-mockup。
- 系统真正落地搭建（建表、自动化、流程）归 huoban-table / huoban-automation 等执行域 skill。
- 用户只要「帮我整理需求」「拆阶段给客户确认」时走 hb-solution，不进本 skill。
