# Isaac Sim 6.0.1 缓存地图

> 盘点 Isaac Sim 各缓存的作用、目录位置与清理策略。所有大小为本机实测值（2026-08-24 扫描）。
> 关联条目：问题 12（云端资产与按需下载）、问题 4（移动目录后注册表重建）、问题 7（换驱动后着色器缓存重编）。

## 总览

Isaac Sim 的缓存分四个区域：

| 区域 | 位置 | 本机总占用 |
|---|---|---|
| 主缓存区 | `C:\Users\<用户名>\AppData\Local\ov\cache\` | ~5.2 GB |
| Warp 内核缓存 | `C:\Users\<用户名>\AppData\Local\NVIDIA\warp\Cache\` | ~72 MB |
| 用户数据（非缓存，勿删） | `C:\Users\<用户名>\AppData\Local\ov\data\` | 小 |
| 日志（非缓存，可清理） | `~\.nvidia-omniverse\logs` + 安装目录 `kit\logs` | ~3.1 GB |

---

## 一、主缓存区：`%LOCALAPPDATA%\ov\cache\`

| 缓存 | 作用 | 本机大小 | 删了会怎样 |
|---|---|---|---|
| **shaders** | 着色器缓存。GPU 着色器编译后的二进制。**首次启动慢 5-10 分钟就是在编译它**。按"显卡型号 + 驱动版本"键控 | 538 MB | 下次启动重新编译，又慢一次；之后恢复秒开。换驱动/显卡时它本来就会自动失效重编 |
| **client** | omni.client 资产缓存。从云端（NVIDIA S3 资产库）下载的资产，按内容哈希存放，不保留原始文件名。就是"**云端资产的本地落地**" | 1158 MB | Franka、默认环境等全部重新联网下载。学习指南前 9 章的资产都在里面，删了断网就跑不了 |
| **DerivedDataCache** | 派生数据缓存。物理 cooking 结果（碰撞体凸包分解）、场景组合中间产物。加载带物理的场景后涨得快 | 3494 MB | 下次加载场景重新计算，首次变慢。**本机目前最大的一块** |
| **Kit** | Kit 应用自身缓存（材质缓存 material_cache.json 等），实际在 `Kit\110.1\<哈希>\` 下 | ~0 MB | 无感。官方 `clear_caches.bat` 想清的就是它——**但该脚本写死的版本号 `Kit\107.3` 已过时，实际是 `110.1`，所以它清不到，要手动删** |
| **ogn_generated** | OmniGraph 节点生成代码缓存（自动生成的 Python 代码） | 8 MB | 重新生成 |
| **texturecache** | 纹理缓存（解码/压缩后的纹理） | 0 MB | 本机还没用过带贴图的场景，所以是空的 |

## 二、Warp 内核缓存：`%LOCALAPPDATA%\NVIDIA\warp\Cache\`

实验 API（`isaacsim.core.experimental.*`）底层用的 Warp GPU 内核编译缓存。

- 本机有两个版本目录：`1.13.0`（空）+ `1.16.0`（72 MB），对应 Isaac Sim 不同组件用的 Warp 版本。
- 删了 → 内核重新编译，headless 启动时多花几秒。
- 旧版本目录（如 1.13.0）可以删。

## 三、用户数据（不是缓存，别乱删）：`%LOCALAPPDATA%\ov\data\`

- `exts` — 自己安装的扩展
- `Kit` — 应用状态：窗口布局、最近文件、偏好设置

这是"配置"不是"缓存"。删了布局和偏好全丢（效果相当于 `isaac-sim.bat --reset-user`）。

## 四、日志（不是缓存，但占空间）

| 位置 | 本机大小 | 说明 |
|---|---|---|
| `C:\Users\<用户名>\.nvidia-omniverse\logs` | **3040 MB** ⚠️ | 遥测 / NVIDIA 账号日志。**本机这块异常大**（正常几百 MB），可放心删 |
| `<安装目录>\kit\logs` | 113 MB | Kit 每次启动的运行日志。**排错第一现场**（查 RTX 报错、启动失败就看它） |

---

## 实用结论

**日常不用管缓存**——它们的存在就是为了让第二次快。

**什么时候清哪个**：

| 症状 | 清什么 |
|---|---|
| Isaac Sim 行为诡异（版本切换后出错等） | `clear_caches.bat` 那三样（shaders / texturecache / Kit）——注意 Kit 目录要手动删对应版本号 `110.1` |
| 磁盘紧张 | `~\.nvidia-omniverse\logs`（本机 3 GB）+ `DerivedDataCache`（3.5 GB），合计能腾 **约 6.5 GB**，代价只是下次启动/加载慢一次 |
| 资产加载出诡异问题 | `%LOCALAPPDATA%\ov\cache\client`（重新联网下载） |

**换驱动 / 换显卡后**：shaders 缓存自动失效重编，首次启动变慢是正常现象（更新驱动后那次 16 秒启动，就是缓存重新就位的过程）。

## 一句话记忆

> **缓存 = 用空间换时间**。shaders 换启动速度、client 换下载速度、DerivedDataCache 换加载速度。都删了也能跑，只是处处变慢一次；所以只在"行为异常"或"磁盘紧张"时才动它们。
