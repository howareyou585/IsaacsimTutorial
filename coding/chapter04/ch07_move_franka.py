# ch07_move_franka.py - 第 7 章: 让 Franka 摆出抓取姿态
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless":False})

import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.experimental.utils.app import play, stop, update_app
from isaacsim.storage.native import get_assets_root_path
import numpy as np

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(usd_path=f"{get_assets_root_path()}/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd", 
path = '/World/Franka')
artic = Articulation("/World/Franka")
#目标：把机械臂摆成“准备抓取”姿态
deg_targets = [0,-30,0,-120,0,60,0] #臂关节 7个,用度写(直观)
finger_targets = [0.04,0.04]        #手指2个，直接给米(0.04=全张开)
rad_targets = np.deg2rad(deg_targets).tolist() + finger_targets
# 注意: 只对臂关节做 deg2rad! 手指是平移 DOF, 单位是米, 不吃角度转换
play()
arm_pos = artic.get_dof_positions()[0][:7] #前 7 个是臂(弧度)，手指是米， 分开处理
print("初始臂角度(度)：", np.rad2deg(arm_pos))
print("初始手指位置(米)：", artic.get_dof_positions()[0][7:])
artic.set_dof_position_targets(rad_targets) #下达命令
for _ in range(180):
    update_app()

final_pos = artic.get_dof_positions()[0]
print("3秒后臂角度(度):",np.rad2deg(final_pos[:7])) #应接近【0,-30,0,-120,0,60,0】
print("3秒后手指位置(米):",final_pos[7:]) #应接近 0.04(全张开)

stop()
simulation_app.close()
