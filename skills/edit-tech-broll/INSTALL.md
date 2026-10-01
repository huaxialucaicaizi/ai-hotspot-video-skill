# 安装与使用

这是一份自包含的工作方法 skill：`SKILL.md`、参考说明、分镜模板和本地校验脚本。它不会自动安装剪映、操作你的电脑或把 JSON 变成剪映草稿。

## Codex

项目内：把整个 `edit-tech-broll` 文件夹复制到项目的 `.agents/skills/`，最终路径为 `.agents/skills/edit-tech-broll/SKILL.md`。

个人全局：复制到 `~/.agents/skills/edit-tech-broll/`。目录规则按 2026-09-30 官方文档核对；使用较旧版本时以该版本实际发现规则为准。若未出现，重启会话并检查文件夹层级，不要只复制入口文件。

调用示例：

> 使用 $edit-tech-broll，把项目里的口播视频按“真实证据、关系解释、作者回场”重剪。保持我的原声和浅色蓝紫风格。先读完整口播，给出语义分镜；我已确认风格并授权制作全片。交付成片、素材、SRT、时间码编辑清单。没有在我的剪映版本开档验证时，不要声称已生成可导入草稿。

## Claude Code

项目内：复制到 `.claude/skills/edit-tech-broll/`。

个人全局：复制到 `~/.claude/skills/edit-tech-broll/`。

在 Claude Code 中输入 `/edit-tech-broll`，并附上视频位置、风格要求和交付阶段。也可自然语言请求匹配工作。个人本地目录不等于云端/Cowork 已启用；那些环境需按 Claude 当时的账户或项目技能设置另行配置。

## 迁移时保留什么

1. 保留整个目录和相对链接；可仅安装这一份，不需要另装原系列 skill
2. 保留现有旧 skill，避免无意覆盖。此包名为 `edit-tech-broll`，原系列是 `edit-tech-explainer`。同一任务优先显式调用本包，减少路由歧义
3. 为每支视频新建项目目录，把媒体和中间文件放在那里，不写回 skill 目录
4. 执行校验可用 Python 3.9 或更新版本，无第三方 Python 依赖。视频探测/合成可用已安装的 FFmpeg/ffprobe 或实际剪辑工具，先检查可用性
5. 缺媒体、ASR、图像生成、浏览器或剪映本地能力时，skill 仍可指导规划；它本身不提供这些运行能力

## 校验命令

在此 skill 目录运行：

```sh
python3 scripts/validate_manifest.py /path/to/project/edit-manifest.json --check-files --strict
python3 scripts/test_validator.py
```

`--check-files` 检查项目内文件存在，`--strict` 将待核实/缺失素材等警告作为未通过。没有这些参数的结构通过不代表素材已经准备好。具体字段见 `references/manifest-format.md`。

## 当前资料

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)，核对 `.agents/skills` 及本地技能发现规则
- [Anthropic：Claude Code skills](https://code.claude.com/docs/en/skills)，核对 `.claude/skills` 与调用方式
- [原 AI 热点口播系列](https://github.com/huaxialucaicaizi/ai-hotspot-video-skill)，继承语义论证、浅色科技风和先分镜后制作的方向；本包新增交接约定与检查脚本

本次未修改远程仓库，也未代你安装。复制安装不包含任何账户授权或剪映兼容保证。
