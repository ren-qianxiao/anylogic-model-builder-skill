# anylogic-model-builder

AnyLogic 8.x 模型构建技能：**复制已验证的官方示例，而不是手写 `.alp`**。

## 为什么

`.alp` 是 AnyLogic 的私有 XML 格式，没有 schema、没有命令行校验。实测从零手写会导致 AnyLogic 打开空白（层级、泛型 ID、连接器引用都无法凭记忆写对）。

因此本技能的工作方式是：

```
需求 → 选官方示例 → 复制骨架 → 改参数 → 打开验证
```

## 内容

- `SKILL.md` — 工作流、能力边界、结构速查
- `references/official-examples.md` — 118 个官方示例索引（块、库、3D、实验）
- `references/alp-structure.md` — `.alp` 的层级、库块、连接器、行人库链条
- `references/pitfalls.md` — 实测踩过的 10 个坑
- `scripts/inspect_alp.py` — 解析任意 `.alp` 的结构摘要
- `scripts/clone_template.py` — 复制官方示例并改模型名
- `scripts/graft_blocks.py` — 从示例整段搬运块/连接器/目标线到目标模型

## 用法

```bash
# 看结构
python scripts/inspect_alp.py "path/to/model.alp"

# 复制示例并改名
python scripts/clone_template.py \
  --src "E:/AnyLogic/.../models/Supply Chain/Supply Chain.alp" \
  --dst "C:/Users/me/Models/MyModel/MyModel.alp" \
  --name "MyModel"
```

## 能力边界

- ✅ 选案例、复制骨架、改参数、解析结构
- ❌ 从零构造可加载的 `.alp`（已实测失败）
- 生成后必须用 AnyLogic 打开验证，没有 CLI 替代

## 相关技能

- `anylogic-logistics-advisor` — 仓储/供应链的选型与容量估算
- `wanghan-anylogic-help` — 官方文档与报错签名
