# Isaac Sim 6.0.1 安装配置问题整理

> 记录在本机（Windows 11 + RTX 4070）搭建 Isaac Sim 6.0.1 过程中遇到的真实问题、原因分析和解决方法。全部为实际踩坑后的验证结论，供后续查阅。

## 最终环境（已验证可用）

| 项 | 值 | 官方要求 | 状态 |
|---|---|---|---|
| GPU | NVIDIA GeForce RTX 4070（12GB 显存） | 最低 RTX 4080 / 16GB | ⚠️ 低于官方最低，学习够用 |
| 驱动 | 610.88 | ≥ 595.97 | ✅ 达标（已更新） |
| OS | Windows 11 专业版（Build 26200） | 仅 Windows 11 / Ubuntu 22.04/24.04 | ✅ 达标 |
| RAM | 32GB | ≥ 32GB（推荐 64GB） | ✅ 达标（卡最低线） |
| 磁盘 | 安装盘剩余 50GB+ | ≥ 50GB SSD | ✅ 达标 |
| 安装方式 | 预编译独立包（standalone zip） | — | — |
| 安装路径 | `D:\robotSim\isaac-sim6` | — | ✅ 可用 |
| 自带 Python | 3.12.13 | 3.12 | ✅ 达标 |

---

## 问题清单速查

| # | 问题 | 一句话原因 | 解决 |
|---|---|---|---|
| 1 | 怎么判断电脑能不能跑 Isaac Sim | 需对照官方硬件清单逐项查 | 见问题 1 |
| 2 | 克隆了源码却跑不了 | 源码 ≠ 可运行程序，需构建或装二进制 | 见问题 2 |
| 3 | `python.bat` 报 not recognized | PowerShell 跑当前目录程序要加 `.\` | 见问题 3 |
| 4 | 移动安装目录后 `ModuleNotFoundError: isaacsim` | kit 扩展注册表写死了旧绝对路径 | 见问题 4 |
| 5 | GUI 启动报 `vkCreateRayTracingPipelinesKHR failed` | 驱动版本低于要求，RTX 管线建不起来 | 见问题 5 |
| 6 | 运行时冒 `get_default` / `invalid prim` 报错 | Omniverse 无害小毛病 | 见问题 6 |
| 7 | 怎么确认 RTX 渲染修好了 | 更新驱动后跑渲染验证 | 见问题 7 |
| 8 | 终端/VSCode 跑脚本报 `ModuleNotFoundError: isaacsim` | 用了系统 Python，没用自带 python.bat | 见问题 8 |
| 9 | `SimulationApp({"headless",False})` 报 ValueError | 逗号写成了集合，应为冒号字典 | 见问题 9 |
| 10 | 加载资产报 "Unable to get Sdf layer / might not exist" | 硬编码 `omniverse://Isaac/...`，把 `Isaac` 当成了服务器主机 | 见问题 10 |
| 11 | Script Editor 里 `from isaacsim import SimulationApp` 报 ImportError | Script Editor 在已运行的 App 里，不能再创建 SimulationApp | 见问题 11 |
| 12 | `get_assets_root_path()` 返回的 S3 地址是什么 | NVIDIA 官方云端资产库（AWS S3），按需下载 + 本地缓存 | 见问题 12 |
| 13 | `simulation_app.get_simulation_time()` 报 AttributeError | 方法在 `SimulationManager` 上，不在 `SimulationApp` 上 | 见问题 13 |
| 14 | `GetRootLayer().SaveAs(...)` 报 AttributeError | `Sdf.Layer` 没有 `SaveAs` 方法；匿名层要用 `Export` | 见问题 14 |
| 15 | 加载自己的机器人 USD 报 "Expected )" | USD 文件里混进一行非法语法（裸元组） | 见问题 15 |
| 16 | Script Editor 报 `NameError: stage_utils` / `SyntaxError: '(' was never closed` | 没导入就使用别名 / 括号张嘴不闭嘴 | 见问题 16 |
| 17 | `Articulation("/World/Franka_.*")` 报 ValueError | 正则搜错了名字；`dof_paths` 是嵌套套娃 | 见问题 17 |
| 18 | play 前调 `set_dof_position_targets` 报 Invalid DOF type | 物理张量只在"营业时间"（play 中）有效，读写都一样 | 见问题 18 |

---

## 问题 1：如何判断电脑能否运行 Isaac Sim 6.0.1

**需求**：装之前先确认硬件够不够格。

**检查方法**（逐条）：

```bash
# 查 GPU 型号、显存、驱动版本
nvidia-smi
```

再看：操作系统版本、内存大小、磁盘剩余空间。

**官方要求（Isaac Sim 6.x，已对官方文档核实）**：

- **GPU**：最低 GeForce RTX 4080，显存 16GB。不支持无 RT Cores 的卡（A100/H100 这类数据中心卡），不支持 Mac。
- **驱动**：Linux 595.58.03 / Windows 595.97。
- **RAM**：≥ 32GB（推荐 64GB）。
- **磁盘**：≥ 50GB SSD。
- **OS**：Windows 11（Windows 10 不支持）/ Ubuntu 22.04、24.04。

**本机结论**：

- GPU RTX 4070（12GB）**低于官方 16GB 最低线**——但学习用途（单机器人、简单场景）够用；复杂场景、批量合成数据、并行 RL 训练会爆显存。
- 其余（OS/RAM/磁盘）达标。
- 驱动 595.71 **低于要求**，需更新（见问题 5）。

**补充**：官方有个一键体检工具 **Isaac Sim Compatibility Checker**，在安装目录里直接跑：

```bash
# Windows
.\isaac-sim.compatibility_check.bat
# Linux
./isaac-sim.compatibility_check.sh
```

它用红绿灯标出每项是否达标：绿=优秀，浅绿=良好，橙=够用但建议更高，红=不够/不支持。还有个 **Test Kit** 按钮能验证核心引擎能否真正跑起来。装完、换显卡、升级驱动后跑它最直观。

---

## 问题 2：克隆了源码仓库，却跑不了 Isaac Sim

**现象**：`F:\newton\IsaacSim` 只有 `source/`、`deps/`、`docs/` 等源码目录，没有 `_build/` 输出；`pip show isaacsim` 也找不到。跑 `from isaacsim import SimulationApp` 报 `ModuleNotFoundError`。

**原因**：**源码 ≠ 可运行程序**。Isaac Sim 源码仓库要用 `build.bat` 从源码构建（需 Visual Studio 2022、Git LFS，编译 30-60 分钟），这条路是给想改 Isaac Sim 平台本身的人准备的。单纯学习和开发应用不需要构建源码。

**三条获取可运行 Isaac Sim 的路**：

1. **PIP 安装**：`pip install isaacsim[all,extscache]==6.0.1.0 --extra-index-url https://pypi.nvidia.com`（需 Python 3.12，注意 `--extra-index-url` 不能少）。适合纯学习、写脚本。
2. **预编译独立包（本次采用）**：NVIDIA 官网下 `isaac-sim-standalone-6.0.1-windows-x86_64.zip`（约 9.87GB），解压即用。适合要看 GUI 的学习者。
3. **源码构建**：只有要改 Isaac Sim 平台源码才需要。

**注意**：系统 Python 是 3.13，Isaac Sim 6.0.1 的 PIP 包要求 3.12，版本不兼容。独立包自带 Python 3.12，不受系统 Python 影响。

**结论**：选独立包，解压到 `D:\robotSim\isaac-sim6`（路径无空格无中文）。源码仓库留着当参考资料即可。

---

## 问题 3：PowerShell 里运行 `python.bat` 报 not recognized

**报错**：

```
python.bat : The term 'python.bat' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**原因**：**PowerShell 默认不搜索当前目录**。这和 CMD 不同——CMD 会在当前目录找可执行文件，PowerShell 不会。

**解决**：加 `.\` 前缀，明确指定当前目录：

```powershell
# 错误
python.bat -c "..."
# 正确
.\python.bat -c "..."
```

同理，启动主程序是 `.\isaac-sim.bat`，不是 `isaac-sim.bat`。

---

## 问题 4：移动安装目录后报 `ModuleNotFoundError: No module named 'isaacsim'`

**现象**：Isaac Sim 从 `E:\download\...` **剪切**到 `D:\robotSim\isaac-sim6` 后，跑 `from isaacsim import SimulationApp` 报 `ModuleNotFoundError`。移动前在 E:\ 是正常的。

**原因**：第一次在 E:\ 启动时，kit 把**扩展注册表**（记录每个扩展在哪）解析成了 E:\ 的绝对路径。剪切到 D:\ 后，kit 仍去读已被掏空的 E:\ 路径，`isaacsim` 命名空间拼不出来，于是报模块找不到。

**注意**：问题出在用户配置缓存，不在安装目录。所以重新解压到 D:\ 也没用——必须让注册表重建。

**解决**：让 kit 重新扫描扩展、重建注册表即可。实际上只要**在新位置完整启动一次**，kit 检测到路径变化会自动重建（相当于自愈）。本次就是跑了一条 `sys.path` 诊断命令触发重建后恢复的。

更直接的办法（任选其一）：

```powershell
# 方法 1：重置用户配置（推荐，一刀切）
.\isaac-sim.bat --reset-user

# 方法 2：清 Kit 扩展缓存（手动）
# 删除 %LOCALAPPDATA%\ov\cache\Kit\<版本号> 目录后重启
```

**经验教训**：

- **别在首次启动后再移动安装目录**。要移动，移动后第一次启动会慢（重建注册表，约 3 分钟），属正常。
- 官方自带的 `clear_caches.bat` 里写死的 Kit 缓存版本号是旧值（107.3），和新版（110.1）对不上，清不到正确目录——所以那个脚本不一定管用，手动删对应版本号目录更靠谱。

---

## 问题 5：GUI 启动报 RTX 光追管线失败

**报错**：

```
[Error] [omni.rtx] VkResult: ERROR_INITIALIZATION_FAILED
[Error] [omni.rtx] vkCreateRayTracingPipelinesKHR failed.
```

更早的无头测试里还有：

```
[Error] [omni.rtx] vkCreateComputePipelines failed.
NVVM compilation failed: 3
```

**关键区别——为什么无头能跑、GUI 起不来**：

- **无头模式**（`headless: True`）：不建显示用的光追管线，所以能跑——物理、逻辑、扩展加载都正常。
- **GUI 模式**（`isaac-sim.bat`）：必须初始化完整的 RTX 光追渲染器，要调 Vulkan 的 `vkCreateRayTracingPipelinesKHR`。**这一步在驱动 595.71 上失败。**

**原因**：驱动版本不够。NVVM 是驱动自带的着色器编译器，595.71 缺了 Isaac Sim 6.0.1 渲染器需要的 Vulkan RTX 支持，着色器编不过，光追管线建不起来。官方要求 Windows 驱动 ≥ 595.97。

**解决**：更新驱动。

1. 去 `https://www.nvidia.com/download/index.aspx`（或用 GeForce Experience）。
2. 选 GeForce RTX 4070 → Windows 11 → 下最新 Game Ready / Studio 驱动（≥ 595.97）。
3. 覆盖安装，**重启电脑**。

本次更新到 **610.88** 后，RTX 管线全部恢复正常（见问题 7）。

---

## 问题 6：运行时的两个无害报错

GUI 跑起来后，使用过程中会偶尔冒这两个报错。**都不致命，可以忽略**。

### 6.1 `'SimpleBoolModel' object has no attribute 'get_default'`

**完整报错原文**：

```
libpng warning: iCCP: known incorrect sRGB profile
[Error] [omni.ui.python] AttributeError: 'omni.ui._ui.SimpleBoolModel' object has no attribute 'get_default'

At:
  .../extscache/omni.kit.viewport.menubar.core-107.2.2+f9bf0dda/omni/kit/viewport/menubar/core/model/reset_button.py(83): refresh
  .../reset_button.py(106): _build_ui
  .../reset_button.py(65): __init__
  .../menubar/core/preference/menubar_treeview_delegate.py(84): build_widget
```

**源码定位**：打开 `D:\robotSim\isaac-sim6\extscache\omni.kit.viewport.menubar.core-107.2.2+f9bf0dda\omni\kit\viewport\menubar\core\model\reset_button.py`，第 83 行：

```python
def refresh(self):
    visible = False
    if self._helpers:
        for helper in self._helpers:
            default = helper.get_default()      # 第 83 行：崩在这里
            current = helper.get_value()
            if default != current:
                visible = True
                break
    self._reset_button.visible = visible
```

**这是什么**：这是视口菜单栏偏好设置里那个**"重置为默认值"小方块按钮**的构建代码。逻辑是：遍历每个设置项，比较"默认值"和"当前值"，不一样就显示那个重置小按钮。问题出在 `helper.get_default()`——helper 底层包装的 `SimpleBoolModel` 这个版本里**没有 `get_default` 方法**。

**原因**：扩展（`omni.kit.viewport.menubar.core` 107.2.2）和底层 UI 库（`omni.ui`）版本轻微错位——扩展以为有这个 API，库里面还没有。可能来自移动后扩展注册表重建时的小错位，也可能是 6.0.1 这个 build 自带的小毛病。

**影响**：只影响那个"重置小方块"的显示，其余一切正常。**非致命，app 照常跑。**

**处理**：忽略即可。嫌它反复刷屏，可以 `.\isaac-sim.bat --reset-user` 重置一次用户配置试试（不保证一定消，但无害）。

### 6.2 `RuntimeError: Accessed schema on invalid prim`

**完整报错原文**：

```
[Error] [asyncio] Task exception was never retrieved
future: <Task finished name='Task-5281' coro=<SimplePropertyWidget.build_items_async() ...> exception=RuntimeError('Accessed schema on invalid prim')>
Traceback (most recent call last):
  File ".../omni/kit/window/property/templates/simple_property_widget.py", line 333, in build_items_async
    self.build_items()
  File ".../omni/kit/property/material/scripts/widgets/material_binding/material_binding_widget.py", line 626, in build_items
    binding = get_binding_from_prims(self._payload.get_stage(), self._payload, self._material_purpose)
  File ".../omni/kit/property/material/scripts/widgets/material_binding/material_utils.py", line 150, in get_binding_from_prims
    db = UsdShade.MaterialBindingAPI(mprim).GetDirectBinding(material_purpose)
RuntimeError: Accessed schema on invalid prim
```

**调用链**：属性面板 `build_items_async`（异步刷新）→ 材质绑定 widget `build_items` → `material_utils.py:150` 的 `UsdShade.MaterialBindingAPI(mprim).GetDirectBinding()`，要读的那个 prim（`mprim`）已经失效。

**这是什么**：Omniverse **属性面板的经典无害毛病**。机制是——你点了某个物体，材质属性面板异步去刷它的材质绑定；等你又点了别处（或取消了选择），那个异步任务才跑完，回头去读之前那个 prim，它已经失效了，于是抛 `invalid prim`。日志里的 `Task exception was never retrieved` 就是这个意思：一个异步任务抛了异常，没人去接，只被记录下来。

**出现时机**：你在 Stage 里点选、切换选择、删除物体时，属性面板刷新没跟上你的手速，就可能冒一条。

**影响**：无。纯属属性面板刷新时机问题，不影响仿真也不影响数据。

**处理**：忽略。用 Isaac Sim 的人天天看到这个。

### 6.3 `libpng warning: iCCP: known incorrect sRGB profile`

- 内置素材里某张 PNG 图片的颜色 profile（iCCP 块）写法不标准。纯警告，零影响。这条常和 6.1 一起出现在同一段日志里。

### 什么时候该紧张

| 情况 | 要不要管 |
|---|---|
| 启动不了、闪退、黑视口 | ✅ 要管 |
| 启动时反复 `[Error] [omni.rtx] vkCreate...` | ✅ 要管（驱动问题） |
| `libpng warning`、`Task exception was never retrieved`、`invalid prim`、小部件 `AttributeError` | ❌ 噪音，忽略 |

---

## 问题 7：驱动更新后如何确认 RTX 渲染修好了

**方法**：跑一次启动 + 加载默认环境 + 渲染若干帧，盯之前的报错是否消失。

```powershell
.\python.bat -c "from isaacsim import SimulationApp; app = SimulationApp({'headless': True}); import isaacsim.core.experimental.utils.stage as s; from isaacsim.storage.native import get_assets_root_path as g; s.create_new_stage(); s.add_reference_to_stage(usd_path=f'{g()}/Isaac/Environments/Grid/default_environment.usd', path='/World/Env'); from isaacsim.core.experimental.utils.app import play; play(); [app.update() for _ in range(30)]; print('RENDER_OK'); app.close()"
```

**验证结果（驱动 610.88）**：

| 报错 | 更新前（595.71） | 更新后（610.88） |
|---|---|---|
| `vkCreateComputePipelines failed` | 出现 | ✅ 消失 |
| `vkCreateRayTracingPipelinesKHR failed` | 出现 | ✅ 消失 |
| `NVVM compilation failed` | 出现 | ✅ 消失 |
| `ERROR_INITIALIZATION_FAILED` | 出现 | ✅ 消失 |

启动到 `Startup Complete` 仅 16 秒（缓存就绪后）。RTX 光追渲染恢复正常。

---

## 问题 8：终端 / VSCode 跑脚本报 `ModuleNotFoundError: No module named 'isaacsim'`

**现象**：在 VSCode 终端或系统终端里，直接 `python ch03_hello_world.py`（或点 VSCode 的运行按钮），报：

```
Traceback (most recent call last):
  File "...\ch03_hello_world.py", line 1, in <module>
    from isaacsim import SimulationApp
ModuleNotFoundError: No module named 'isaacsim'
```

但同样的脚本，用 Isaac Sim 自带的 `python.bat` 跑就正常。

**原因**：你这次用的是**系统 Python**（本机是 3.13），它里面根本没装 `isaacsim` 包。Isaac Sim 的 Python 环境是独立的，得靠自带的 `python.bat`（Windows）/ `python.sh`（Linux）来配置 `ISAAC_PATH`、`CARB_APP_PATH`、`EXP_PATH`、`PYTHONPATH` 这一整套路径。只有在它搭建的环境里，`isaacsim` 包才能被找到。

**解决**：跑 Isaac Sim 脚本，永远用它自带的 Python：

```
D:\robotSim\isaac-sim6\python.bat F:\newton\IsaacsimTutorial\coding\chapter01\ch03_hello_world.py
```

**关于 VSCode**：想在 VSCode 里点运行按钮 / 按 F5，光把解释器指过去还不够，还得配齐那套环境变量。对新手，最省事的就是在终端敲上面那条 `python.bat` 命令。

**要让 VSCode 给 isaacsim 库做智能提示**（代码补全、跳转、参数提示），已配好：在 `F:\newton\IsaacsimTutorial\.vscode\settings.json` 里写入了 `python.analysis.extraPaths`（654 条指向 `D:\robotSim\isaac-sim6` 各扩展的绝对路径，由 Isaac Sim 官方自带的 `.vscode/settings.json` 转换而来），并把解释器指向自带的 `kit/python/python.exe`。**激活方式**：用 VSCode 打开文件夹 `F:\newton\IsaacsimTutorial`，装好 Python 扩展和 Pylance，重启后输入 `import isaacsim` 即有补全。注意智能提示只管"写代码时看得见的提示"，跑脚本仍要用 `python.bat`。

---

## 问题 9：`SimulationApp({"headless",False})` 报 `ValueError: ... length 8; 2 is required`

**现象 / 报错原文**：

```
  File "...\ch03_hello_world.py", line 2, in <module>
    simulation_app = SimulationApp({"headless",False})
  File "...\simulation_app.py", line 266, in __init__
    self.config.update(launch_config)
ValueError: dictionary update sequence element #0 has length 8; 2 is required
```

**原因**：**Python 语法笔误**。你写的是 `{"headless", False}`，中间是**逗号**——这创建的是一个**集合（set）**，里面装了两个元素 `"headless"` 和 `False`。而 `SimulationApp` 的 `self.config.update(launch_config)` 要的是**字典（dict）**。程序拿你的集合当字典解析，挨个元素拆 key:value 对，拆到 `"headless"` 这个长度为 8 的字符串时，就报 `length 8; 2 is required`（8 就是 `"headless"` 的字符数）。

**解决**：把逗号改成冒号：

```python
simulation_app = SimulationApp({"headless": False})   # ✅ 冒号 → 字典
# 错误写法：SimulationApp({"headless", False})         # ❌ 逗号 → 集合
```

**教训**：`{k: v}` 是字典，`{a, b}` 是集合，一字之差类型完全不同。凡是传配置参数的地方（`SimulationApp({...})`、`setup_simulation(...)` 等），用的都是字典，键值之间用冒号。这也正好呼应学习指南第 1 章讲的"字典和列表/集合"那节。

---

## 问题 10：加载资产报 "Unable to get Sdf layer ... might not exist"

**现象 / 报错原文**：在 Script Editor 或脚本里用 `add_reference_to_stage` 加载环境 / 机器人，报：

```
Exception: Unable to get Sdf layer. The USD file omniverse://Isaac/Environments/Grid/default_environment.usd might not exist or is not readable
At: .../isaacsim/core/experimental/utils/impl/stage.py(465): add_reference_to_stage
```

**原因**：资产路径被**硬编码**成了 `omniverse://Isaac/...`。`omniverse://` 协议的格式是 `omniverse://<服务器主机>/<路径>`——这么写就把第一段 `Isaac` 当成了**服务器主机名**。根本没有一台叫 "Isaac" 的服务器，USD 解析器找不到文件，于是报"文件不存在 / 无法获取 layer"。

补充一点：Isaac Sim 独立包的内置资产默认**不打包在本地**，而是按需从 NVIDIA 云端资产服务器下载（首次加载会联网拉取并缓存）。所以资产路径必须由"当前环境的资产根 + 相对路径"动态拼出来，写死主机名必然出错。

**解决**：用 `get_assets_root_path()` 读出当前环境的资产根，再用 f-string 拼相对路径：

```python
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.storage.native import get_assets_root_path

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
    path="/World/Environment"
)
```

**怎么自查路径对不对**：打开 Isaac Sim 的 Content Browser，手动浏览到 `Isaac/Environments/Grid/`，看 `default_environment.usd` 在不在。在 = 你的代码路径写错了；不在 = 资产没挂载或没下载成。

**教训**：凡是引用 Isaac Sim 内置资产（机器人、环境、传感器），一律 `get_assets_root_path() + "/Isaac/..."`，**绝不手写 `omniverse://主机/...`**。

---

## 问题 11：在 Script Editor 里创建 SimulationApp，报 ImportError

**现象 / 报错原文**：把独立脚本的开头两行粘进 Script Editor（Window > Script Editor）执行：

```python
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})
```

报：

```
ImportError: cannot import name 'SimulationApp' from 'isaacsim' (unknown location)
At:
  .../script_xxxx.py(1): <module>
```

**原因（用法错误）**：Script Editor 是在**已经运行的 Isaac Sim 里面**执行代码的。App 已经在跑了，**不需要、也不能再创建 `SimulationApp`**——那是 App 外面的独立脚本启动 Isaac Sim 时才用的"大门"。往运行中的 App 里再塞一个 App，方向就错了。

**原因（为什么恰好报 ImportError）**：独立脚本里 `from isaacsim import SimulationApp` 能用，靠的是 `python_packages/isaacsim/__init__.py` 这个引导包；而在**已运行的 App 内部**，`isaacsim` 解析成的是各扩展目录拼出来的命名空间包（没有顶层 `__init__.py`），顶层没有 `SimulationApp` 这个名字。报错里的 **"(unknown location)" 正是命名空间包查不到名字的典型特征**。

**解决**：把那两行**删掉**。Script Editor 里直接写"操作场景的代码 + 对应 import"：

```python
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.storage.native import get_assets_root_path

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
    path="/World/Environment"
)
```

**口诀**（学习指南第 10 章系统讲三种工作流，这里先记住区别）：

| 在哪写代码 | 要不要 SimulationApp | 要不要 while 主循环 |
|---|---|---|
| 独立脚本（用 `python.bat` 跑 .py 文件） | ✅ 要 | ✅ 要 |
| Script Editor（App 里的内置编辑器） | ❌ 不要 | ❌ 不要 |
| GUI（鼠标点菜单） | —（不写代码） | — |

**教训**：`SimulationApp` 是"App 外的大门钥匙"。进了 App（Script Editor），钥匙就用不上了；把两种工作流的代码混着抄，必踩这个坑。

---

## 问题 12：`get_assets_root_path()` 返回的地址是什么

**问题**：在 Script Editor / 脚本里查看 `get_assets_root_path()` 的返回值，得到：

```
https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.0
```

这个地址是提供资源的地址吗？

**答案**：是。这是 **NVIDIA 官方的云端资产服务器**——托管在亚马逊 AWS S3（美国西部俄勒冈区域）上的 Isaac Sim 内置资产库。所有内置资产——机器人（Franka、UR10、Nova Carter）、环境（Grid、仓库）、传感器、道具——全存在这个云库里，**按 Isaac Sim 版本分目录**（`/Assets/Isaac/6.0` 对应 6.0）。

**URL 拆解**：

| 部分 | 含义 |
|---|---|
| `omniverse-content-production` | NVIDIA 的官方内容资产库 |
| `.s3-us-west-2.amazonaws.com` | 托管在 AWS S3，美国西部（俄勒冈）区域 |
| `/Assets/Isaac/6.0` | Isaac Sim 6.0 版的内置资产目录 |

**工作机制**（这也解释了问题 10 里"为什么本地搜不到资产文件"）：

1. **独立安装包不打包资产**。9.87GB 的 zip 里只有程序本体，机器人模型等资产都在云端。
2. **按需下载 + 本地缓存**。首次加载某个资产时从 S3 下载，存入本地缓存 `%LOCALAPPDATA%\ov\cache\client\`（按内容哈希命名，不保留原始文件名；实测该目录已缓存 600+ MB，就是之前跑 Hello World 和渲染验证时下载的）。
3. **第二次加载走本地缓存**，不再联网，所以快。

**实际影响**：

- **首次加载每个新资产都要联网**，且服务器在美国西海岸，国内网络访问可能偏慢。第一次加载大场景（如仓库）卡几分钟属正常，不是死机。
- **已缓存的资产离线可用**。学习指南第 3-9 章用到的默认环境和 Franka 已缓存，断网也能跑。
- **Isaac Sim 大版本升级后资产目录跟着换**（`/Isaac/6.0` → `/Isaac/7.0`），升级后首次加载会重新下载一套。
- 返回这个地址说明当前环境是**云端资产模式**。也有别的部署方式（本地 Nucleus 服务器、本地资产包）会返回不同的根地址；个人学习用云端模式最省事，不用额外配置。

**一句话**：`get_assets_root_path()` 返回的就是"当前环境去哪拿资产"的答案——本环境从 NVIDIA 的 AWS 云库拿，按需下载、本地缓存。

---

## 问题 13：`simulation_app.get_simulation_time()` 报 AttributeError

**现象 / 报错原文**：在脚本里想读仿真时间：

```python
simulation_app.get_simulation_time()
```

报：

```
AttributeError: 'SimulationApp' object has no attribute 'get_simulation_time'
```

**原因**：方法挂错了类。`get_simulation_time()` 这个方法**存在**，但它在 `SimulationManager` 上，不在 `SimulationApp` 上（源码 `simulation_manager.py:834`，类方法，返回秒数）。两个类分工不同：

| 类 | 职责 | 有没有 `get_simulation_time()` |
|---|---|---|
| `SimulationApp` | 启动/关闭应用（"大门钥匙"） | ❌ 没有 |
| `SimulationManager` | 物理仿真调度（管 step、时间、回调） | ✅ 有 |

**顺带澄清一个概念**：`import time` 后的 `time.time()` 是**真实世界的墙上时钟**（17 亿开头的巨大时间戳），不是仿真时间。仿真世界有自己独立的时间轴，快慢由物理步长决定——headless 模式下仿真往往跑得比真实时间快得多。两者完全是两回事。

**解决**：用 `SimulationManager` 读仿真时间：

```python
from isaacsim.core.simulation_manager import SimulationManager

frame = 0
while simulation_app.is_running():
    simulation_app.update()
    frame += 1
    if frame % 60 == 0:   # 每 60 帧打印一次，免得刷屏
        print(f"仿真时间: {SimulationManager.get_simulation_time():.2f} 秒")
```

预期输出：`1.00`、`2.00`、`3.00`……稳步往前跳。默认物理步长 1/60 秒，所以每 60 帧≈1 秒仿真时间。

**教训**：想调用一个方法前先确认它挂在哪个类上。`SimulationApp` 只管启动/关闭；进入仿真循环后，时间、步进、回调这些归 `SimulationManager` 管。`SimulationManager` 上还有个配套的 `get_num_physics_steps()` 可以读物理步数。

---

## 问题 14：`stage.GetRootLayer().SaveAs(...)` 报 AttributeError

**现象 / 报错原文**：想把 Stage 保存成 .usda 文件：

```python
stage.GetRootLayer().SaveAs("ch04_mystage.usda")
```

报：

```
AttributeError: 'Layer' object has no attribute 'SaveAs'. Did you mean: 'Save'?
```

照提示改成 `Save("ch04_mystage.usda")` 也不行——`Save()` 不接收文件名参数（它只把层存回自己绑定的文件，而新建的层没有绑定文件，会报错）。

**原因**：两层问题叠加：

1. Isaac Sim 的 USD 库里，`Sdf.Layer` 类**根本没有 `SaveAs` 方法**（报错提示 `Did you mean: 'Save'?` 已经说明）。
2. `stage_utils.create_new_stage()` 创建的舞台，root layer 是**匿名层**（内存里没有对应任何文件，源码 docstring 写着 `Sdf.Find('anon:...usd')`）。匿名层没有"自己的文件名"，`Save()` 无处可写。所以既不能 `SaveAs`，也不能 `Save`。

**解决**：用 `Export("路径")`——把层内容导出到指定文件，不改层本身的绑定，对匿名层正合适：

```python
stage.GetRootLayer().Export("ch04_mystage.usda")
```

已在本机验证：`Export` 成功生成 `ch04_mystage.usda`，用记事本打开是纯文本，能看到 `def Cube "Cube" { double size = 2; double3 xformOp:translate = (0, 0, 3); }`。

**附带说明**：导出的文件里除了你定义的 `/World/Cube`，还会有 `Render`、`OmniverseKit` 等 prim——那是 Kit 启动时自动写进 root layer 的视口渲染配置（分辨率、渲染模式等），不是错误，属于正常现象。

**教训**：新建的 Stage 想"另存为"文件，用 `layer.Export("路径")`。记忆方式：**`Save` 是"存回原文件"（匿名层没有原文件），`Export` 是"导出一份到指定文件"**。新手阶段想保存，用 `Export` 总是对的。

---

## 问题 15：加载自己的机器人 USD，报 "Expected ) ... might not exist"

**现象 / 报错原文**：用 `add_reference_to_stage` 加载自己项目里的机器人模型（如 `panda.usd`），报：

```
pxr.Tf.ErrorException:
Error in '...Sdf_TextFileFormatParser' : 'D:\...\panda.usd:2:18: Expected ) at ', "NewtonArticulationRootAPI", "NewtonMimicAPI")' in </>
```

**原因（生活类比）**：USD 文件就像一封信，每一行都要按固定格式写。这个文件的第 2 行写了个 Python 风格的元组 `("NewtonSceneAPI", "NewtonArticulationRootAPI", "NewtonMimicAPI")`——相当于中文信里突然夹了一行谁也不认识的暗号。读信人（USD 解析器）读到第 2 行第 18 个字符（正好是那个逗号的位置，分毫不差）就停下来喊"这我没法读"。

关键：**报错里的 `文件名:2:18` 是精确导航**——第 2 行第 18 列，直接翻到那个位置看，坏的一目了然。这不是 Isaac Sim 的问题，也不是版本兼容问题，是**文件本身语法非法**（任何版本的 USD 都读不了）。打开一看：这行是生成模型的工具（机器人转 USD 的导出器）直接把"API 名单"当裸元组写出来了；文件其余 96 行全部合法。

**解决**：删掉那一行非法的即可（那行想表达的 API 已经正确地写在各个 prim 上了，纯属冗余坏行）。已实测验证：删掉后文件正常加载。

**根治**：去修生成这个文件的导出工具——不然它每导出一个模型都自带这行病，每个都要手动删。

**教训**：usda 报错自带"行:列"级 GPS。遇到解析报错，第一步就是**打开文件翻到那一行那一列**，肉眼一看真假立辨。这也是第 4 章说"USD 就是纯文本"的最大红利：文件坏了你能自己看、自己修。

---

## 问题 16：Script Editor 报 `NameError: stage_utils` 和 `SyntaxError: '(' was never closed`

**现象 / 报错原文**：把第 6 章"两步加载机器人"的代码抄进 Script Editor 运行，先后撞了两个错：

```
NameError: name 'stage_utils' is not defined          # 第一个错
SyntaxError: '(' was never closed (line 3)            # 第二个错
```

**原因（生活类比）**：两个错，两个经典坑。

1. **`NameError: stage_utils`** = **没带工具箱就开工**。`stage_utils` 是个别名，得先写 `import isaacsim.core.experimental.utils.stage as stage_utils`——这一行相当于告诉 Python"以后我喊 `stage_utils`，指的就是这个工具箱"。没声明就喊，Python 一脸茫然："这名字谁啊？"（当时指南的示例漏了这行 import，已修。）

2. **`SyntaxError: '(' was never closed`** = **说话张嘴不闭嘴**。左括号 `(` 是张嘴，右括号 `)` 是闭嘴。`add_reference_to_stage(` 张了嘴，参数报完，行尾必须 `)` 闭嘴——抄代码时容易盯着参数、漏掉收尾的闭嘴。注意报错指向的是**张嘴的那一行**（line 3），但缺的闭嘴其实在后面某行。多行函数调用是这类笔误的重灾区。

**解决**：补上 import 那行；从报错指向的行开始往下读，数括号：见到 `(` 加一，见到 `)` 减一，数到文件尾还没归零，就是中间哪里漏了闭嘴。VSCode 里把光标放在括号旁边会自动高亮它的配对括号——**没有高亮 = 没配对**，一秒定位。

**教训**：'X' was never closed 这类报错，X 可能是 `(`、`[`、`{`、引号——报错行是"开口"位置，要找的是后面丢失的"闭口"。

---

## 问题 17：`Articulation("/World/Franka_.*")` 报 ValueError（附 dof_paths 套娃结构）

**现象 / 报错原文**：

```
ValueError: Specified paths are invalid. Possible reasons:
 - A regex is used but the stage does not contain any prims matching the regex
Given paths: ['/World/Franka_.*']
Invalid paths: ['/World/Franka_.*']
```

**原因（生活类比）**：正则**搜错了名字**。在通讯录里搜"张_"，可你的联系人叫"张三丰"（`/World/Franka`），他儿子们叫"张三丰/大儿子"（`/World/Franka/panda_joint1` 这种斜杠层级）——**没有任何人叫"张_"开头**。同理：正则 `/World/Franka_.*` 搜的是 `Franka_`（带下划线）开头的路径，而 stage 里只有 `Franka`（无下划线）和 `Franka/xxx`（斜杠），一个都匹配不到 → 直接报错。

**解决**：单台机器人**直接报全名**，不用正则：

```python
artic = Articulation("/World/Franka")   # 官方示例 control_frankas.py 就是这么写的
```

原理：`Articulation` 拿到路径后，会自动在这个 prim **自身和子树里**找贴了 `ArticulationRootAPI`（"脊椎根"标签）的 prim，从那里把整台机器人包起来——子 prim 不用你操心。**正则真正的用途是批量**：挂两台机器人 `/World/Franka_1`、`/World/Franka_2` 时，`/World/Franka_.*` 一次匹配两个挂载点。

**连带的坑：dof_paths 是俄罗斯套娃**。修完正则后打印 DOF 数又发现不对——`artic.dof_paths` 返回的是**嵌套列表**（一个骨架一层套娃，打开才是关节列表）：

```python
len(artic.dof_paths)       # 套娃个数 = 骨架数（单台 = 1）—— 别把这个当 DOF 数！
len(artic.dof_paths[0])    # 打开第一个套娃数关节 = 这台机器人的 DOF 数（Franka = 9）
```

指南原来写 `len(artic.dof_paths)` 打印 9，实际打印 1——就是被套娃坑的。

**教训**：给 `Articulation` 传**挂载路径**，别画蛇添足加正则；读 `dof_paths` 记得它是嵌套结构，先 `[0]` 打开第一层再数。

---

## 问题 18：play() 之前调 `set_dof_position_targets`，报 Invalid DOF type

**现象 / 报错原文**：在 `play()` 之前给关节下目标：

```python
artic.set_dof_position_targets([0, -0.523, 0, -2.094, 0, 1.047, 0, 0.04, 0.04])  # play 之前
```

报：

```
[Warning] Invalid DOF type (DofType.Invalid) at index 8
pxr.Tf.ErrorException: 'ApplyAPI: for multiple apply API schema PhysicsDriveAPI, a non-empty instance name must be provided.'
```

**原因（生活类比）**：物理引擎有**营业时间**。`play()` = 开门营业，`stop()` = 打烊。所有走物理张量的读写——读关节角度（`get_dof_positions`）、设关节目标（`set_dof_position_targets`）——都只在**营业时间内**提供服务。

play 之前去调 `set`，就像商店还没开门就去买东西：店员（DOF 类型查询）还没上班，你问它"这关节是旋转还是平移"（决定用角度驱动还是位移驱动），它答不上来（Invalid），账单开不出来（驱动 API 的实例名为空）→ 当场崩溃。

同根源的另一个坑（问题 17 里顺带发现的）：**stop() 之后再读** `get_dof_positions()`，会报 `physics tensor entity is not valid. Play the simulation to re-initialize it`——打烊了才来，门已经锁了。

**解决**：读写都放在营业时间内：

```python
play()                                # 开门
for _ in range(30):
    update_app()                      # 跑半秒,让物理张量初始化(店员就位)

artic.set_dof_position_targets([...]) # 现在可以下单了
for _ in range(600):
    update_app()                      # 等关节转到位
print(artic.get_dof_positions())      # 营业中,随时可查
stop()                                # 打烊
```

已实测：play 后调用精确到位——目标 `[0, -0.523, 0, -2.094, 0, 1.047, 0, 0.04, 0.04]`，5 秒后实测 `[0.0, -0.521, -0.0, -2.094, -0.0, 1.047, 0.0, 0.04, 0.04]`，分毫不差。

**口诀**：**play 开门，stop 打烊；读写关节，都在营业时间。** 一句话：所有走物理张量的读写，只在"播放中"这个窗口里有效。

**教训**：官方示例 `control_frankas.py` 的顺序就是标准答案——先 `play()`，再在循环里 `set` 和 `get`。拿不准时机时，照官方示例的顺序抄。

---

## 经验总结（防坑要点）

1. **装前先体检**：`nvidia-smi` + 官方 `isaac-sim.compatibility_check.bat`，红绿灯一目了然。
2. **源码 ≠ 程序**：学习用独立包或 PIP，别碰源码构建。
3. **PowerShell 跑当前目录程序加 `.\`**：`.\isaac-sim.bat`、`.\python.bat`。
4. **跑 Isaac Sim 脚本用自带 Python**：`.\python.bat`（Win）/ `./python.sh`（Linux），别用系统 Python。
5. **装完别乱移目录**：移了就让注册表重建（`--reset-user` 或删 Kit 缓存版本目录）。
6. **驱动匹配版本**：低于要求会导致 RTX 渲染起不来（无头却能跑，容易误判）。
7. **分清报错轻重**：启动失败才要紧；`invalid prim`、`libpng`、异步未回收这类是噪音。
8. **首次启动慢是正常的**：着色器编译缓存，5-10 分钟，之后秒开。
9. **字典用冒号，集合用逗号**：`{"headless": False}` 是字典，`{"headless", False}` 是集合。给 `SimulationApp` 这类配置传参，用字典。
10. **资产路径别手写主机名**：引用内置资产一律 `get_assets_root_path() + "/Isaac/..."`，手写 `omniverse://Isaac/...` 会把 `Isaac` 当成不存在的服务器。
11. **SimulationApp 只在独立脚本里用**：Script Editor 已经在运行的 App 里，不写 `SimulationApp(...)`、不写 `while` 主循环，直接操作场景。
12. **方法挂在哪个类上要分清**：启动/关闭归 `SimulationApp`；仿真时间、步进、回调归 `SimulationManager`（`get_simulation_time()`、`get_num_physics_steps()`）。`time.time()` 是真实墙上时钟，不是仿真时间。
13. **新舞台存文件用 `Export`**：`create_new_stage()` 建的是匿名层，没有 `SaveAs` 方法、`Save()` 也无处可写。`layer.Export("路径")` 才是"另存为"的正确姿势。
14. **usda 报错自带行:列级 GPS**：解析报错直接翻到那一行那一列肉眼看——USD 是纯文本，文件坏了能自己看、自己修。生成器产出的坏文件要根治生成端。
15. **括号张嘴要闭嘴**：`'(' was never closed` 的报错行是"开口"位置，缺的"闭口"在后面。VSCode 光标放括号旁看有没有高亮配对，一秒定位。
16. **Articulation 传挂载路径，别加正则**：单台直接 `Articulation("/World/Franka")`，自动向下找骨架根；正则留给多台批量。`dof_paths` 是套娃结构，`[0]` 打开第一层才是关节列表。
17. **物理张量有营业时间**：play 开门，stop 打烊。读关节（`get_dof_positions`）和设目标（`set_dof_position_targets`）都只在播放中有效，play 前设、stop 后读都会崩。
