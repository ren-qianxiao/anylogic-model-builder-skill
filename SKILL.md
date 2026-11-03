---
name: anylogic-model-builder
description: "Build AnyLogic 8.x models from a curated structural template library. Use when the user asks to 建一个 AnyLogic 模型, 用 AnyLogic 仿真, 把某个流程做成模型, 在现有模型里加 AGV/行人/输送线/吊机, 或 wants a deliverable .alp. Also use when inspecting or debugging an .alp XML file, choosing a reference architecture, or parameterizing an existing model. Delivers by assembling a structural skeleton and filling parameters; does not hand-construct .alp from scratch."
---

# AnyLogic 模型构建器

## 能力边界

**能交付**：结构模板选型、骨架装配、参数填充、结构解析、容量估算。

**不承诺**：任意新结构的零参考构造。`.alp` 是私有 XML 格式，没有 schema 和命令行校验；脱离模板手写，加载失败的概率很高。

所以工作流是：**选参考架构 → 装配骨架 → 参数化 → 打开验证**。

## 工作流

### 1. 需求拆解

提取：对象（行人/托盘/AGV/车辆）、流程（从哪到哪）、资源（人/车/月台）、目标（吞吐/等待/成本）。缺的追问，一次不超过两项。

### 2. 选结构模板

查 `references/templates.md`（12 类场景的模板，含关键块、可提取链条、依赖）和 `references/official-examples.md`（118 个参考模型索引）。按**流程环节**匹配，不按行业名匹配。

参考模型根目录：

```
E:/AnyLogic/AnyLogic 8.9 Professional/plugins/com.anylogic.examples_8.9.8.*/
├── models/        物流、供应链、生产、交通
└── basicmodels/   行人、流程、基础库
```

### 3. 装配骨架

两种方式：

- 整段搬运：`scripts/graft_blocks.py`，从参考模型提取块、连接器、目标线，装配进目标模型
- 新建模型：`scripts/clone_template.py`，以参考模型为底稿生成新模型

装配后只调整 `Id`、`Name`、`PackageName`、坐标，不改块的内部结构。

### 4. 参数化

改参数前读 `references/alp-structure.md`，确认字段位置。原则：

- 优先改 `<Parameter>` 的 `<Value>`，不新增元素
- 改引用时，所有 `PackageName` 同步
- 改块名时，所有 `Connector` 的 `ItemName` 同步
- 行人链的 `PedSource` 必须有 `locationLine`

### 5. 验证

生成后在 AnyLogic 打开确认。这是唯一可靠的验证方式，没有 CLI 替代。失败时对照 `references/pitfalls.md`。

## .alp 结构速查

```
AnyLogicWorkspace
└─ Model
   ├─ ActiveObjectClasses
   │  └─ ActiveObjectClass (Main)
   │     └─ Presentation
   │        └─ Level
   │           ├─ Id/Name/.../LevelVisibility
   │           └─ Presentation          ← 块、线、连接器在这一层
   │              ├─ TargetLine
   │              ├─ EmbeddedObject      ← 库块
   │              └─ Connector
   └─ Experiments
```

关键：`Level` 下面还有一层 `Presentation`。元素放错层级，画布会空白。

库块的识别方式：

```xml
<EmbeddedObject>
  <Name>pedSource</Name>
  <ActiveObjectClass>
    <PackageName>com.anylogic.libraries.pedestrian</PackageName>
    <ClassName>PedSource</ClassName>
  </ActiveObjectClass>
  <Parameters>...</Parameters>
</EmbeddedObject>
```

连接器：

```xml
<Connector>
  <SourceEmbeddedObjectReference> Main / ItemName=pedSource </...>
  <SourceConnectableItemReference> PedSource / ItemName=out </...>
  <TargetEmbeddedObjectReference> Main / ItemName=pedGoTo </...>
  <TargetConnectableItemReference> PedGoTo / ItemName=in </...>
</Connector>
```

## 已知坑

读 `references/pitfalls.md`。最贵的三个：

1. **层级漏一层**：元素必须在 `Level/Presentation` 下。
2. **行人块缺线**：`PedSource.pedEnter` 报 `targetLine 未指定`。
3. **演示上限**：参考模型常有 `maxArrivals=25`、`lastOrderId<11`、`ordersListMaxLength=50`，不改则跑不出规模。

## 脚本

- `scripts/inspect_alp.py`：解析 `.alp` 结构摘要
- `scripts/clone_template.py`：以参考模型为底稿生成新模型
- `scripts/graft_blocks.py`：装配块、连接器、目标线到目标模型

三个脚本都不依赖 AnyLogic 运行。

## 与其他技能的分工

- `anylogic-logistics-advisor`：仓储/供应链的选型、容量估算、建模蓝图
- `wanghan-anylogic-help`：块/API 的官方文档与报错签名
- 本技能：结构装配、参数化、输出 `.alp`
