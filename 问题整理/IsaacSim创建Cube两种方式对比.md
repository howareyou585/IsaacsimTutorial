# Isaac Sim 创建 Cube 的两种方式对比（原生 USD API vs 实验 API）

> 对比 `stage.DefinePrim("/World/Cube","Cube")` + `UsdGeom.Cube(...)` 与 `Cube(paths=..., positions=..., sizes=...)` 两种写法的区别。
> 关联章节：学习指南第 4 章（USD Stage，教底层方式）、第 5 章（World 与物理，教高层方式）。

## 一句话版本

**方式 B 是方式 A 的封装糖衣**：`Cube(paths, positions, sizes)` 底层干的就是 `DefinePrim` + `CreateSizeAttr` + `AddTranslateOp` 那三步，只是打包成一次调用。

## 逐项对比

| 维度 | A：`DefinePrim` + `UsdGeom`（第 4 章） | B：`Cube(...)`（第 5 章） |
|---|---|---|
| **API 归属** | 原生 USD（`pxr`，Pixar 的行业标准） | Isaac Sim 高层封装（`isaacsim.core.experimental.objects`） |
| **层数** | 底层，直接写"节目单" | 高层，一行调用底层帮你写"节目单" |
| **步数** | 三步：定义 → 设尺寸 → 设位置 | 一步：构造参数全给 |
| **批量** | 一次一个 prim | `paths` 支持列表/正则，`positions`/`sizes` 跟着变列表，**一次创建一排** |
| **通用性** | 任何 USD 环境通用（USDView、其他 DCC 软件） | 只在 Isaac Sim 里存在 |
| **可配参数** | 要什么属性自己一个个加 | 构造参数直接给：`scales`、`colors`、`orientations`…… |
| **返回值** | 裸 prim（USD 的 `Usd.Prim`） | 高层对象，可无缝接后续的 `GeomPrim`/`RigidPrim` 包裹链 |

## 等价翻译

这两段代码在舞台上留下的东西**一模一样**：

```python
# 方式 A：亲手往节目单上写三笔
cube_prim = stage.DefinePrim("/World/MyCube", "Cube")       # 写一行：有个 Cube
UsdGeom.Cube(cube_prim).CreateSizeAttr().Set(0.5)           # 写：size = 0.5
UsdGeom.Cube(cube_prim).AddTranslateOp().Set((0, 3, 0))     # 写：位置 (0,3,0)

# 方式 B：一句话让助理帮你写同样的三笔
cube = Cube(paths="/World/MyCube", positions=[(0, 3, 0)], sizes=0.5)
```

验证方法：两种各存一份 `.usda`，用记事本打开对比——内容一致（都只是 `def Cube` + `size` + `xformOp:translate` 那几行）。这正好验证第 4 章的观点：**Stage 就是文本，殊途同归**。

## 两个容易搞混的点

### 1. 两种方式创建的都只是"描述"，都不会下落

B 方式的 `Cube` 名字看着高级，但它同样只是几何+变换描述（第 4 章说的"全息影像"）。要下落都得走第 5 章那套三步：

```python
cube = Cube(paths="/World/MyCube", positions=[(0,3,0)], sizes=0.5)  # 描述
GeomPrim(["/World/MyCube"], apply_collision_apis=True)              # 贴"碰撞"标签
RigidPrim(["/World/MyCube"])                                        # 贴"刚体"标签
```

A 方式如果想加物理，就得自己 `UsdPhysics.CollisionAPI.Apply(prim)` + `RigidBodyAPI.Apply(prim)`——更啰嗦，这正是 B 体系存在的意义。

### 2. 参数单复数是记忆锚点

- A 是底层属性方法，**单数**：`CreateSizeAttr`（一个属性）。
- B 是批量接口，**全复数**：`paths`、`positions`、`sizes`——因为它设计上就是给"一次一排物体 + GPU 批量计算"用的（Warp 后端）。
- 传 `prim_path=`/`position=` 报错（问题整理文档问题 8 系列的坑），根源就是 B 的参数是复数形式。

## 什么时候用哪个

| 场景 | 用哪个 |
|---|---|
| 日常开发（标准几何体、后续要物理/批量） | **B**——简洁、可批量、能接实验 API 生态 |
| 创建没有封装的东西（Scope、自定义类型 prim、Camera 这类） | **A**——只能自己 `DefinePrim` |
| 要理解 USD 本质、写通用工具、排查场景结构 | **A**——看得见每一笔 |
| 跟官方教程/其他 USD 资料 | 两种都会遇到，都得认识 |

**指南的设计也是这个逻辑**：第 4 章用 A 教"prim 就是节目单上的一行字"（看清本质），第 5 章起切到 B（工程上顺手）。Isaac Sim 仓库自己的开发规范（`.cursor/rules/usd_prefer_experimental_api.mdc`）也是同样的优先级：能用实验 API 就不手写 pxr。
