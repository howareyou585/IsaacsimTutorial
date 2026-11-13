from math import pi
from pxr import Usd,UsdGeom
import numpy as np
robot_name = "Franka"
count = 7

def greet(name, joints):
    print(f"{name} has {joints} joints.")

config = {"headless",False}
joints = ["j1","j2","j3"]

class Robot:
    def __init__(self,name):
        self.name = name

y_true = np.array([80,90,70,85])
y_pred = np.array([78,95,72,80])
mse = np.mean((y_pred-y_true)**2)
print(f"mse = {mse}")
rmse = np.sqrt(mse)
print(f"rmse = {rmse}")

bot = Robot(robot_name)
greet(bot.name,count)
print(f"Config: {config}")
print(f"First joint:{joints[0]}")
print(f"PI = {pi}")

my_robot ={"links":["base","arm"],
           "joints":[
               {"name":"shoulder",
                "dof":1
                }],
            "sendor":[
                {
                    "type":"camera",
                    "resolution":[640,480]
                }]
}
print(my_robot)

stage = Usd.Stage.CreateNew("hello.usda")
#UsdGeom.Define(stage,"/World/Cube")
UsdGeom.Cube.Define(stage, "/World/Cube")        # 在 /World 下定义一个 Cube Prim
stage.GetRootLayer().Save()
print("Save hello.usda")