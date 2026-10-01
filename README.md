# AI 热点视频 Skills

把 AI 热点与观点口播做成观众看得懂、画面有依据的视频。两套 Skill 都保留作者出镜、原声和观点，先理解口播，再设计分镜、匹配素材并验收。

本仓库提供工作方法、参考说明与模板，**不自带剪辑或渲染引擎，也不附带视频素材包**。实际制作取决于 Agent 环境中可用的工具与媒体。

## 选择哪套 Skill

| Skill | 适合的任务 | 画面与交付重点 | 入口 |
| --- | --- | --- | --- |
| `edit-tech-explainer` | 产品走红、功能更新、工具对比与热点解释；参考博主拆解 | 真实素材、解释页与策略页；默认 9:16 上下分屏 | 根目录 [SKILL.md](SKILL.md) · [完整介绍](README-explainer.md) |
| `edit-tech-broll` | 希望按观点组织 B-roll、让关系图随原声展开的口播 | 语义动效；人物全屏、B-roll 全屏＋人物圆窗、上下分屏；固定画布进度条与剪映交接 | [SKILL.md](skills/edit-tech-broll/SKILL.md) · [完整介绍](skills/edit-tech-broll/README.md) |

需要语义动效与三种构图时，显式调用 `edit-tech-broll`；使用原有热点解释流程时，调用 `edit-tech-explainer`。两套可以分别安装，旧版入口与配套文件完整保留。

默认视觉沿用白色或浅灰底、浅色蓝紫渐变、深色标题和清晰的关系模块。用户指定的风格优先。此次整理不改动 Skill 的视觉规范。

## 安装

保留技能目录内部的相对位置，不要只复制 `SKILL.md`。

- **B-roll Skill**：复制完整的 `skills/edit-tech-broll/` 文件夹。
- **Tech Explainer Skill**：新建 `edit-tech-explainer/` 文件夹，将仓库根目录的 `SKILL.md`、`agents/`、`assets/`、`references/` 放入其中。无需把新 B-roll Skill 复制进去。

将上述技能文件夹放入对应工具的目录：

| 工具 | 项目内目录 | 个人目录 | 调用方式 |
| --- | --- | --- | --- |
| Codex | `.agents/skills/<技能名>/` | `~/.agents/skills/<技能名>/` | `$edit-tech-broll` 或 `$edit-tech-explainer` |
| Claude Code | `.claude/skills/<技能名>/` | `~/.claude/skills/<技能名>/` | `/edit-tech-broll` 或 `/edit-tech-explainer` |

也可让能读取本地文件的 Agent 直接读取对应 `SKILL.md`。B-roll 的完整安装与迁移说明见 [INSTALL.md](skills/edit-tech-broll/INSTALL.md)。实际技能发现与调用需在所用工具版本中检查。

## 快速开始

提供口播视频；已有脚本、字幕或参考片时一并提供。说明目标观众、风格，以及本轮需要分镜、样片还是全片。

```text
使用 $edit-tech-broll 处理我的 AI 观点口播。
观众：AI 小白。保留我的出镜、原声、字幕和观点顺序。
沿用浅色蓝紫风格，按语义选择人物全屏、B-roll 全屏＋人物圆窗、上下分屏。
图解中的节点、箭头和重点随原声展开；进度条固定在画布顶部，按整片时间推进。
本轮先交付静态分镜和动效设计，附素材来源与待补缺口；确认后制作代表样片。
```

Claude Code 将首行改为 `/edit-tech-broll`。使用旧流程时改为 `$edit-tech-explainer`，并说明上下分屏、解释页或参考视频拆解要求。更多示例见 [Tech Explainer 完整介绍](README-explainer.md) 和 [B-roll 完整介绍](skills/edit-tech-broll/README.md)。

## 工作流程与依赖

| 阶段 | 交付内容 | 检查重点 |
| --- | --- | --- |
| 理解口播与参考 | 观点、依据、逻辑关系与必要的参考拆解 | 画面需要证明或解释什么 |
| 整理素材 | 素材、来源、授权状态与缺口 | 真实证据和示意图是否区分清楚 |
| 静态分镜 | 代表页、分镜与手机比例预览 | 构图、信息量与阅读时间 |
| 代表样片 | 约 10–15 秒片段；按任务检查内部动效 | 原声触发、音画配合、阅读与裁切 |
| 全片与交接 | 实际制作的成片、素材、字幕与编辑清单 | 播放、同步、文件完整性及交接方式 |

可以只完成一个阶段。参考视频分析需要视频读取、音轨检查与转写能力；录屏、作图、转写及视频合成需要实际可用的外部工具。缺少工具或素材时，应说明缺口并完成可执行部分。

Hypit 是原流程的方法参考与可选工具，当前未集成 Hypit Runtime。两套 Skill 均不替代实际剪辑软件。

## 剪映交接与验证范围

执行视频任务时，通用交付包应包含实际媒体、SRT、CSV/JSON 时间码编辑说明，需要在剪映中人工导入和摆放。**通用包不是已验证的剪映原生工程，自定义 JSON 也不是剪映或 CapCut 草稿格式。** 原生工程须在记录的操作系统、软件和适配器版本上完成开档、重连、播放、导出和重开验证后才能这样命名。

校验脚本使用 Python 3.9+ 标准库，无第三方 Python 依赖；转写、录屏、图像制作和视频合成依赖实际可用的外部工具。脚本通过只证明清单结构、路径和时间约定，不证明素材授权、事实准确、动效效果或剪映兼容。

```sh
cd skills/edit-tech-broll
python3 scripts/test_validator.py
python3 scripts/validate_manifest.py /path/to/project/edit-manifest.json --check-files --strict
```

示例模板故意保留缺素材状态，严格检查应失败；不要删除检查或伪造素材状态。包内参考拆解和样片验证是作者留下的历史记录，本次 GitHub 存档未重新观看或验证相关视频。目标发布平台的手机界面遮挡、软件实际安装与剪映原生工程兼容仍需另行实测。

新版本说明：[README](skills/edit-tech-broll/README.md) · [语义动效](skills/edit-tech-broll/references/semantic-motion.md) · [剪映交接](skills/edit-tech-broll/references/jianying-handoff.md) · [包验证记录](skills/edit-tech-broll/VALIDATION.md)。
