# .alp 结构说明

基于 AnyLogic 8.9.8 的 `.alp` 实测结构（`AlpVersion 8.9.7`）。

## 顶层

```xml
<AnyLogicWorkspace WorkspaceVersion="1.9" AnyLogicVersion="8.9.8..." AlpVersion="8.9.7">
  <Model>
    <Id>...</Id>
    <Name>模型名</Name>
    <JavaPackageName>model</JavaPackageName>
    <ModelTimeUnit>Second</ModelTimeUnit>
    <ActiveObjectClasses>...</ActiveObjectClasses>
    <Experiments>...</Experiments>
  </Model>
  <ConvertersApplied>...</ConvertersApplied>
</AnyLogicWorkspace>
```

## 智能体类

```xml
<ActiveObjectClasses>
  <ActiveObjectClass>
    <Id>...</Id>
    <Name>Main</Name>
    <Presentation>
      <Level>
        <Id>...</Id>
        <Name>level</Name>
        <X>0</X><Y>0</Y>
        ...
        <LevelVisibility>DIM_NON_CURRENT</LevelVisibility>
        <Presentation>          <!-- 关键：这一层不能少 -->
          <!-- TargetLine / EmbeddedObject / Connector / 图形 -->
        </Presentation>
      </Level>
    </Presentation>
  </ActiveObjectClass>
</ActiveObjectClasses>
```

**把元素直接挂在 `Level` 下而不放进 `Level/Presentation`，AnyLogic 打开后画布是空白。** 这是实际踩过的坑。

## 库块

库块不是独立标签，而是 `<EmbeddedObject>`，用 `ActiveObjectClass` 里的 `ClassName` 区分：

```xml
<EmbeddedObject>
  <Id>1605521571493</Id>
  <Name>pedSource</Name>
  <X>150</X><Y>300</Y>
  <ActiveObjectClass>
    <PackageName>com.anylogic.libraries.pedestrian</PackageName>
    <ClassName>PedSource</ClassName>
  </ActiveObjectClass>
  <GenericParameterSubstitute>
    <GenericParameterSubstituteReference>
      <PackageName>com.anylogic.libraries.pedestrian</PackageName>
      <ClassName>PedSource</ClassName>
      <ItemName>1412464601074</ItemName>
    </GenericParameterSubstituteReference>
  </GenericParameterSubstitute>
  <Parameters>
    <Parameter>
      <Name>locationType</Name>
    </Parameter>
    <Parameter>
      <Name>locationLine</Name>
      <Value Class="CodeValue"><Code>entryLine</Code></Value>
    </Parameter>
    ...
  </Parameters>
</EmbeddedObject>
```

要点：

- `GenericParameterSubstitute` 里的 `ItemName` 是库内部的固定泛型 ID，**不要改**。
- `Parameters` 里没有 `<Value>` 的项表示使用库默认值，可以保留空。
- 如果参数引用自定义 agent（如 `newPed` 指向示例里的 `Client`），迁移到新模型后必须删除或改指向，否则编译失败。

## 连接器

```xml
<Connector>
  <Id>...</Id>
  <Name>connector1</Name>
  <X>...</X><Y>...</Y>
  <SourceEmbeddedObjectReference>
    <PackageName>model</PackageName>
    <ClassName>Main</ClassName>
    <ItemName>pedSource</ItemName>
  </SourceEmbeddedObjectReference>
  <SourceConnectableItemReference>
    <PackageName>com.anylogic.libraries.pedestrian</PackageName>
    <ClassName>PedSource</ClassName>
    <ItemName>out</ItemName>
  </SourceConnectableItemReference>
  <TargetEmbeddedObjectReference>
    <PackageName>model</PackageName>
    <ClassName>Main</ClassName>
    <ItemName>pedGoTo</ItemName>
  </TargetEmbeddedObjectReference>
  <TargetConnectableItemReference>
    <PackageName>com.anylogic.libraries.pedestrian</PackageName>
    <ClassName>PedGoTo</ClassName>
    <ItemName>in</ItemName>
  </TargetConnectableItemReference>
  <Points>...</Points>
</Connector>
```

- `*EmbeddedObjectReference` 指向所在智能体（通常是 `Main`），`PackageName` 是模型包名。
- `*ConnectableItemReference` 指向库类的端口：`out` / `in`。
- 改块名时，两处 `ItemName` 都要同步。

## 空间标记：TargetLine

```xml
<TargetLine>
  <Id>...</Id>
  <Name>entryLine</Name>
  <X>100</X><Y>230</Y>
  <Points>
    <Point><X>0</X><Y>0</Y></Point>
    <Point><X>0</X><Y>140</Y></Point>
  </Points>
</TargetLine>
```

`Points` 是相对于 `X/Y` 的局部坐标。竖线 = x 不变、y 变化。

## 行人库的最小链条

```
TargetLine(entryLine) → PedSource(locationLine=entryLine) → PedGoTo(locationLine=目标线) → PedSink
```

- `PedSource` 必须有 `locationLine`，否则运行时报 `pedEnter: 参数'targetLine'未指定`。
- `PedGoTo` 的 `locationLine` 指向目标线；如果改用坐标点，需要设置 `locationType=POINT` 和 `locationX/Y`，但枚举值的 XML 编码未验证，优先用目标线。
- `PedSink` 不需要目标线。

## 改参数的优先级

1. 改 `<Parameter>/<Value>` —— 最安全
2. 改 `<Name>` 并同步所有引用 —— 中等
3. 增删元素 —— 高风险，优先复用已有元素再改，不要手写新标签

## 整段装配的实操要点

从官方示例搬一条流程时，四样东西要一起搬：

| 东西 | 怎么找 | 容易漏 |
|---|---|---|
| 块 | `<EmbeddedObject>` + `ClassName` | 中间块 |
| 连接器 | `Source/TargetEmbeddedObjectReference` | 只搬两端会断链 |
| 目标线 | 块的 `locationLine` 参数值 | 缺线则运行报 targetLine 未指定 |
| 库依赖 | `RequiredLibraryReference` | 缺 pedestrian 库则编译失败 |

改写时只动这四类字段：`Id`、`Name`（及引用）、`PackageName`、`X/Y`。块的 `<Parameters>` 结构不要动。

已验证可用的模板位置：

- 行人最小链：`basicmodels/Areas with Restrictions for Pedestrians/`，块 `clientSource → returnToMall → servedPerson`，配 `pedSettings` 和两条 `TargetLine`
- 行人统计：`basicmodels/Pedestrian Flow Statistics/`（Main 里没有块，结构在别处，不适合直接搬）
- 物流/供应链：`models/` 下的 39 个案例，索引见 `official-examples.md`

搬运后跑 `graft_blocks.py`，检查输出的 `dangling refs` 是否为 0；再用 `inspect_alp.py` 确认块数增加。
