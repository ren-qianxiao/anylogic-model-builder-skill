# 已知坑（按代价排序）

## 1. 元素挂错层级 → 打开空白

`.alp` 的层级是：

```
ActiveObjectClass → Presentation → Level → Presentation → 块
```

把 `TargetLine`、`EmbeddedObject`、`Connector` 直接放到 `Level` 下（漏掉最后那层 `Presentation`），AnyLogic 不报错，但画布空白。

**验证方法**：`python scripts/inspect_alp.py <file>`，看块是否被计入；或打开文件看画布。

## 2. 行人不出现：`pedEnter: 参数'targetLine'未指定`

`PedSource` 的 `locationLine` 为空。必须有一条 `TargetLine`，并在 `PedSource` 的参数里引用它的名字。

`PedGoTo` 同理：用目标线时 `locationLine` 必须指向一条存在的线。

## 3. 迁移块后编译失败：参数引用了示例里的自定义 agent

例如 `PedSource` 的 `newPed` 参数指向示例的 `Client` agent。新模型没有这个 agent，编译时报找不到类。

**处理**：删除 `newPed` 参数，让库用默认的 `Pedestrian`；或者把引用改成新模型里存在的类。

## 4. 改块名后连接断开

`Connector` 的 `SourceEmbeddedObjectReference/ItemName` 和 `TargetEmbeddedObjectReference/ItemName` 都要同步改。只改 `<Name>` 不改引用，运行时不报错但流程断开。

## 5. 包名不一致

`Connector` 里的 `SourceEmbeddedObjectReference/PackageName` 是模型包名（`JavaPackageName`）。迁移到新模型后如果包名不同，要统一改；否则引用解析不到。

## 6. 演示上限把模型锁死

官方示例常用演示级上限：

| 示例 | 上限 | 后果 |
|---|---|---|
| Distribution Center | `sourceTruckToUnload.maxArrivals=25` | 只产生 25 辆车 |
| Distribution Center | `createOrderEvent` 条件 `lastOrderId < 11` | 只产生 11 张订单 |
| Distribution Center | `ordersListMaxLength=50` | 50 单后停止创建 |
| Supply Chain | `demandGenerator` 是 `rate=10 PER_DAY` | 改成日需求时只换分布会变成 10 倍 |

迁移后先列一张“必须覆盖的默认值”清单。

## 7. 同时事件顺序（LIFO）

`.alp` 默认 `SelectionModeForSimultaneousEvents=LIFO`。到货事件和日检查事件在同一时刻触发时，检查可能先于到货，等效提前期 +1 天。

处理：把交付延迟改成 `L*day() - 1*minute()`，保证到货早于检查。

## 8. 重建 XML 丢 CDATA

用 ElementTree 重写会把 `<![CDATA[...]]>` 变成普通文本。多数情况 AnyLogic 能解析，但原文件里的特殊字符和空白可能变化。优先做字符串级的最小替换，不用整树重写。

## 9. ID 冲突

`Id` 在同一模型内要唯一。迁移元素时不要保留原 `Id`，用新数字。冲突可能导致加载失败或元素互相覆盖。

## 10. 版本差异

`.alp` 头部有 `AnyLogicVersion` 和 `AlpVersion`。从 8.9.6 模型迁移到 8.9.8 通常可以，但反向（新→旧）可能失败。迁移时保留目标模型自己的头部。
