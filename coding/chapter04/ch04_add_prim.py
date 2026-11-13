#ch04_add_prim.py
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless":False})

import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdGeom, Sdf

stage = stage_utils.create_new_stage() # 拿一张空白节目单
# 在 /World 路径下定义一个 Cube 类型的 prim
cube_prim = stage.DefinePrim("/World/Cube","Cube")

UsdGeom.Cube(cube_prim).CreateSizeAttr().Set(2.0)
UsdGeom.Cube(cube_prim).AddTranslateOp().Set((0,0,3))

sphere_prim = stage.DefinePrim("/World/MySphere","Sphere")
UsdGeom.Sphere(sphere_prim).CreateRadiusAttr().Set(1.0)
                            
UsdGeom.Sphere(sphere_prim).AddTranslateOp().Set((0,3,0))
           # add_reference_to_stage
stage_utils.add_reference_to_stage(usd_path = f"{get_assets_root_path()}/Isaac/Environments/Grid/default_environment.usd",
                                   path = "/World/Environment")

stage.GetRootLayer().Export("ch04_mystage.usda")# 把节目单存档 没有SaveAs/Save接口
print("Stage 已保存,prim 路径:",cube_prim.GetPath())
simulation_app.close()