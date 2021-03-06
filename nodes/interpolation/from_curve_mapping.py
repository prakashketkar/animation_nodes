import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from .. container_provider import getHelperMaterial

class InterpolationFromCurveMappingNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InterpolationFromCurveMappingNode"
    bl_label = "Interpolation from Curve Mapping"
    bl_width_default = 200

    curveNodeName = StringProperty(default = "")

    def create(self):
        self.newOutput("Interpolation", "Interpolation", "interpolation")
        self.createCurveNode()

    def draw(self, layout):
        layout.template_curve_mapping(self.curveNode, "mapping", type = "NONE")
        self.invokeFunction(layout, "resetEndPoints", text = "Reset End Points")

    def execute(self):
        mapping = self.mapping
        curve = mapping.curves[3]
        try: curve.evaluate(0.5)
        except: mapping.initialize()
        return curve.evaluate

    def createCurveNode(self):
        material = getHelperMaterial()
        node = material.node_tree.nodes.new("ShaderNodeRGBCurve")
        self.curveNodeName = node.name
        mapping = self.mapping
        mapping.use_clip = True
        mapping.clip_min_y = -0.5
        mapping.clip_max_y = 1.5
        self.resetEndPoints()
        return node

    def removeCurveNode(self):
        material = getHelperMaterial()
        tree = material.node_tree
        curveNode = tree.nodes.get(self.curveNodeName)
        if curveNode is not None:
            tree.nodes.remove(curveNode)
        self.curveNodeName = ""

    def resetEndPoints(self):
        points = self.curve.points
        points[0].location = (0, 0)
        points[-1].location = (1, 1)
        self.mapping.update()

    def duplicate(self, sourceNode):
        self.createCurveNode()
        curvePoints = self.curve.points
        for i, point in enumerate(sourceNode.curve.points):
            if len(curvePoints) == i:
                curvePoints.new(50, 50) # random start position
            curvePoints[i].location = point.location
            curvePoints[i].handle_type = point.handle_type


    def delete(self):
        self.removeCurveNode()

    @property
    def curve(self):
        return self.mapping.curves[3]

    @property
    def mapping(self):
        return self.curveNode.mapping

    @property
    def curveNode(self):
        material = getHelperMaterial()
        node = material.node_tree.nodes.get(self.curveNodeName)
        if node is None: node = self.createCurveNode()
        return node
