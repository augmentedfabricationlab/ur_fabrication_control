"""Example: Create robot from URDF.
"""
import compas_fab
from compas.robots import RobotModel
from compas.robots import GithubPackageMeshLoader

#from viewer import RobotArtist
#from viewer import ThreeJsViewer

# repo, package, branch
r = 'ros-industrial/abb'
p = 'abb_irb6600_support'
b = 'kinetic-devel'

# download urdf and meshes from github
loader = GithubPackageMeshLoader(r, p, b)
urdf = loader.load_urdf('irb6640.urdf')

# create robot model from URDF
model = RobotModel.from_urdf_file(urdf)
model.load_geometry(loader)

print(model)

# create robot artist
#artist = RobotArtist(model)