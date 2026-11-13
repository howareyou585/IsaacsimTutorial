from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless":False})
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.experimental.utils.app import play,stop, update_app
from isaacsim.storage.native import get_assets_root_path

stage_utils.create_new_stage()
stage_utils.add_reference_to_stage(usd_path = f"{get_assets_root_path()}/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
                                   path = "/World/Franka")

# 在 Franka 末端（法兰盘）挂一个相机
from pxr import UsdGeom, Gf
stage = stage_utils.get_current_stage()
camera = UsdGeom.Camera.Define(stage, "/World/Franka/panda_hand/MyCamera")
camera.CreateFocalLengthAttr().Set(24.0)
#camera.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.05))   # 距法兰 5cm(先 Add 创建属性再 Set;注意是 0.05 不是 0.5)
#camera.AddRotateXYZOp().Set(Gf.Vec3d(180, 0, 0))    # 朝下看(实测:-90°只是水平,180° 才朝下)
camera.AddTranslateOp().Set(Gf.Vec3d(0,0,0.05))
camera.AddRotateXYZOp().Set(Gf.Vec3d(-90,0,0))

artic = Articulation("/World/Franka")# 路径必须以 / 开头
#artic = Articulation("/World/Franka")   # 路径必须以 / 开头

play()

for _ in range(30):
    update_app()

#触发渲染并保存图像
#from isaacsim.core.rendering_manager import RenderingManager   # 注意模块名是 rendering_manager(不是 render_manager)
from isaacsim.core.rendering_manager import RenderingManager
RenderingManager.render()
# (简化: 实际需配 render product + replicator writer 导出 PNG, 此处示意)
print("相机prim已经创建，路径：",camera.GetPrim().GetPath())

stop()

simulation_app.close()