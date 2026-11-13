#ch05_falling_cube.py  第 5 章：让 Cube 从空中掉下来
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless":False})
import isaacsim.core.experimental.utils.stage as stage_utils
from   isaacsim.core.experimental.objects import Cube
from   isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from   isaacsim.core.experimental.utils.app import play, stop
from   isaacsim.storage.native import get_assets_root_path


stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(
    usd_path=f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
    path = "/World/Environment"
)

cube = Cube(paths = "/World/MyCube",positions = [(0,3,0)],sizes = 0.5)
GeomPrim(["/World/MyCube"],apply_collision_apis = True)# 给立方体贴"有碰撞"标签

rigid = RigidPrim(["/World/MyCube"]) # 给立方体贴"是刚体"标签
play()
for _ in range(120):
    simulation_app.update()
stop()
positions,orientations = rigid.get_world_poses()
print("2s后 Cube 位置:",positions[0])
simulation_app.close()