# AnyLogic Model Builder

为 AnyLogic 8.x 提供**结构模板库**和**模型装配工具**：按需求选择参考架构，装配骨架，填充参数，输出可交付的 `.alp`。

## 核心能力

| 能力 | 说明 |
|---|---|
| 模板选型 | 12 类场景的参考架构，覆盖行人、物料搬运、输送、仓储、供应链、铁路、流体 |
| 骨架装配 | 从参考模型提取块、连接器、目标线，装配进目标模型 |
| 参数化 | 调整 Id、名称、包名、坐标、块参数 |
| 结构解析 | 输出任意 `.alp` 的智能体、块、连接、3D、实验摘要 |
| 容量估算 | 配合 `anylogic-logistics-advisor` 做资源规模测算 |

## 模板库

`references/templates.md` 收录 12 类模板：

- 行人行走、行人统计
- 配送中心收发货、输送线、多层拣选
- 自由空间 AGV、多任务 AGV、共享机器人
- 铁路到发编组
- 三级供应链
- 连续流管网、生产物流

每个模板记录参考模型路径、关键块、可提取链条和库依赖。完整模型索引见 `references/official-examples.md`（118 个参考模型）。

## 工作流

```
需求拆解 → 选结构模板 → 装配骨架 → 参数化 → 打开验证
```

## 脚本

```bash
# 查看模型结构
python scripts/inspect_alp.py "path/to/model.alp"

# 以参考模型为底稿生成新模型
python scripts/clone_template.py \
  --src "path/to/reference.alp" \
  --dst "path/to/new.alp" \
  --name "NewModel"

# 装配块、连接器、目标线到目标模型
python scripts/graft_blocks.py \
  --example "path/to/reference.alp" \
  --target "path/to/target.alp" \
  --out "path/to/output.alp" \
  --blocks blockA,blockB,blockC \
  --pkg-target <package>
```

## 结构说明

`.alp` 的层级、库块、连接器、目标线结构见 `references/alp-structure.md`。

关键点：

- 块必须位于 `Level/Presentation` 层
- 库块用 `EmbeddedObject + ClassName` 标识
- 连接器通过 `ItemName` 引用块和端口
- 行人链需要 `TargetLine` 作为进入/离开边界

## 已知边界

- 模板覆盖范围内：可装配、可参数化、可交付
- 模板覆盖范围外：需要先准备一个可加载的参考结构
- 生成后用 AnyLogic 打开验证；没有命令行校验替代

## 相关技能

- `anylogic-logistics-advisor` — 仓储与供应链的选型、容量估算、建模蓝图
- `wanghan-anylogic-help` — 官方文档索引与报错签名
