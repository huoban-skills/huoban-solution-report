# 自由配色：现场生成皮肤规范

固定皮肤不合适时（客户有品牌色、用户点名要某种颜色），按本规范现场生成一套新皮肤。方法论取自 anthropics/skills theme-factory、claude-code frontend-design、color-palette-skill 等成熟 skill：先出计划 → 自审 → 落文件 → 脚本校验 → 渲染给用户确认。

## 第一步：配色计划（先想后写）

写码前先给出一段计划，包含：

- **4-6 个带名字的 hex**：主强调（accent）、辅助强调（gold）、底色（paper）、正文近黑（ink），外加一句话说明每个颜色为什么属于这个客户（行业气质、品牌色渊源）。
- **一句自审**：「如果换一个行业的客户，我还会给出这套配色吗？」会 → 这是 AI 默认答案，重来。特别警惕这些烂大街套路：白底紫蓝渐变、橙配青、全员高饱和。
- 大胆只花在一处：accent 承载个性，其余全部收敛。

计划给用户过目点头后再落文件。

## 第二步：落文件（示例即规范）

照现有皮肤文件的结构写 `skins/{kebab-case 名}.css`：头注释（气质一句话＋适用行业＋同名同气质提示）、light 与 dark 两个 `:root` 块、12 个变量一个不少（变量清单与职责直接抄 navy-gold.css）。渐变底参考 dawn-blue.css 的写法（`--paper` 放 linear-gradient）。

从 accent 推其余变量的经验公式：

| 变量 | 推法 |
|------|------|
| paper | 近白，向 accent 色相偏 2%-4%；或极浅渐变 |
| ink / ink-soft / muted | accent 色相方向的近黑，亮度约 15% / 32% / 52% 三档 |
| accent-soft / gold-soft | 对应主色掺白至 ~92% 亮度 |
| gold | accent 的邻近或互补方向低饱和深色（蓝配暖金、红配金棕、绿配暖金） |
| line / warn-bg / warn-edge | paper 加深一档 / gold-soft 同系 / gold 同系 |

dark 块与 light 块一一对应：深底（accent 色相，亮度 ~8%-10%）、浅字、强调色提亮到深底可读。

## 第三步：脚本校验（不许口算）

```bash
python3 scripts/check_skin.py assets/skins/{名}.css
```

FAIL 就按提示修（底不够白 → 提亮；对比不足 → 加深前景），改到 PASS 为止。脚本管住的是硬底线：底色近白不发黄不发浊、正文非纯黑且对比 ≥7:1、accent ≥4.5:1、gold ≥3:1、dark 块齐全可读。

## 第四步：渲染确认

用 apply_skin.py 应用到报告，整页截图给用户看，用户点头才算定稿。看图时自查：底不脏、强调色不刺、诊断卡顶边和 kicker 的 gold 不抢戏。

## 破功条件（出现任何一条即失败，不用等用户说）

- 底色落入米黄/灰米/大地/莫兰迪浊色域（check_skin.py 会拦大部分，肉眼再兜底：底色铺满一屏像旧纸/水泥/燕麦就是脏）
- 强调色荧光、霓虹
- 正文纯黑 #000
- light/dark 任一块缺变量导致 apply_skin.py 报警
