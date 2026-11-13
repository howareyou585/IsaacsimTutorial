# ch03_hello_world.py - 第 3 章：启动 Isaac Sim 并加载默认环境
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})     # 注意：是冒号(字典),不是逗号(集合)

import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.storage.native import get_assets_root_path
from isaacsim.core.experimental.utils.app import play

stage_utils.create_new_stage()                          # 建一个空舞台
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
    path="/World/Environment")                          # 摆进默认环境(地板+灯光)

play()                                                  # 按下"播放",物理开始跑

while simulation_app.is_running():                      # 只要没关窗口
    simulation_app.update()                             # 让仿真转一圈

simulation_app.close()                                  # 打烊
