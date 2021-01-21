from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.geometry import transform_points
from compas.geometry import Transformation

#from compas_ghpython.geometry.xforms import xform_from_transformation
from compas_ghpython.geometry.xforms import xtransformed


def transform_point(p, T):
    return transform_points([p], T)[0]

class Tool(object):
    """
    This is the base class for tools / robot's end-effectors.
    It consists of:
    - geometry (meshes)
    - frame
    - transformation matrix

    TODO:
        - more tcps for one tool!
        - what about a tool with rotating/moving parts?
        - add tool kinematic?
    """

    def __init__(self, tcp_frame):

        self.model = [] #mesh
        self.model_breps = [] #breps

        self.tool0_frame = Frame.worldXY()
        self.tcp_frame = tcp_frame
        
        self.transformation_tool0_tcp = Transformation.from_frame_to_frame(self.tcp_frame, self.tool0_frame)
        self.transformation_tcp_tool0 = Transformation.from_frame_to_frame(self.tool0_frame, self.tcp_frame)

    def load_model(self, xdraw_function=None):
        """Load the geometry (meshes) of the tool.

        Args:
            xdraw_function (function, optional): The function to draw the
                meshes in the respective CAD environment. Defaults to None.
        """
        raise NotImplementedError

    def get_transformed_model(self, transformation):
        """Get the transformed meshes of the tool model.
        Args:
            transformation (:class:`Transformation`): The transformation to
                reach tool0_frame.
        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
        """
        tmodel = []
        for m in self.model:
            tmodel.append(xtransformed(m, transformation))
        return tmodel

    def get_transformed_model_brep(self, transformation):
        """Get the transformed meshes of the tool model.
        Args:
            transformation (:class:`Transformation`): The transformation to
                reach tool0_frame.
        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
        """
        tmodel = []
        for m in self.model_breps:
            tmodel.append(xtransformed(m, transformation))
        return tmodel

    def _get_transformed_model(self, transformation, xtransform_function=None):
        """Get the transformed meshes of the tool model.

        Args:
            transformation (:class:`Transformation`): The transformation to
                reach tool0_frame.
            xform_function (function name, optional): the name of the function
                used to transform the model. Defaults to None.

        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
        """
        tmodel = []
        if xtransform_function:
            for m in self.model:
                tmodel.append(xtransform_function(m, transformation, copy=True))
        else:
            for m in self.model:
                xyz = [(a['x'], a['y'], a['z']) for k, a in m.vertices(True)]
                mtxyz = transform_points(xyz, transformation)
                #mtxyz = transform_points(m.xyz, transformation)
                faces = [m.face_vertices(fkey) for fkey in m.faces()]
                tmodel.append(Mesh.from_vertices_and_faces(mtxyz, faces))
        return tmodel