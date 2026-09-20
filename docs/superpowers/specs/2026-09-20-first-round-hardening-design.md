# PPT Page Image 第一轮改造设计

## 目标

第一轮改造解决四个问题：制作过程与最终交付混放、三份规划文件重复且可能漂移、项目状态门禁名不副实、学习规则重复注入。改造后，最终目录只包含最终成品和正式交付材料；页面调整稿、候选页、旧页、失败页、拼图、OCR、回渲、检查记录和状态文件全部属于过程产物，不得进入最终目录。

## 目录模型

制作工作区和最终交付目录必须是两个不同目录：

```text
<base>/.ppt-page-image-work/<project-id>/
|-- project-state.json
|-- planning/
|   |-- PPT内容大纲.txt
|   |-- 风格提示词.txt
|   `-- 字体说明.txt
|-- fonts/
|-- slides/                  当前通过审核的页面图，仍属于过程产物
|-- candidates/              当前候选页
|-- montages/
|-- ocr/
|-- reports/
|-- render-back/
`-- history/                 必要的失败与纠正记录

<base>/<deck-name>/
|-- <deck-name>.pdf
|-- PPT内容大纲.txt
|-- 风格提示词.txt
|-- 字体说明.txt
|-- fonts/
`-- images/                  仅限获准交付的来源或修复素材，可选
```

最终目录不包含 `.work`、`slides`、`candidates`、`history`、OCR、拼图、回渲、状态文件或带有旧版/修改版/候选版含义的文件。过程工作区可保留以支持后续修改，但必须位于最终目录之外。用户要求清理过程工作区时再删除，不把“保持最终目录干净”解释成自动删除可恢复材料。

所有页面修改均在工作区完成。通过页面审核时，只替换工作区 `slides/` 中的当前页；旧候选和失败候选进入 `history/` 或删除。最终 PDF 只从当前通过审核的 `slides/` 生成。最终目录通过暂存目录原子提升，避免半成品混入既有最终目录。

## 单一规划数据源

`.ppt-page-image-work/<project-id>/project-state.json` 是唯一可编辑的规划数据源。三份中文规划文件由脚本确定性生成，不再人工分别维护：

```powershell
python scripts/generate_planning_files.py --state <workspace>/project-state.json --out-dir <workspace>/planning
```

生成器输出：

- `PPT内容大纲.txt`：项目元信息、页面顺序、锁定文案、教学目标、页面家族和内容依据；
- `风格提示词.txt`：风格指纹、页面家族规范、全局提示词和逐页提示词；
- `字体说明.txt`：字体角色、文件映射、许可状态、替代字体和逐页角色使用。

`validate_project.py` 重新生成内存中的期望文本，并与 `planning/` 内文件逐字比较。任何人工编辑或状态更新后未重新生成都会失败，从机制上消除三份文件与状态之间的漂移。

## 项目状态 Schema v2

新项目使用 `schema_version: 2`。核心结构包括：

- `deck`：名称、页数、受众、场景、语言、来源权威和范围；
- `style`：选定风格、用户反馈、保留特征、拒绝特征、风格指纹、全局提示词和负面约束；
- `fonts`：角色、显示名、字重、来源路径、打包文件、替代字体、可视特征和许可状态；
- `families`：母页、成员页、不变量和组件规范；
- `pages`：页码、类型、目标、标题、锁定文案、事实来源、内容依据、设计理由、元素预算、阅读顺序、分区、字体角色、负面约束、完整提示词、QA 状态和缺陷历史；
- `reviews`：试页、页面家族、整套和 PDF 回渲检查；
- `delivery`：最终名称和允许交付的可选素材。

第一轮保留 schema v1 的只读兼容校验：旧项目仍可检查原有结构，但不能使用 v2 的严格状态门禁。校验结果必须明确显示 `legacy: true`，不能假装已通过新版完整门禁。

## 状态门禁

`validate_project.py` 增加 `--gate`：

- `planning`：要求状态至少为 `PLANNING_READY`，检查规划文件、字体、页面、家族和提示词；
- `pilot`：要求 `PILOT_APPROVED`，并检查用户指定试页或高风险代表页已有通过记录；
- `production`：要求 `FULL_PRODUCTION` 或更后状态，所有需制作页面具有当前图像记录；
- `delivery`：要求 `DELIVERY_READY`，所有页面、页面家族、整套和回渲检查均通过。

状态只能沿既定顺序推进。内容修改回退到 `PLANNING_READY`；视觉修改回退到受影响的最早制作阶段。校验器检查状态所需证据，不提供一个可随意填写状态字符串就绕过门禁的入口。

页面提示词必须包含全部非空锁定文案以及页面声明的字体角色。重复页面家族必须有完整组件规范。页面 QA、缺陷历史、家族检查和整套检查的状态值必须来自固定枚举。

## 最终提升与清洁交付

新增 `promote_delivery.py`：

```powershell
python scripts/promote_delivery.py \
  --state <workspace>/project-state.json \
  --workspace <workspace> \
  --pdf <workspace>/reports/<deck-name>.candidate.pdf \
  --delivery-dir <base>/<deck-name> \
  --render-report <workspace>/render-back/render-back-report.json
```

提升过程：

1. 运行 `delivery` 状态门禁；
2. 验证候选 PDF 与回渲报告哈希一致；
3. 在最终目录同级创建临时暂存目录；
4. 复制 PDF、生成后的三份规划文件、获准字体和获准素材；
5. 对暂存目录运行 `validate_delivery.py`；
6. 仅在全部通过后替换最终目录中的受管交付内容；
7. 不复制任何页面过程图、候选页、历史页、拼图、OCR、状态或报告。

如果目标目录含有不属于本技能管理的文件，提升脚本拒绝覆盖并报告文件名。第一轮不自动删除用户已有文件。

## 学习规则整理

Skill 仓库内的 `references/learned-rules.json` 改为只读历史和核心规则来源。已经写入 `SKILL.md` 或参考文档的规则标记为 `promoted`，`list-active` 不再把它们重复注入每个项目。

新的用户级可变规则存放在：

```text
%CODEX_HOME%/state/ppt-page-image/learned-rules.json
```

未设置 `CODEX_HOME` 时使用 `%USERPROFILE%/.codex/state/ppt-page-image/learned-rules.json`。`record_correction.py` 默认读写用户级存储，仍允许通过 `--store` 显式指定测试或迁移文件。规则状态固定为 `active`、`superseded`、`promoted`；历史不删除。第一轮合并或提升现有重复规则，不改变已经固化到核心文档中的用户偏好。

## 接口与兼容性

- 文档中的所有 Python 命令使用 `python -X utf8`，避免中文 Windows 默认编码导致验证失败。
- `validate_project.py` 的 `--project-dir` 保留为 schema v1 兼容参数；schema v2 使用 `--workspace` 与 `--gate`。
- `validate_delivery.py` 继续保持严格白名单，过程产物一律失败。
- 新增脚本和状态字段先写失败测试，再实现。
- 测试统一从顶层 `tests/` 发现；现有 `scripts/tests/` 测试迁移后不再保留两套入口。

## 测试与验收

第一轮必须覆盖：

1. schema v2 能生成三份稳定、可重复的规划文件；
2. 任一规划文件被人工修改后，规划门禁失败；
3. 锁定文案为空、字体角色缺失、提示词遗漏角色或文案时失败；
4. 不满足状态或缺少对应审查记录时，各门禁失败；
5. schema v1 返回明确 legacy 结果；
6. `promote_delivery.py` 只复制最终成品，不复制任何过程产物；
7. 目标目录存在非受管文件时拒绝覆盖；
8. `promoted` 和 `superseded` 规则不会出现在活动规则列表；
9. 默认规则存储位于用户状态目录而不是 Skill 仓库；
10. 现有 PDF 打包、回渲、字体和交付校验测试继续通过。

完成标准是：新建一个最小 v2 项目，从状态生成规划文件、通过规划门禁、构造通过状态、提升最终交付，并证明最终目录中不存在任何修改页、候选页、旧页、拼图、OCR、回渲、状态或报告。
