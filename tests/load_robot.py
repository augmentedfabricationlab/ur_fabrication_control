"""
Creates a `Robot` representing a UR5 robot from a urdf model and the semantics 
from a srdf file.
"""
import os
import compas
from compas.robots import RobotModel
from compas.robots import LocalPackageMeshLoader
from compas_fab.robots import Robot
from compas_fab.robots import RobotSemantics
from compas_fab.backends import RosClient
# from compas_fab.ghpython import RobotArtist

compas.PRECISION = '12f'

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../data')
PATH = os.path.join(DATA, 'robot_description')

#package = 'ur_description'
package = 'ur_setups'
urdf_filename = os.path.join(PATH, package, "urdf", "ur10_with_measurement_tool.urdf")
srdf_filename = os.path.join(PATH, package, "ur10_with_measurement_tool.srdf")

#package = "abb_linear_axis"
#urdf_filename = os.path.join(PATH, package, "urdf", "abb_linear_axis_brick_suction_tool.urdf")
#srdf_filename = os.path.join(PATH, package, "abb_linear_axis_suction_tool.srdf")

model = RobotModel.from_urdf_file(urdf_filename)

loaders = []
loaders.append(LocalPackageMeshLoader(PATH, "ur_description"))
loaders.append(LocalPackageMeshLoader(PATH, "ur_end_effectors"))
#loaders.append(LocalPackageMeshLoader(PATH, "abb_linear_axis"))
#loaders.append(LocalPackageMeshLoader(PATH, "abb_irb4600_40_255"))
#loaders.append(LocalPackageMeshLoader(PATH, "abb_end_effectors"))
model.load_geometry(*loaders)

artist = None
# artist = RobotArtist(model)

semantics = RobotSemantics.from_srdf_file(srdf_filename, model)

robot = Robot(model, artist, semantics, client=None)
robot.info()
