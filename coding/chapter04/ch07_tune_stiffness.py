# ch07_tune_stiffness.py - 第 7 章调参实验:运行时改刚度(不用碰 USD 文件)
# 用法:python.bat ch07_tune_stiffness.py [刚度值]
#   不带参数 = 默认刚度(400);带参数如 100 = 低刚度组
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.experimental.utils.app import play, stop, update_app
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdPhysics
import sys
import numpy as np

STIFFNESS = float(sys.argv[1]) if len(sys.argv) > 1 else None   # None = 用默认

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
    path="/World/Franka")
artic = Articulation("/World/Franka")

# === 运行时改刚度:加载之后、play 之前 ===
stage = stage_utils.get_current_stage()
joint_prims = [stage.GetPrimAtPath(p) for p in artic.dof_paths[0]]

if STIFFNESS is not None:
    for jp in joint_prims[:7]:   # 只改 7 个臂关节(angular 旋转驱动)
        drive = UsdPhysics.DriveAPI.Get(jp, "angular")
        drive.GetStiffnessAttr().Set(STIFFNESS)
    print(f"已把 7 个臂关节刚度改为 {STIFFNESS}(默认 400)")
else:
    d = UsdPhysics.DriveAPI.Get(joint_prims[0], "angular")
    print("使用默认刚度:", d.GetStiffnessAttr().Get())
# ========================================

# 目标:混合单位——臂(度→弧度) + 手指(直接给米)
deg_targets = [0, -30, 0, -120, 0, 60, 0]
finger_targets = [0.04, 0.04]
rad_targets = np.deg2rad(deg_targets).tolist() + finger_targets

play()
for _ in range(30):                 # 热身 0.5 秒
    update_app()

pos0 = artic.get_dof_positions()[0]
print("初始臂角度(度):", np.rad2deg(pos0[:7]))

artic.set_dof_position_targets(rad_targets)

# 数多少步到位(关节2 误差 < 0.05 rad)
steps = 0
while steps < 600:
    update_app()
    steps += 1
    pos = artic.get_dof_positions()[0].numpy()   # warp 数组先转 numpy 才能单元素索引
    if abs(pos[1] + 0.523) < 0.05:
        break

print(f"关节2 到位步数: {steps}(约 {steps/60:.2f} 秒)")
print("到位臂角度(度):", np.round(np.rad2deg(pos[:7]), 2).tolist())
print("到位手指位置(米):", np.round(pos[7:], 4).tolist())
stop()
simulation_app.close()

# 对比建议:分别跑
#   python.bat ch07_tune_stiffness.py        ← 默认 400
#   python.bat ch07_tune_stiffness.py 100    ← 低刚度,明显变慢变柔
#   python.bat ch07_tune_stiffness.py 4000   ← 高刚度,又快又硬
# 观察窗口里机械臂的动态差别 + 终端打印的到位步数
