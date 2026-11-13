# ch06_add_franka.py - 第 6 章：加一个 Franka 机械臂
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless":False})
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.experimental.utils.app import play,stop, update_app
from isaacsim.storage.native import get_assets_root_path

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(
    usd_path = f"{get_assets_root_path()}/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
    path = "/World/Franka"
)

#artic = Articulation("/World/Franka") # 直接传挂载路径,自动向下找骨架根(不要用正则,会报 ValueError)
artic =Articulation("/World/Franka")
#print("骨架数:", len(artic.dof_paths))
print("骨架数：",len(artic.dof_paths))
#print("DOF:", len(artic.dof_paths[0]))   # dof_paths 是嵌套列表,取 [0] 才是这台机器人的 DOF
print("DOF:",len(artic.dof_paths[0]))
#print("关节名：",artic.dof_paths[0])
print("关节名:",artic.dof_paths[0])
play()
for _ in range(30):
    update_app()

# 设关节目标也必须在 play 之后(DOF 类型来自物理引擎张量,播放中才有效;play 前调用会报 Invalid DOF type)
artic.set_dof_position_targets([0,-0.523,0,-2.094,0,1.047,0,0.04,0.04])

for _ in range(600):
    update_app()
# 读角度必须在 play 状态下(stop 后物理张量失效会报错)
print("当前 DOF 位置:",artic.get_dof_positions()) # 每个 DOF 一个值;Franka 全 Revolute,恰好等于各关节角度
stop()
simulation_app.close()