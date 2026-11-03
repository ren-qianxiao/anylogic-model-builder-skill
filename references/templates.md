# 结构模板库

按**流程环节**选择，不按行业名选择。每个模板都来自 AnyLogic 参考模型的结构分析，记录了可提取的块、连接和依赖。

参考模型根目录：

```
E:/AnyLogic/AnyLogic 8.9 Professional/plugins/com.anylogic.examples_8.9.8.*/
├── models/        物流、供应链、生产、交通
└── basicmodels/   行人、流程、基础库
```

## 模板清单

| 场景 | 参考模型 | 关键块 | 可直接提取的链条 | 依赖 |
|---|---|---|---|---|
| 行人行走 | `basicmodels/Areas with Restrictions for Pedestrians` | PedSource, PedGoTo, PedSink, PedWait, PedSettings | `clientSource → returnToMall → servedPerson` + 2 条 TargetLine | pedestrian |
| 行人密度/统计 | `basicmodels/Pedestrian Flow Statistics` | 块在子智能体里，Main 只有图形 | 不直接提取，参考其统计配置 | pedestrian |
| 配送中心收发货 | `models/Distribution Center` | Seize, Hold, Store, Retrieve, Split, Pickup, MoveTo, RestrictedArea | 收货链、组单链、发货链 | processmodeling, material_handling |
| 输送线 | `models/Warehouse conveyor` | Convey, ConveyorNetwork, PalletSource, DropOffStation, PickingStation | 整托拆零、空托回流、多段输送 | material_handling |
| 多层输送与拣选 | `models/Fulfillment Center Conveyor System` | Convey, BottomPickingArea, SmartRack, Sink | 声明式输送路由、拣选到包装 | material_handling |
| 自由空间 AGV | `models/Transporters Moving in Free Space` | TransporterFleet, MoveByTransporter, StationBuffer, Convey | 双车队主线搬运 + 线边补料 | material_handling |
| 多任务 AGV | `models/Material Handling in Hospital` | SeizeTransporter, MoveByTransporter, Release, MHStation | 送餐/布草/污物三类任务共用车队 | material_handling |
| 共享机器人/AGV | `models/Palletizing system with AGV` | MoveByTransporter, Pickup, Combine, ProcessByRobot | 缺料请求、优先级互斥、整层抓取 | material_handling |
| 铁路到发编组 | `models/Classification Yard` | TrainSource, TrainMoveTo, TrainDecouple, TrainCouple, TrainDispose | 摘钩、按车种集结、满编发车 | rail |
| 三级供应链 | `models/Supply Chain` | Factory, Wholesaler, Retailer（纯智能体） | 智能体层级、端口消息、s/S 决策 | 无 |
| 连续流管网 | `models/Oil Supply Chain` | FluidSource, Tank, Valve, Pipeline, FluidSplit, FluidExit | 储罐—管道—阀门—分液 | fluid |
| 生产物流 | `models/Chocolate Production` | Tank, ProcessTank, MixTank, Pipeline, BulkConveyor | 连续生产到离散包装 | fluid, processmodeling |

## 取用方式

用 `graft_blocks.py` 把模板里的块、连接器、目标线搬到目标模型：

```bash
python -I scripts/graft_blocks.py \
  --example "<参考模型>.alp" \
  --target "<目标模型>.alp" \
  --out "<输出>.alp" \
  --blocks <块1>,<块2>,... \
  --pkg-target <目标包名> \
  --offset-x <dx> --offset-y <dy>
```

规则：

1. **整条链路的块都要列出来**，漏掉中间块会断链
2. 只改 Id、Name、PackageName、坐标，不动块的内部结构
3. 运行后看 `dangling refs`，必须为 0
4. 用 `inspect_alp.py` 确认块数增加
5. 最后在 AnyLogic 中打开确认

## 组合建议

- 行人 + 产线：`Areas` 的行人链 + `Warehouse conveyor` 的输送线
- AGV + 仓储：`Transporters Moving in Free Space` 的车队 + `Distribution Center` 的月台
- 供应链 + 产能：`Supply Chain` 的三级智能体 + `Supply Chain and Product Diffusion` 的 SD 产能
- 铁路 + 码头：`Classification Yard` 的编组 + `Grain Terminal` 的卸粮线

组合后必须检查：连接器两端是否都在目标模型里、坐标是否重叠、库依赖是否齐全。
