from bpy.app.handlers import frame_change_pre, persistent
from bpy.props import BoolProperty, IntProperty, CollectionProperty, PointerProperty
from bpy.types import Panel, PropertyGroup, Object
from bpy.utils import register_class, unregister_class
from mathutils import Vector
from functools import reduce
import bpy

bl_info = {
    'name': 'Copy average location and rotation of last n frames',
    'author': 'gabriel montagné, gabriel@tibas.london',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'description': "Adds a panel in the Objects property where you can select a target object from which to copy the last _n_ frames, averaged out.",
    'warning': "The addon is very simple: the position and rotation is read from the target object's f - curves: so it needs to be animated - - constraint animations, etc. would need to be baked.",
    'tracker_url': 'https://github.com/gabrielmontagne/blender-addon-average-follow-loc-rot',
    'category': 'Object'
}


class FollowPositionProperties(PropertyGroup):
    location = BoolProperty(name="Location", default=False)
    rotation = BoolProperty(name="Rotation", default=False)
    steps = IntProperty(name="Steps",
                        default=3,
                        min=1, max=100
                        )

    target = PointerProperty(name='Target', type=Object)


@persistent
def frame_pre(scene):

    frame = scene.frame_current_final

    for o in scene.objects:

        target = o.follow_position_properties.target
        steps = o.follow_position_properties.steps

        if not target:
            continue

        animation_data = target.animation_data

        if not animation_data:
            continue

        action = animation_data.action

        if not action:
            continue

        if o.follow_position_properties.location:

            x = action.fcurves.find('location', index=0)
            y = action.fcurves.find('location', index=1)
            z = action.fcurves.find('location', index=2)

            if x and y and z:

                positions = [
                    Vector([
                        x.evaluate(frame - offset),
                        y.evaluate(frame - offset),
                        z.evaluate(frame - offset)
                    ])
                    for offset in range(steps)
                ]

                o.location = reduce(lambda x, y: x + y, positions) / steps

        if o.follow_position_properties.rotation:

            x = action.fcurves.find('rotation_euler', index=0)
            y = action.fcurves.find('rotation_euler', index=1)
            z = action.fcurves.find('rotation_euler', index=2)

            if x and y and z:

                positions = [
                    Vector([
                        x.evaluate(frame - offset),
                        y.evaluate(frame - offset),
                        z.evaluate(frame - offset)
                    ])
                    for offset in range(steps)
                ]

                o.rotation_euler = reduce(
                    lambda x, y: x + y, positions) / steps


class FollowPositionPanel(Panel):
    """Panel in the object properties window to link a to the averaged position of a different element"""

    bl_label = "Follow Average Position Link"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout
        target = context.active_object

        row = layout.row()
        row.prop(target.follow_position_properties, 'target')

        row = layout.row()
        row.prop(target.follow_position_properties, 'location')
        row.prop(target.follow_position_properties, 'rotation')
        row.prop(target.follow_position_properties, 'steps')


def register():
    print('Register follow avg position')
    register_class(FollowPositionProperties)
    register_class(FollowPositionPanel)
    Object.follow_position_properties = PointerProperty(
        type=FollowPositionProperties)

    frame_change_pre.clear()
    frame_change_pre.append(frame_pre)


def unregister():
    unregister_class(FollowPositionProperties)
    unregister_class(FollowPositionPanel)
    frame_change_pre.remove(frame_pre)

    del Object.follow_position_properties

if __name__ == '__main__':
    register()
