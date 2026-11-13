# ch03_hello_world.py - 第 3 章：启动 Isaac Sim 并加载默认环境

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})     # 注意：是冒号(字典),不是逗号(集合)

import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.storage.native import get_assets_root_path
stage_utils.create_new_stage()                          # 建一个空的舞台
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
    path="/World/Environment"                           # 摆进一个默认环境（地板 + 灯光）
)
print(f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd")

from isaacsim.core.experimental.utils.app import play
play()

# 实验：打印仿真时间(注意是 SimulationManager,不是 simulation_app)
#from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.core.simulation_manager import SimulationManager
frame = 0
while simulation_app.is_running():
    simulation_app.update()
    frame += 1
    if frame % 60 == 0:   # 每 60 帧打印一次,免得刷屏
        #print(f"仿真时间: {SimulationManager.get_simulation_time():.2f} 秒")
        print(f"仿真时间: {SimulationManager.get_simulation_time():.2f} 秒")

simulation_app.close()
