from __future__ import absolute_import

import math
import os

from compas.datastructures.mesh import Mesh
from compas.geometry import Frame
from compas.geometry import multiply_matrices
from compas.geometry import multiply_matrix_vector
from compas.geometry import subtract_vectors
from compas.geometry import transform_points
from compas.geometry import Rotation
from compas.geometry import Transformation

from ...kinematics import forward_kinematics
from ...kinematics import inverse_kinematics
from compas_fab.robots import Configuration
from .tool import Tool

class UR(object):
    """The UR robot class.
    """

    d1 = 0
    a2 = 0
    a3 = 0
    d4 = 0
    d5 = 0
    d6 = 0

    shoulder_offset = 0
    elbow_offset = 0

    def __init__(self):
        super(UR, self).__init__()

        self.model = []  # a list of meshes
        self.basis_frame = None
        # move to UR !!!!
        self.transformation_RCS_WCS = None
        self.transformation_WCS_RCS = None
        self.set_base(Frame.worldXY())
        self.tool = Tool(Frame.worldXY())
        self.configuration = None

        d1, a2, a3, d4, d5, d6 = self.params

        # j0 - j5 are the axes around which the joints m0 - m5 rotate, e.g. m0
        # rotates around j0, m1 around j1, etc.
        self.j0 = [(0, 0, 0),                 (0, 0, d1)]
        self.j1 = [(0, 0, d1),                (0, -self.shoulder_offset, d1)]
        self.j2 = [(a2, -self.shoulder_offset-self.elbow_offset, d1), (a2, -self.shoulder_offset, d1)]
        self.j3 = [(a2+a3, 0, d1),            (a2+a3,-d4, d1)]
        self.j4 = [(a2+a3, -d4, d1),          (a2+a3, -d4, d1-d5)]
        self.j5 = [(a2+a3, -d4, d1-d5),       (a2+a3, -d4-d6, d1-d5)]

        # check difference ur5 and ur10!!!
        self.tool0_frame = Frame(self.j5[1], [1,0,0], [0,0,1])
        #self.tool0_frame = Frame(self.j5[1], [-1,0,0], [0,0,-1])
        #self.model = self.load_model()


    def set_base(self, base_frame):
        # move to UR !!!! ???
        self.base_frame = base_frame
        # transformation matrix from world coordinate system to robot coordinate system
        self.transformation_WCS_RCS = Transformation.from_frame_to_frame(Frame.worldXY(), self.base_frame)
        # transformation matrix from robot coordinate system to world coordinate system
        self.transformation_RCS_WCS = Transformation.from_frame_to_frame(self.base_frame, Frame.worldXY())
        # modify joint axis !

    def set_tool(self, tool):
        self.tool = tool

    def get_robot_configuration(self):
        raise NotImplementedError

    @property
    def transformation_tool0_tcp(self):
        return self.tool.transformation_tool0_tcp

    @property
    def transformation_tcp_tool0(self):
        return self.tool.transformation_tcp_tool0

    def get_frame_in_RCS(self, frame_WCS):
        """Transform the frame in world coordinate system (WCS) into a frame in
        robot coordinate system (RCS), which is defined by the robots' basis frame.
        """
        frame_RCS = frame_WCS.transformed(self.transformation_WCS_RCS)
        #frame_RCS = frame_WCS.transform(self.transformation_RCS_WCS)
        return frame_RCS

    def get_frame_in_WCS(self, frame_RCS):
        """Transform the frame in robot coordinate system (RCS) into a frame in
        world coordinate system (WCS), which is defined by the robots' basis frame.
        """
        frame_WCS = frame_RCS.transformed(self.transformation_RCS_WCS)
        return frame_WCS

    def get_tool0_frame_from_tcp_frame(self, frame_tcp):
        """Get the tool0 frame (frame at robot) from the tool frame (frame_tcp).
        """
        T = Transformation.from_frame(frame_tcp)
        return Frame.from_transformation(T * self.transformation_tool0_tcp)

    def get_tcp_frame_from_tool0_frame(self, frame_tool0):
        """Get the tcp frame from the tool0 frame.
        """
        T = Transformation.from_frame(frame_tool0)
        return Frame.from_transformation(T * self.transformation_tcp_tool0)

    @property
    def params(self):
        """Get UR specific model parameters.

        Returns:
            (:obj:`list` of :obj:`float`): UR specific model parameters.
        """
        return [self.d1, self.a2, self.a3, self.d4, self.d5, self.d6]

    def get_model_path(self):
        raise NotImplementedError

    def load_model(self, xdraw_function=None):
        """Load the geometry (meshes) of the robot.

        Args:
            xdraw_function (function, ): The function to draw the
                meshes in the respective CAD environment. Defaults to None.
        """
        path = self.get_model_path()

        # the links loaded as meshes
        m0 = Mesh.from_obj(os.path.join(path, 'base_and_shoulder.obj'))
        m1 = Mesh.from_obj(os.path.join(path, 'upperarm.obj'))
        m2 = Mesh.from_obj(os.path.join(path, 'forearm.obj'))
        m3 = Mesh.from_obj(os.path.join(path, 'wrist1.obj'))
        m4 = Mesh.from_obj(os.path.join(path, 'wrist2.obj'))
        m5 = Mesh.from_obj(os.path.join(path, 'wrist3.obj'))

        # draw the geometry in the respective CAD environment
        if xdraw_function:
            m0 = xdraw_function(m0)
            m1 = xdraw_function(m1)
            m2 = xdraw_function(m2)
            m3 = xdraw_function(m3)
            m4 = xdraw_function(m4)
            m5 = xdraw_function(m5)

        self.model = [m0, m1, m2, m3, m4, m5]

    def get_forward_transformations(self, configuration):
        """Calculate the transformations according to the configuration.

        Args:
            configuration (:class:`Configuration`): The robot's configuration.

        Returns:
            transformations (:obj:`list` of :class:`Transformation`): The
                transformations for each link.
        """
        q0, q1, q2, q3, q4, q5 = configuration.values
        j0, j1, j2, j3, j4, j5 = self.j0, self.j1, self.j2, self.j3, self.j4, self.j5

        T0 = Rotation.from_axis_and_angle(subtract_vectors(j0[1], j0[0]), q0, j0[1])
        j1 = transform_points(j1, T0)
        T1 = Rotation.from_axis_and_angle(subtract_vectors(j1[1], j1[0]), q1, j1[1]) * T0
        j2 = transform_points(j2, T1)
        T2 = Rotation.from_axis_and_angle(subtract_vectors(j2[1], j2[0]), q2, j2[1]) * T1
        j3 = transform_points(j3, T2)
        T3 = Rotation.from_axis_and_angle(subtract_vectors(j3[1], j3[0]), q3, j3[1]) * T2
        j4 = transform_points(j4, T3)
        T4 = Rotation.from_axis_and_angle(subtract_vectors(j4[1], j4[0]), q4, j4[1]) * T3
        j5 = transform_points(j5, T4)
        T5 = Rotation.from_axis_and_angle(subtract_vectors(j5[1], j5[0]), q5, j5[1]) * T4

        # now apply the transformation to the base
        T0 = self.transformation_RCS_WCS * T0
        T1 = self.transformation_RCS_WCS * T1
        T2 = self.transformation_RCS_WCS * T2
        T3 = self.transformation_RCS_WCS * T3
        T4 = self.transformation_RCS_WCS * T4
        T5 = self.transformation_RCS_WCS * T5

        return T0, T1, T2, T3, T4, T5

    def get_tool0_transformation(self, T5):
        """Get the transformation to reach tool0_frame.
        """
        return T5 * Transformation.from_frame(self.tool0_frame)

    def get_transformed_tool_frames(self, T5):
        T = self.get_tool0_transformation(T5)
        tool0_frame = Frame.from_transformation(T)
        tcp_frame = Frame.from_transformation(T * self.transformation_tcp_tool0)
        return tool0_frame, tcp_frame

    def get_transformed_model(self, transformations, xtransform_function=None):
        """Get the transformed meshes of the robot model.

        Args:
            transformations (:obj:`list` of :class:`Transformation`): A list of
                transformations to apply on each of the links
            xtransform_function (function name, ): the name of the function
                used to transform the model. Defaults to None.

        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
        """
        tmodel = []
        if xtransform_function:
            for m, T in zip(self.model, transformations):
                tmodel.append(xtransform_function(m, T, copy=True))
        else:
            for m, T in zip(self.model, transformations):
                mtxyz = transform_points(m.xyz, T)
                faces = [m.face_vertices(fkey) for fkey in m.faces()]
                tmodel.append(Mesh.from_vertices_and_faces(mtxyz, faces))
        return tmodel

    def xdraw(self, configuration, xtransform_function=None):
    	"""Get the transformed meshes of the robot and the tool model.

    	Args:
            configuration (:class:`Configuration`): the 6 joint angles in radians
            xtransform_function (function name, ): the name of the function
                used to transform the model. Defaults to None.

        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
    	"""
        transformations = self.get_forward_transformations(configuration)
        tmodel = self.get_transformed_model(transformations, xtransform_function)
        if self.tool:
        	tmodel += self.get_transformed_tool_model(transformations[5], xtransform_function)
        return tmodel


    def get_transformed_tool_model(self, T5, xtransform_function=None):
        """Get the transformed meshes of the tool model.

        Args:
            T5 (:class:`Transformation`): The transformation of the robot's
                last joint.
            xtransform_function (function name, ): the name of the function
                used to transform the model. Defaults to None.

        Returns:
            model (:obj:`list` of :class:`Mesh`): The list of meshes in the
                respective class of the CAD environment
        """
        T = self.get_tool0_transformation(T5)
        return self.tool.get_transformed_model(T, xtransform_function)

    def forward_kinematics(self, configuration):
        """Forward kinematics function.

        Args:
            configuration (:class:`Configuration`): the 6 joint angles in radians

        Returns:
            frame (:class:`Frame`): The tool0 frame in robot coordinate system (RCS).
        """

        return forward_kinematics(configuration.values, self.params)

    def inverse_kinematics(self, tool0_frame_RCS):
        """Inverse kinematics function.
        Args:
            tool0_frame_RCS (:class:`Frame`): The tool0 frame to reach in robot
                coordinate system (RCS).

        Returns:
            configurations (:obj:`list` of :class:`Configuration`): A list
                of possible configurations.
        """
        solutions = inverse_kinematics(tool0_frame_RCS, self.params)
        configurations = []
        for joint_values in solutions:
            configurations.append(Configuration.from_revolute_values(joint_values))
        return configurations
