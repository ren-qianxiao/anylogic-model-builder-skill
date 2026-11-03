---
name: anylogic-model-builder
description: "Build AnyLogic 8.x models by cloning and adapting official examples instead of handwriting .alp XML. Use when the user asks to 建一个 AnyLogic 模型, 用 AnyLogic 仿真, 把某个流程做成模型, 在现有模型里加 AGV/行人/输送线, 或 wants a deliverable .alp. Also use when inspecting or debugging an .alp XML file, choosing which built-in example to copy, or adapting an existing model's parameters. Critical boundary: this skill clones verified templates; it does NOT hand-construct .alp from scratch — that has been proven to produce files AnyLogic opens blank."
---

# AnyLogic 模型构建器

## 先读这条：能力边界

**能做**：复制官方示例骨架、改参数/名字/引用、解析 `.alp` 结构、选案例、算容量。

**不能做**：从零手写一个可加载的 `.alp`。实测两次都导致 AnyLogic 打开空白。原因是 `.alp` 有私有结构（嵌套层级、泛型 ID、连接器引用），没有 schema、没有命令行校验，手写无法保证。

所以工作流永远是：**找现成模板 → 复制 → 最小改动**，不是生成。

## 工作流

### 1. 需求拆解

从用户描述里提取：对象（行人/托盘/AGV/车辆）、流程（从哪到哪）、资源（人/车/月台）、目标（吞吐/等待/成本）。缺的追问，一次不超过两项。

### 2. 选官方示例

查 `references/official-examples.md`（118 个案例的索引，含块数量、主块、库、3D 数）。按**主块**匹配，不按行业名匹配。

示例安装路径：

```
E:/AnyLogic/AnyLogic 8.9 Professional/plugins/com.anylogic.examples_8.9.8.*/models/<案例名>/<案例名>.alp
```

基础模型（行人、流程等）在 `basicmodels/<案例名>/` 下。

### 3. 复制骨架

用 `scripts/clone_template.py`：

```bash
python -I scripts/clone_template.py \
  --src "E:/AnyLogic/.../models/Supply Chain/Supply Chain.alp" \
  --dst "C:/Users/<user>/Models/MyModel/MyModel.alp" \
  --name "MyModel"
```

它只改模型名和输出路径，不动内部结构。这样生成的文件一定能加载。

### 4. 改参数

改参数前先读 `references/alp-structure.md`，确认要改的字段在哪一层。原则：

- 优先改 `<Parameter>` 的 `<Value>`，不新增元素
- 改引用时，所有 `PackageName` 同步改
- 改块名时，所有 `Connector` 的 `ItemName` 同步改
- 行人库的 `PedSource` 必须有 `locationLine`；`PedGoTo` 的 `locationLine` 指向目标线

### 5. 验证

生成后让用户在 AnyLogic 打开。这是唯一可靠的验证方式，没有 CLI 替代。打开失败时读 `references/pitfalls.md` 对照。

## .alp 结构速查

```
AnyLogicWorkspace
└─ Model
   ├─ ActiveObjectClasses
   │  └─ ActiveObjectClass (Main)
   │     └─ Presentation
   │        └─ Level
   │           ├─ Id/Name/.../LevelVisibility
   │           └─ Presentation          ← 块、线、连接器都在这一层里
   │              ├─ TargetLine
   │              ├─ EmbeddedObject      ← 库块（PedSource 等）
   │              └─ Connector
   └─ Experiments
```

关键：`Level` 下面还有一层 `Presentation`。把元素直接放 `Level` 下，AnyLogic 打开是空白。

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

1. **层级漏一层**：元素必须放在 `Level/Presentation` 下，不是 `Level` 下。
2. **行人块缺线**：`PedSource.pedEnter` 报 `targetLine 未指定`，因为 `locationLine` 为空。
3. **演示上限**：官方示例常有 `maxArrivals=25`、`lastOrderId<11`、`ordersListMaxLength=50`，不改则模型跑不出规模。

## 脚本

- `scripts/inspect_alp.py`：输出 `.alp` 的结构摘要（智能体、块、连接、3D、实验），用于选型和比对。
- `scripts/clone_template.py`：复制官方示例并改模型名，输出新 `.alp`。

两个脚本都不依赖 AnyLogic 运行。

## 与 other skills 的分工

- `anylogic-logistics-advisor`：仓储/供应链场景的选型、容量估算、建模蓝图。本技能负责“怎么把选中的案例变成文件”。
- `wanghan-anylogic-help`：块/API 的官方文档与报错签名。本技能不重复解释单个块。
