# edit-manifest.json 数据约定（v1）

这是跨工具的编辑说明，不是剪映或 CapCut 的草稿格式。只覆盖保留原声完整时长的 B-roll 叠加工作；删句、重排、变速后需要另外记录 source→timeline 映射，不能强塞本简化格式。

所有 `start/end`、`duration_s`、`asset_in/asset_out` 为从零开始的**秒**，可有小数；结束时间为排他边界。帧精度检查允许一帧误差。`source.path` 和资产文件用清单所在目录内的相对路径，禁止绝对路径、`..` 和越界 symlink。制作中引用外部原片时，交付前复制入包或明确让接收者放入相同路径。

## 字段

- `schema_version`: 1
- `project_title`: 本片标题
- `source`: `path`、`duration_s`、`fps`、`width`、`height`、`audio_policy`（`stream_copy` 或 `preserve_timing`）、`burned_captions`（布尔）
- `output`: `width`、`height`、`fps`
- `segments`: 连续、不重叠、首0末=`duration_s`；每项是一个完整构图状态，不是互相重叠的多个素材轨道
  - `id`、`start`、`end`、`trigger_phrase`、`visual_type`、`asset`（资产 ID 或路径；纯人物可为空）、`claim_status`、`sources`（原始来源链接或用户文件出处列表）、`layout`、`presenter_visible`（布尔）、`note`
  - `visual_type`: `presenter` / `real_ui` / `official_source` / `relationship_graph` / `concrete_scene`
  - `claim_status`: `verified_fact` / `official_claim` / `author_analysis` / `unverified` / `not_applicable`
  - `layout`: `presenter_full` / `broll_full_circle` / `split`；兼容旧 `presenter` / `fullscreen`，但本系列优先三种标准模式
  - 可选 `asset_in/asset_out`: 视频资产入出点，正常速度时跨度等于该状态时长；静图省略。额外 `transform` 或动画事件需在 HANDOFF 解释，校验器不验证其画面效果
- `assets`: 每项 `id`、`path`、`type`（`image`/`video`/`vector`）、`source_url`（不适用可空）、`verification`（`verified`/`illustration`/`unverified`）、`status`（`ready`/`missing`/`excluded`）、`editable_source`（相对路径，不适用可空）
  - 可选 `duration_s` 用于检查视频取段边界；`origin`（`official`/`user`/`licensed`/`self_made`/`generated`）有助区分示意与证据
  - `rights_note`、`verified_on`、`product_version`、`supports_claim` 可补充来源与权限；脚本不会替你做事实或版权判断
- 可选 `progress_bar`: `enabled`（布尔）、`mode=whole_video`、`placement=fixed_canvas`、`anchor=top` 或 `bottom`；实际像素/归一化位置、边距和目标平台测试记录放在此对象的扩展字段或交接说明里，不能每段改变位置
- 三种标准模式都需 `presenter_visible=true`。不能把旧 `fullscreen` 写成隐去作者却默认满足此系列要求；该模式需在交接说明解释

## 语义动效扩展（向后兼容）

丰富讲解/动效修订项目使用 `motion_requirement=semantic`；没有动效要求时可省略或为 `not_requested`。`motions` 是事件数组，仍然只是渲染输入/交接说明，不会由校验器自动执行动画。

每条包含：`id`、`segment_id`、`layer`（`broll`/`a_roll`/`progress`/`captions`/`transition`）、`target`（具体元素）、`action`（如 `reveal`/`draw_path`/`focus`/`highlight`）、`trigger_phrase`、全片绝对秒 `start/end`、`duration_s`、`state_from/state_to`（非空文字或对象）、`easing`、`attention_objective`。

事件应位于所属段落时间内，时长等于结束减开始。多个事件可在同段落内顺次或合理重叠，不必新增镜头。需要保持静止的B-roll段落写 `hold_reason` 说明阅读/证据上的理由。`semantic` 模式会提示既无内部B-roll事件也无静止理由的段落；只有人物、字幕、进度条或换页转场不会消除此提示。这不要求固定动画数或覆盖率。

`motion-storyboard.csv` 记录相同规划，加上实际渲染文件、检查时间点和观察结果。校验器只能检查字段和时间，不证明动画在成片中真的运动；实际播放验收按 `semantic-motion.md` 执行。

## 使用方式

复制 `templates/edit-manifest.json`，填真实路径、实测参数与时间码。示例中的概念资产是说明格式，`status=missing` 有意保留，不能当成已有素材。真实项目做好后运行 `--check-files --strict`。

结果：错误返回1；普通模式可带警告通过；strict 模式有任何警告也返回1。错误包含无效时间、引用或越界路径；警告包含缺素材、未核实、未解释的静止B-roll等。`--check-files` 并不解码媒体；媒体类型、真实时长和音画一致另做检查。

原片有烧录字幕且部分圆窗/全人物构图需要重建字幕时，`add_caption_overlay=true`会保留人工检查警告；它不是实际叠字的判定。用 `output.caption_overlay_policy` 说明哪些段落重建、哪些保留原字幕，在交接记录留下检查结果。不要为追求零警告写假 `false`；可交付结构通过并解释已人工审查的警告，不声称strict零警告通过。

提供额外字段不会报错，方便不同工具扩展；不能因此宣称额外字段被验证过。
