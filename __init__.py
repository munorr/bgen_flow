bl_info = {
    "name": "BGEN Flow",
    "author": "Munorr",
    "version": (1, 2, 0),
    "blender": (3, 5, 0),
    "location": "View3D > N",
    "description": "Control parameters from B_GEN geometry node hair system",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy
import os

from . import addon_updater_ops
from bpy.utils import previews
icons = previews.new()
icons.load(
    name='BGEN_FLOW',
    path=os.path.join(os.path.dirname(__file__), "bgen_flow_1080.png"),
    path_type='IMAGE'
)


# [Get node name]
# ============================================================
nodeID_1 = "ID:BGEN_0001"
nodeID_2 = "ID:BGEN_0002"
nodeID_3 = "ID:B-GEN_VtoS_0001"
nodeID_4 = "ID:BV2_VtoS_0001"

bgen_flow_mod_01 = "bgen_flow_hair"
bgen_flow_mod_02 = "bgen_flow_braids"
vts_mod_name_01 = "00_bgen_vts"
stc_mod_name_01 = "00_bgen_stc"
bgen_hair_shader = "Bgen_Hair_Shader"

def vts_nodes():
    vts = []
    for ng in bpy.data.node_groups:
        for node in ng.nodes:
            if node.name == nodeID_4:
                vts.append(ng.name)
    return vts

def get_gNode(obj):
    #obj = bpy.context.active_object
    modName = ""
    nodeTreeName = "<NA base>"
    node_ID = ""
    if obj.modifiers:
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group:
                a = obj.modifiers.get(modifier.name)
                b = obj.modifiers.get(modifier.name).node_group.name
                c = obj.modifiers.get(modifier.name).node_group
                #modName = a
                #nodeTreeName = b
                if c:
                    for node in c.nodes:
                        if node.name == nodeID_1:
                            #print("Node present" , c.name)
                            modName = a
                            nodeTreeName = c.name
                            node_ID = nodeID_1
                            break
                        elif node.name == nodeID_2:
                            #print("Node present" , c.name)
                            modName = a
                            nodeTreeName = c.name
                            node_ID = nodeID_2
                            break
                   
    return modName, nodeTreeName, node_ID

def get_gNode_2(obj):
    #obj = bpy.context.active_object
    vtsMod = ""
    nodeTreeName = "<NA>"
    node_ID = ""
    if obj.modifiers:
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group:
                a = obj.modifiers.get(modifier.name)
                b = obj.modifiers.get(modifier.name).node_group
                if b:
                    for node in b.nodes:
                        if node.name == nodeID_4:
                            vtsMod = a
                            nodeTreeName = b.name
                            node_ID = nodeID_4
                            break

    return vtsMod, nodeTreeName, node_ID

def get_materials():
    mattList = []
    for matt in bpy.data.materials:
        if matt.node_tree:
            #print(matt.node_tree.nodes)
            for node in matt.node_tree.nodes:
                #print(node)
                if node.name == 'ID:bv2_material':
                    #print(matt)
                    mattList.append(matt)
    return mattList

def get_sim_collection():
    simCol = []
    for coll in bpy.data.collections:
        if coll.name[:4] == "SIM=":
            simCol.append(coll)
    return simCol

def is_bgen_sim(obj):
    if obj.type == "MESH":
        if obj.modifiers:
            for modifeir in obj.modifiers:
                if modifeir.type == "CLOTH":
                    return True
            #if get_gNode_2(obj)[2] == nodeID_4:
            #    return True
    
    if obj.type == "CURVES":
        bgenMod = get_gNode(obj)[0]
        if not bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value is None:
            if bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value.name[:4] == "SIM=":
                return True
    
    return False



#==================================================================================================
#                                        [OPERATORS]
#==================================================================================================

class BGEN_OT_single_user_vts(bpy.types.Operator):
    """ Make sim modifier a single user """
    bl_idname = "object.bgen_single_user_vts"
    bl_label = "Make single user"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        vts_ = bpy.data.node_groups[bpy.context.scene.bgen_tools.vts_mod].copy()
        bpy.context.scene.bgen_tools.vts_mod = vts_.name
        return{'FINISHED'}
    
class BGEN_OT_single_user_matt(bpy.types.Operator):
    """ Duplicate bgen Material """
    bl_idname = "object.bgen_single_user_matt"
    bl_label = "Duplicate bgen Material"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mts_ = bpy.data.materials[bpy.context.scene.bgen_tools.matList].copy()
        bpy.context.scene.bgen_tools.matList = mts_.name
        return{'FINISHED'}
    
class BGEN_OT_choose_nodeTree(bpy.types.Operator):
    """ Choose which bgen Node to use"""
    bl_idname = "object.bgen_choose_nodetree"
    bl_label = "Choose bgen Node"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
                
        if get_gNode(active)[2] != nodeID_1 and get_gNode(active)[2] != nodeID_2:
            return False
        return context.mode == "OBJECT", context.mode == "SCULPT_CURVES"
    
    bgen_hair:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_1],
        name="Change Modifier to:",
        description="Select bgen hair modifier",)
    
    bgen_braids:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_2],
        name="Change Modifier to:",
        description="Select bgen braid modifier",)
    
    def execute(self, context):
        obj = bpy.context.active_object
        node_group_name = get_gNode(obj)[0].name
        
        if get_gNode(obj)[2] == nodeID_1:
            obj.modifiers[node_group_name].node_group = bpy.data.node_groups[self.bgen_hair]
        
        if get_gNode(obj)[2] == nodeID_2:
            obj.modifiers[node_group_name].node_group = bpy.data.node_groups[self.bgen_braids]
        
        return{'FINISHED'}

class BGEN_OT_single_user(bpy.types.Operator):
    """ Make BGEN modifier a single user """
    bl_idname = "object.bgen_single_user"
    bl_label = "Make single user"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        
        if get_gNode(active)[2] != nodeID_1 and get_gNode(active)[2] != nodeID_2:
            return False
        return context.mode == "OBJECT", context.mode == "SCULPT_CURVES"
    
    def execute(self, context):
        obj = bpy.context.active_object
        node_group_name = get_gNode(obj)[0].name
        
        obj.modifiers[node_group_name].node_group = obj.modifiers[node_group_name].node_group.copy()
        
        return{'FINISHED'}

class BGEN_OT_add_VTS_mod(bpy.types.Operator):
    """ Add Empty hair curve """
    bl_idname = "object.bgen_add_vts_mod"
    bl_label = "Add Curve Empty Hair"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        if active.type == "MESH":
            if len(active.data.polygons) !=0:
                return False
            
        if active.type != "CURVES" and active.type != "CURVE" and active.type != "MESH":
            return False
        
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        if get_gNode(active)[2] == nodeID_1 or get_gNode(active)[2] == nodeID_2 :
            return False
        return context.mode == "OBJECT"
    
    mod_name: bpy.props.StringProperty(name="Modifier Name", description="Name the new modifier",default="bgen_flow_")
    mod_option: bpy.props.EnumProperty(
        items=(('EXISTING', "Use Existing", "Use existing bgen modifier"),
               ('NEW', "Create New", "Create with new hair modifier")),
        default='EXISTING',)
     
    with_simulation: bpy.props.BoolProperty(name="With Simulation", description="Add simulation with modifier", default= False)

    collision_collection: bpy.props.EnumProperty(
            items=lambda self, context: [(c.name, c.name, "") for c in context.scene.collection.children],
            name="Collision Collection")
    
    hairType: bpy.props.EnumProperty(
        items=(('HAIR', "Hair", "Add Hair node"),
               ('BRAIDS', "Braid", "Add Braid node")),
        default='HAIR',)
    
    
    hair_nodes:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_1],
        name="BGEN Hair Modifiers",
        description="Select bgen modifier",)
    
    braid_nodes:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_2],
        name="BGEN Hair Modifiers",
        description="Select bgen modifier",)
       
    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self) 
    
    def invoke(self, context, event):
        dirpath = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(dirpath,"resources")
        nodelib_path = os.path.join(resource_folder, "bgen_v1_nodes.blend")

        def load_node(nt_name, link=True):
            if not os.path.isfile(nodelib_path):
                return False

            with bpy.data.libraries.load(nodelib_path, link=link) as (data_from, data_to):
                if nt_name in data_from.node_groups:
                    data_to.node_groups = [nt_name]
                    return True
            return False
        
        def load_material(nt_name, link=True):
            if not os.path.isfile(nodelib_path):
                return False

            with bpy.data.libraries.load(nodelib_path, link=link) as (data_from, data_to):
                if nt_name in data_from.materials:
                    data_to.materials = [nt_name]
                    return True
            return False

        if "bgen_nodes" not in bpy.data.node_groups:
            load_node("bgen_nodes", link=False)
            
        if bgen_flow_mod_01 not in bpy.data.node_groups:
            load_node(bgen_flow_mod_01, link=False)
        
        if bgen_flow_mod_02 not in bpy.data.node_groups:
            load_node(bgen_flow_mod_02, link=False)

        if bgen_hair_shader not in bpy.data.materials:
            load_material(bgen_hair_shader, link=False)

        return context.window_manager.invoke_props_dialog(self)
    
    
    
    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        col = layout.column()

        box = col.box()
        col_ = box.column()
        col_.scale_y = 1.2
        row_ = col_.row()
        
        if obj.type == "MESH":
            row_.prop(self,"hairType", expand = True)
            if self.hairType == "HAIR":
                box_ = col_.box()
                col_ = box_.column()
                row1 = col_.row()
                
                row1.prop(self,"mod_option", expand = True)
                if self.mod_option == "EXISTING":
                    
                    col_.prop(self,"with_simulation", text="With Simulation")
                    if self.with_simulation == True:
                        col_.label(text="Collision collection")
                        col_.prop(self,"collision_collection", text="")
                    col_.label(text=" Select Hair Node:")
                    col_.prop(self,"hair_nodes", text="")
                else:
                    col_.prop(self,"with_simulation", text="With Simulation")
                    if self.with_simulation == True:
                        col_.label(text="Collision collection")
                        col_.prop(self,"collision_collection", text="")
                    #col_.label(text=" Select Hair Node:")
                    #col_.prop(self,"hair_nodes", text="")
                    col_.prop(self,"mod_name", text="Mod Name")

            else:
                box_ = col_.box()
                col_ = box_.column()
                row1 = col_.row()
                
                row1.prop(self,"mod_option", expand = True)
                if self.mod_option == "EXISTING":
                    
                    col_.prop(self,"with_simulation", text="With Simulation")
                    if self.with_simulation == True:
                        col_.label(text="Collision collection")
                        col_.prop(self,"collision_collection", text="")
                    col_.label(text=" Select Braid Node:")
                    col_.prop(self,"braid_nodes", text="")
                else:
                    col_.prop(self,"with_simulation", text="With Simulation")
                    if self.with_simulation == True:
                        col_.label(text="Collision collection")
                        col_.prop(self,"collision_collection", text="")
                    #col_.label(text=" Select Braid Node:")
                    #col_.prop(self,"braid_nodes", text="")
                    col_.prop(self,"mod_name", text="Mod Name")

        if obj.type == "CURVES" or obj.type == "CURVE":
            row_.prop(self,"hairType", expand = True)
            if self.hairType == "HAIR":
                row1 = col_.row()
                row1.prop(self,"mod_option", expand = True)
                if self.mod_option == "EXISTING":
                    col_.label(text=" Select Hair Node:")
                    col_.prop(self,"hair_nodes", text="")
                else:
                    col_.prop(self,"mod_name", text="Mod name")
                
            else:
                row1 = col_.row()
                row1.prop(self,"mod_option", expand = True)
                if self.mod_option == "EXISTING":
                    col_.label(text=" Select Braid Node:")
                    col_.prop(self,"braid_nodes", text="")
                else:
                    col_.prop(self,"mod_name", text="Mod name")
     
    def execute(self, context):
        objs = bpy.context.selected_objects

        if self.hairType == "BRAIDS": #If new hair modifier
            if self.mod_option == "NEW":
                ''' Gets the geoNode hair modifier''' 
                for obj in objs:
                    if obj.type == 'MESH':

                        if self.with_simulation == True:
                            get_reset = bpy.data.node_groups.get("00_bgen: reset_strip")
                            reset_mod = obj.modifiers.new(name="reset_modifier", type='NODES')
                            reset_mod.node_group = get_reset
                            bpy.ops.object.convert(target='MESH')

                            get_mod_01 = bpy.data.node_groups.get(vts_mod_name_01)
                            mod_01 = obj.modifiers.new(name="vts_modifier", type='NODES')
                            mod_01.node_group = get_mod_01

                            # Remove all vertex groups from the object
                            for group in obj.vertex_groups:
                                obj.vertex_groups.remove(group)

                            # Add a new vertex group to the object
                            obj.vertex_groups.new(name="Group")

                            mod_02 = obj.modifiers.new(name="Cloth", type='CLOTH')
                            #cloth_modifier = obj.modifiers["Cloth"]    
                            mod_02.settings.vertex_group_mass = "Group"  # Sets Pin group
                            mod_02.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
                            mod_02.collision_settings.distance_min = 0.001
                            mod_02.collision_settings.collection = bpy.data.collections[self.collision_collection]

                            get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_02)
                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = get_mod_03
                            mod_03.node_group = mod_03.node_group.copy()
                            mod_03.node_group.name = self.mod_name
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_69"] = False #Mesh or Curve
                            bgenMod["Input_71"] = True # With Simulation
                        else:
                            get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_02)
                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = get_mod_03
                            mod_03.node_group = mod_03.node_group.copy()
                            mod_03.node_group.name = self.mod_name
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_69"] = False #Mesh or Curve
                            bgenMod["Input_71"] = False # With Simulation

                    else:
                        get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_02)
                        mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                        mod_03.node_group = get_mod_03
                        mod_03.node_group = mod_03.node_group.copy()
                        mod_03.node_group.name = self.mod_name
                        bgenMod = get_gNode(obj)[0]

                        bgenMod["Input_69"] = True #Mesh or Curve
                        bgenMod["Input_71"] = False # With Simulation
                        if obj.type == "CURVE":
                            bgenMod["Input_72"] = False # With Simulation
                        else:
                            bgenMod["Input_72"] = True # With Simulation

            else:
                '''Uses existing one''' 
                for obj in objs:
    
                    if obj.type == 'MESH':
                        
                        if self.with_simulation == True:
                            get_reset = bpy.data.node_groups.get("00_bgen: reset_strip")
                            reset_mod = obj.modifiers.new(name="reset_modifier", type='NODES')
                            reset_mod.node_group = get_reset
                            bpy.ops.object.convert(target='MESH')

                            get_mod_01 = bpy.data.node_groups.get(vts_mod_name_01)
                            mod_01 = obj.modifiers.new(name="vts_modifier", type='NODES')
                            mod_01.node_group = get_mod_01

                            # Remove all vertex groups from the object
                            for group in obj.vertex_groups:
                                obj.vertex_groups.remove(group)

                            # Add a new vertex group to the object
                            obj.vertex_groups.new(name="Group")

                            mod_02 = obj.modifiers.new(name="Cloth", type='CLOTH')
                            #cloth_modifier = obj.modifiers["Cloth"]    
                            mod_02.settings.vertex_group_mass = "Group"  # Sets Pin group
                            mod_02.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
                            mod_02.collision_settings.distance_min = 0.001
                            mod_02.collision_settings.collection = bpy.data.collections[self.collision_collection]

                            mod_03 = obj.modifiers.new(name="bgen_braid_modifier", type='NODES')
                            mod_03.node_group = bpy.data.node_groups[self.braid_nodes]
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_69"] = False #mesh or curve
                            bgenMod["Input_71"] = True #with simulation

                        else:
                            mod_03 = obj.modifiers.new(name="bgen_braid_modifier", type='NODES')
                            mod_03.node_group = bpy.data.node_groups[self.braid_nodes]
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_69"] = False #mesh or curve
                            bgenMod["Input_71"] = False #with simulation
                    else:
                        mod_03 = obj.modifiers.new(name="bgen_braid_modifier", type='NODES')
                        mod_03.node_group = bpy.data.node_groups[self.braid_nodes]
                        bgenMod = get_gNode(obj)[0]

                        bgenMod["Input_69"] = True #mesh or curve
                        bgenMod["Input_71"] = False #with simulation

                        if obj.type == "CURVE":
                            bgenMod["Input_72"] = False # With Simulation
                        else:
                            bgenMod["Input_72"] = True # With Simulation
                    
        else: #IF HAIR
            if self.mod_option == "NEW":
                ''' Gets the geoNode hair modifier''' 
                for obj in objs:
                    if obj.type == 'MESH':
                        
                        if self.with_simulation == True:
                            get_reset = bpy.data.node_groups.get("00_bgen: reset_strip")
                            reset_mod = obj.modifiers.new(name="reset_modifier", type='NODES')
                            reset_mod.node_group = get_reset
                            bpy.ops.object.convert(target='MESH')

                            get_mod_01 = bpy.data.node_groups.get(vts_mod_name_01)
                            mod_01 = obj.modifiers.new(name="vts_modifier", type='NODES')
                            mod_01.node_group = get_mod_01

                            # Remove all vertex groups from the object
                            for group in obj.vertex_groups:
                                obj.vertex_groups.remove(group)

                            # Add a new vertex group to the object
                            obj.vertex_groups.new(name="Group")

                            mod_02 = obj.modifiers.new(name="Cloth", type='CLOTH')
                            #cloth_modifier = obj.modifiers["Cloth"]    
                            mod_02.settings.vertex_group_mass = "Group"  # Sets Pin group
                            mod_02.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
                            mod_02.collision_settings.distance_min = 0.001
                            mod_02.collision_settings.collection = bpy.data.collections[self.collision_collection]

                            get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_01)
                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = get_mod_03
                            mod_03.node_group = mod_03.node_group.copy()
                            mod_03.node_group.name = self.mod_name
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_50"] = False #Mesh or Curve
                            bgenMod["Input_26"] = True # With Simulation
                            bgenMod["Input_47"] = True # Follow Tilt
                            if bgenMod["Input_63"]:
                                bgenMod["Input_63"] = False # Vts or mesh

                        else:
                            get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_01)
                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = get_mod_03
                            mod_03.node_group = mod_03.node_group.copy()
                            mod_03.node_group.name = self.mod_name
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_50"] = False #Mesh or Curve
                            bgenMod["Input_26"] = False # With Simulation
                            bgenMod["Input_47"] = True # Follow Tilt
                    else:
                        get_mod_03 = bpy.data.node_groups.get(bgen_flow_mod_01)
                        mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                        mod_03.node_group = get_mod_03
                        mod_03.node_group = mod_03.node_group.copy()
                        mod_03.node_group.name = self.mod_name
                        bgenMod = get_gNode(obj)[0]

                        bgenMod["Input_50"] = True
                        bgenMod["Input_26"] = False
                        bgenMod["Input_47"] = True # Follow Tilt

                        if obj.type == "CURVE":
                            bgenMod["Input_61"] = False # With Simulation
                        else:
                            bgenMod["Input_61"] = True # With Simulation

            else:
                '''Uses existing one''' 
                for obj in objs:
    
                    if obj.type == 'MESH':
                        
                        if self.with_simulation == True:
                            get_reset = bpy.data.node_groups.get("00_bgen: reset_strip")
                            reset_mod = obj.modifiers.new(name="reset_modifier", type='NODES')
                            reset_mod.node_group = get_reset
                            bpy.ops.object.convert(target='MESH')

                            get_mod_01 = bpy.data.node_groups.get(vts_mod_name_01)
                            mod_01 = obj.modifiers.new(name="vts_modifier", type='NODES')
                            mod_01.node_group = get_mod_01

                            # Remove all vertex groups from the object
                            for group in obj.vertex_groups:
                                obj.vertex_groups.remove(group)

                            # Add a new vertex group to the object
                            obj.vertex_groups.new(name="Group")

                            mod_02 = obj.modifiers.new(name="Cloth", type='CLOTH')
                            #cloth_modifier = obj.modifiers["Cloth"]    
                            mod_02.settings.vertex_group_mass = "Group"  # Sets Pin group
                            mod_02.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
                            mod_02.collision_settings.distance_min = 0.001
                            mod_02.collision_settings.collection = bpy.data.collections[self.collision_collection]

                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = bpy.data.node_groups[self.hair_nodes]
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_50"] = False #Mesh or Curve
                            bgenMod["Input_26"] = True # With Simulation
                            bgenMod["Input_47"] = True # Follow Tilt
                            if bgenMod["Input_63"]:
                                bgenMod["Input_63"] = False # Vts or mesh

                        else:
                            mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                            mod_03.node_group = bpy.data.node_groups[self.hair_nodes]
                            bgenMod = get_gNode(obj)[0]

                            bgenMod["Input_50"] = False #Mesh or Curve
                            bgenMod["Input_26"] = False # With Simulation
                            bgenMod["Input_47"] = True # Follow Tilt
                    else:
                        mod_03 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                        mod_03.node_group = bpy.data.node_groups[self.hair_nodes]
                        bgenMod = get_gNode(obj)[0]

                        bgenMod["Input_50"] = True
                        bgenMod["Input_26"] = False
                        bgenMod["Input_47"] = True # Follow Tilt

                        if obj.type == "CURVE":
                            bgenMod["Input_61"] = False # With Simulation
                        else:
                            bgenMod["Input_61"] = True # With Simulation
            


        return{'FINISHED'}

class BGEN_OT_add_LM_mod(bpy.types.Operator):
    """ Add Empty hair curve """
    bl_idname = "object.bgen_add_lm_mod"
    bl_label = "Add linear mesh mod"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        if active.type == "MESH":
            if len(active.data.polygons) ==0:
                return False
            
        if active.type != "CURVES" and active.type != "CURVE" and active.type != "MESH":
            return False

        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        if active.type == "CURVE" or active.type == "CURVES":
            return False
        if get_gNode(active)[2] == nodeID_1 or get_gNode(active)[2] == nodeID_2 :
            return False
        return context.mode == "OBJECT"
    
    mod_name: bpy.props.StringProperty(name="Modifier Name", description="Name the new modifier",default="bgen_flow_")
    mod_option: bpy.props.EnumProperty(
        items=(('EXISTING', "Use Existing", "Use existing bgen modifier"),
               ('NEW', "Create New", "Create with new hair modifier")),
        default='EXISTING',)
    
    hair_nodes:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_1],
        name="BGEN Hair Modifiers",
        description="Select bgen modifier",)   
       
    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self) 

    def invoke(self, context, event):
        dirpath = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(dirpath,"resources")
        nodelib_path = os.path.join(resource_folder, "bgen_v1_nodes.blend")

        def load_node(nt_name, link=True):
            if not os.path.isfile(nodelib_path):
                return False

            with bpy.data.libraries.load(nodelib_path, link=link) as (data_from, data_to):
                if nt_name in data_from.node_groups:
                    data_to.node_groups = [nt_name]
                    return True
            return False

        def load_material(nt_name, link=True):
            if not os.path.isfile(nodelib_path):
                return False

            with bpy.data.libraries.load(nodelib_path, link=link) as (data_from, data_to):
                if nt_name in data_from.materials:
                    data_to.materials = [nt_name]
                    return True
            return False
        
        if "bgen_nodes" not in bpy.data.node_groups:
            load_node("bgen_nodes", link=False)
            
        if bgen_flow_mod_01 not in bpy.data.node_groups:
            load_node(bgen_flow_mod_01, link=False)
        
        if bgen_hair_shader not in bpy.data.materials:
            load_material(bgen_hair_shader, link=False)
        
        return context.window_manager.invoke_props_dialog(self)
    
    
    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        col = layout.column()

        box = col.box()
        col_ = box.column()
        col_.scale_y = 1.2
        row_ = col_.row()
        
        
        row1 = col_.row()
        row1.prop(self,"mod_option", expand = True)
        if self.mod_option == "EXISTING":
            col_.label(text=" Select Hair Node:")
            col_.prop(self,"hair_nodes", text="")
        else:
            col_.prop(self,"mod_name", text="Mod Name")

        
    def execute(self, context):
        objs = bpy.context.selected_objects

        
        if self.mod_option == "NEW":
            ''' Gets the geoNode hair modifier''' 
            for obj in objs:
                get_mod_01 = bpy.data.node_groups.get(bgen_flow_mod_01)
                mod_01 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                mod_01.node_group = get_mod_01
                mod_01.node_group = mod_01.node_group.copy()
                mod_01.node_group.name = self.mod_name

                bgenMod = get_gNode(obj)[0]

                bgenMod["Input_50"] = False #Mesh or Curve
                bgenMod["Input_26"] = True # With Simulation
                if bgenMod["Input_63"]:
                    bgenMod["Input_63"] = True # Vts or mesh
        else:
            '''Uses existing one''' 
            for obj in objs:
                mod_01 = obj.modifiers.new(name="bgen_hair_modifier", type='NODES')
                mod_01.node_group = bpy.data.node_groups[self.hair_nodes]

                bgenMod = get_gNode(obj)[0]

                bgenMod["Input_50"] = False #Mesh or Curve
                bgenMod["Input_26"] = True # With Simulation
                if bgenMod["Input_63"]:
                    bgenMod["Input_63"] = True # Vts or mesh

        
       


        return{'FINISHED'}
    
class BGEN_OT_remove_bgen_mod(bpy.types.Operator):
    """ Remove bgen hair modifier """
    bl_idname = "object.bgen_remove_hair_mod"
    bl_label = "Removes bgen modifier"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        if get_gNode(active)[2] == nodeID_1 or get_gNode(active)[2] == nodeID_2:
            return True
        else:
            return False

        return context.mode == "OBJECT"
    
    def execute(self, context):
        objs = context.selected_objects
        for obj in objs:
            if obj.modifiers:
                for modifier in obj.modifiers:
                    if get_gNode(obj)[2] == nodeID_1 or get_gNode(obj)[2] == nodeID_2:
                        obj.modifiers.remove(modifier)

        self.report({"INFO"},message="Modifiers deleted")
        return{'FINISHED'}
          
class BGEN_OT_execute_cloth_settings(bpy.types.Operator):
    ''' Executes the settings from the parameters above'''
    bl_label = "EXECUTE SIM VALUES"
    bl_idname = "object.bgen_execute_cloth_settings"
    bl_context = "scene"
    
    def execute(self, context):
        gName = bpy.context.scene.bgen_tools.hair_collection
        root_collection = bpy.data.collections[gName]
        collection_stack = [root_collection]
        collectionKeys = bpy.data.collections.keys()
        
        # Context Values
        quality_Val = bpy.context.scene.bgen_tools.my_int1
        mass_Val = bpy.context.scene.bgen_tools.my_float1
        gravity_Val = bpy.context.scene.bgen_tools.my_float2
        stifTension_Val = bpy.context.scene.bgen_tools.my_float3
        clsnColl = bpy.context.scene.bgen_tools.col_collection
        #pinStiff = bpy.context.scene.bgen_tools.my_float5
        airVis = bpy.context.scene.bgen_tools.my_float6

        frame_start = bpy.context.scene.bgen_tools.sim_start
        frame_end = bpy.context.scene.bgen_tools.sim_end
        
        while collection_stack:
            current_collection = collection_stack.pop()
            for obj in current_collection.objects:
                
                if get_gNode_2(obj)[2] == nodeID_4:
                    vtsMod = get_gNode_2(obj)[0]
                    vtsMod.node_group = bpy.data.node_groups[bpy.context.scene.bgen_tools.vts_mod]
                    if obj.modifiers['Cloth']:
                        cloth_modifier = obj.modifiers["Cloth"]
                        if bpy.context.scene.bgen_tools.simToggle_ == "ON":
                            cloth_modifier.show_viewport = True
                            cloth_modifier.show_render = True
                        if bpy.context.scene.bgen_tools.simToggle_ == "OFF":
                            cloth_modifier.show_viewport = False
                            cloth_modifier.show_render = False
                            
                        cs = cloth_modifier.settings
                        cs.quality = quality_Val
                        cs.mass = mass_Val
                        
                        cs.tension_stiffness = stifTension_Val
                        cs.compression_stiffness = stifTension_Val
                        
                        cs.pin_stiffness = 25
                        cs.effector_weights.all = 1 
                        cs.effector_weights.gravity = gravity_Val
                        cs.air_damping = airVis
                        
                        for clsn in collectionKeys:
                            if clsnColl != clsn:
                                pass
                            else:
                                cloth_modifier.collision_settings.collection = bpy.data.collections[clsnColl]
                        
                        for vg in obj.vertex_groups:
                            obj.vertex_groups.remove(vg)

                        new_vg = obj.vertex_groups.new(name="Group")
                        
                        cloth_modifier.settings.vertex_group_mass = "Group"  # Sets Pin group
                        cloth_modifier.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
                        cloth_modifier.collision_settings.collision_quality = 5
                        cloth_modifier.collision_settings.distance_min = 0.001
                        cloth_modifier.collision_settings.impulse_clamp = 20

                        cloth_modifier.point_cache.frame_start = frame_start
                        cloth_modifier.point_cache.frame_end = frame_end
                    
                for child_collection in current_collection.children:
                    collection_stack.append(child_collection)

        self.report({"INFO"},message="Sim Values EXECUTED")
        return {'FINISHED'}        

def convert_to_mesh(obj,int):
    # Duplicate the object
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()

    # Remove all the modifiers from the duplicated object
    while new_obj.modifiers:
        new_obj.modifiers.remove(new_obj.modifiers[0])

    # Link the duplicated object to the scene and select it
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.collection.objects.link(new_obj)
    bpy.context.view_layer.objects.active = new_obj

    group = bpy.data.node_groups.get("00_bgen: [Resample Curve]")
    mod = new_obj.modifiers.new(name="resample_mod", type='NODES')
    mod.node_group = group
    bpy.data.node_groups["00_bgen: [Resample Curve]"].nodes["ID:resample_curve"].inputs[2].default_value = int
    bpy.ops.object.convert(target='MESH')
    
    return new_obj

class BGEN_OT_create_sim_guides(bpy.types.Operator):
    """Create Simulation Guide"""
    bl_idname = "object.bgen_create_sim_guides"
    bl_label = "Create Sim Guide"
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        if not active.type == "CURVES":
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        
        return context.mode == "OBJECT" 
    '''
    def invoke(self, context, event):
        # Display a popup asking for the collection name
        return context.window_manager.invoke_props_dialog(self)
        '''
    def invoke(self, context, event):
        dirpath = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(dirpath,"resources")
        nodelib_path = os.path.join(resource_folder, "bgen_v1_nodes.blend")

        def load_node(nt_name, link=True):
            if not os.path.isfile(nodelib_path):
                return False

            with bpy.data.libraries.load(nodelib_path, link=link) as (data_from, data_to):
                if nt_name in data_from.node_groups:
                    data_to.node_groups = [nt_name]
                    return True
            return False

        if "bgen_nodes" not in bpy.data.node_groups:
            load_node("bgen_nodes", link=False)
            
        if vts_mod_name_01 not in bpy.data.node_groups:
            load_node(vts_mod_name_01, link=False)
        
        if stc_mod_name_01 not in bpy.data.node_groups:
            load_node(stc_mod_name_01, link=False)

        if "00_bgen: [Resample Curve]" not in bpy.data.node_groups:
            load_node("00_bgen: [Resample Curve]", link=False)
        
        return context.window_manager.invoke_props_dialog(self)
    
    try:
        collision_collection: bpy.props.EnumProperty(
            items=lambda self, context: [(c.name, c.name, "") for c in context.scene.collection.children],
            name="Collision Collection")
        
        resolution : bpy.props.IntProperty(name= "Resolution", soft_min= 0, soft_max= 50, default= (16))
        
        def execute(self, context):
            obj_ = bpy.context.object
            obj_.hide_select = False
            main_obj = obj_.name

            bpy.ops.object.select_all(action='DESELECT')
            
            obj_.select_set(True)
            bpy.context.view_layer.objects.active = obj_
            obj = bpy.context.active_object
            
            convert_to_mesh(obj,self.resolution)  # Used method to convert to mesh
            obj = bpy.context.active_object
            obj.name = "SIM=[" + obj_.name + "]"
            obj_.hide_select = True
            #--------------------------------------------------------------------------
            ''' Gets VTS modifier from resouorce file''' 
            dirpath = os.path.dirname(os.path.realpath(__file__))
            resource_folder = os.path.join(dirpath,"resources")
            nodelib_path = os.path.join(resource_folder, "bgen_v1_nodes.blend")

            with bpy.data.libraries.load(nodelib_path, link=False) as (data_from, data_to):
                data_to.node_groups = [vts_mod_name_01]

            appended_node_tree = data_to.node_groups[0]
            get_mod_01 = appended_node_tree
            mod_01 = obj.modifiers.new(name="geometry_nodes_mod", type='NODES')
            mod_01.node_group = get_mod_01
            mod_01.node_group.name = obj.name
            #--------------------------------------------------------------------------
            mod_02 = obj.modifiers.new(name="Cloth", type='CLOTH')
            # Remove all vertex groups from the object
            for group in obj.vertex_groups:
                obj.vertex_groups.remove(group)

            # Add a new vertex group to the object
            obj.vertex_groups.new(name="Group")
 
            cloth_modifier = obj.modifiers["Cloth"]    
            cloth_modifier.settings.vertex_group_mass = "Group"  # Sets Pin group
            cloth_modifier.collision_settings.vertex_group_object_collisions = "" # Sets Collision group
            cloth_modifier.collision_settings.distance_min = 0.001
            if self.collision_collection == "":
                pass
            else:
                cloth_modifier.collision_settings.collection = bpy.data.collections[self.collision_collection]

            #-------------------------------------------------------------------------------
            if stc_mod_name_01 not in bpy.data.node_groups:
                ''' Gets VTS modifier from resouorce file''' 
                dirpath = os.path.dirname(os.path.realpath(__file__))
                resource_folder = os.path.join(dirpath,"resources")
                nodelib_path = os.path.join(resource_folder, "bgen_v1_nodes.blend")

                with bpy.data.libraries.load(nodelib_path, link=False) as (data_from, data_to):
                    data_to.node_groups = [stc_mod_name_01]

                appended_node_tree = data_to.node_groups[0]
                get_mod_03 = appended_node_tree
                mod_03 = obj.modifiers.new(name="STC_node", type='NODES')
                mod_03.node_group = get_mod_01
            else:
                get_mod_03 = bpy.data.node_groups.get(stc_mod_name_01)
                mod_03 = obj.modifiers.new(name="STC_node", type='NODES')
                mod_03.node_group = get_mod_03

            new_collection = bpy.data.collections.new("")
            bpy.context.scene.collection.children.link(new_collection)
            
            # Add all selected objects to the new collection
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                scene_collection = bpy.context.scene.collection
                
                if obj.users_collection:
                    collection = obj.users_collection[0]
                    collection.objects.unlink(obj)
                
                new_collection.objects.link(obj)
            
            bpy.context.view_layer.objects.active = obj_
            new_collection.name = "SIM=[" + obj_.name + "]"
            #------------------------------------------------------------------------------------
            obj0 = obj_
            bgenMod = get_gNode(obj0)[0]
            nodeTree_name = get_gNode(obj0)[1]

            bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value = new_collection

            if get_gNode(obj_)[2] == nodeID_1:
                bgenMod["Input_62"] = True  
            if get_gNode(obj_)[2] == nodeID_2:
                bgenMod["Input_67"] = True 
            
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='OBJECT')
            new_collection.hide_render = True
            new_collection.hide_viewport = True
            bpy.data.scenes[bpy.context.scene.name].view_layers[bpy.context.view_layer.name].layer_collection.children[new_collection.name].exclude = True
            
            obj_.hide_select = False
            bpy.context.view_layer.objects.active = obj_
            obj_.select_set(True)

            bpy.context.scene.bgen_tools.vts_mod = mod_01.node_group.name
            return {'FINISHED'}
    except:
        pass
        
class BGEN_OT_remove_sim_collection(bpy.types.Operator):
    """ Remove Sim Collection """
    bl_idname = "object.bgen_remove_sim_collection"
    bl_label = "Remove Sim Collection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        if get_gNode(active)[2] == nodeID_1 or get_gNode(active)[2] == nodeID_2:
            return True
        else:
            return False
    
    def execute(self, context):
        obj_ = bpy.context.active_object
        
        if bpy.context.scene.bgen_tools.sim_collection:
            colls = bpy.data.collections[bpy.context.scene.bgen_tools.sim_collection]
            for obj in colls.objects:
                colls.objects.unlink(obj)
                bpy.data.objects.remove(obj)

            bpy.data.collections.remove(colls) 


            bgenMod = get_gNode(obj_)[0]
            if get_gNode(obj_)[2] == nodeID_1:
                bgenMod["Input_62"] = False 
            if get_gNode(obj_)[2] == nodeID_2:
                bgenMod["Input_67"] = False

            bpy.ops.object.editmode_toggle()
            bpy.ops.object.editmode_toggle()

        else:    
            self.report({"ERROR"},message="NO SIM COLLECTIONS")
            return {"CANCELLED"}

        return{'FINISHED'}
   
class BGEN_OT_flip_index_order(bpy.types.Operator):
    """ Reorders the index if order is flipped """
    bl_idname = "object.bgen_flip_index_order"
    bl_label = "Flip index order"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        if not active.type == "MESH":
            return False
        if active.type == "MESH":
            if len(active.data.polygons) !=0:
                return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        
        return context.mode == "OBJECT" 
    
    def execute(self, context):
        objs = context.selected_objects
        #for obj in objs:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.sort_elements(type='REVERSE', elements={'VERT'})
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({"INFO"},message="Index order Flipped")
        return{'FINISHED'}

class BGEN_OT_reset_index_order(bpy.types.Operator):
    """ Resets the index order so index count is linear"""
    bl_idname = "object.bgen_reset_index_order"
    bl_label = "Reset index order"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):

        active = context.active_object
        if active is None:
            return False
        if not active.type == "MESH":
            return False
        if active.type == "MESH":
            if len(active.data.polygons) !=0:
                return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        
        return context.mode == "OBJECT" 
    
    def execute(self, context):
        objs = context.selected_objects
        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            get_reset = bpy.data.node_groups.get("00_bgen: reset_strip")
            reset_mod = obj.modifiers.new(name="reset_modifier", type='NODES')
            reset_mod.node_group = get_reset

            reset_mod_index = obj.modifiers.find(reset_mod.name)
            obj.modifiers.move(reset_mod_index, 0)
            bpy.ops.object.modifier_apply(modifier=reset_mod.name)

            # Remove all vertex groups from the object
            for group in obj.vertex_groups:
                obj.vertex_groups.remove(group)

            # Add a new vertex group to the object
            obj.vertex_groups.new(name="Group")

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report({"INFO"},message="Index order Flipped")
        return{'FINISHED'}

class BGEN_OT_bake_hair_sim(bpy.types.Operator):
    bl_idname = "object.bgen_bake_hair_sim"
    bl_label = "Bake Dynamics"
    bl_description = "Bake all dynamics in the specified collection"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    
    def execute(self, context):
        if context.active_object is not None:
            bgen_tools = context.scene.bgen_tools
            obj_exp = context.object.bgen_expand
            if bgen_tools.pin_obj == True:
                obj = bpy.context.scene.bgen_tools.pinned_obj
            else:
                obj = context.active_object
        else:
                obj = context.active_object

        bgenMod = get_gNode(obj)[0]
        mod_sim_data = bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value.name

        bpy.data.scenes[bpy.context.scene.name].view_layers[bpy.context.view_layer.name].layer_collection.children[mod_sim_data].exclude = False
        bpy.ops.ptcache.bake_all(bake=True)
        bpy.data.scenes[bpy.context.scene.name].view_layers[bpy.context.view_layer.name].layer_collection.children[mod_sim_data].exclude = True
        self.report({"INFO"},message="SIM BAKE FINISHED")
        return {'FINISHED'}

class BGEN_OT_choose_vts_nodeTree(bpy.types.Operator):
    """ Choose which bgen Node to use"""
    bl_idname = "object.bgen_choose_vts_nodetree"
    bl_label = "Choose vts Node"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            return False
        selected_objects = context.selected_objects
        if selected_objects is None:
            return False
        return context.mode == "OBJECT", context.mode == "SCULPT_CURVES"
    
    vts_nodes:bpy.props.EnumProperty(
        items=lambda self, context: [(b.name, b.name, "") for b in bpy.data.node_groups for bn in b.nodes if bn.name == nodeID_4],
        name="Change Modifier to:",
        description="Select bgen modifier",)

    
    def execute(self, context):
        if context.active_object is not None:
            bgen_tools = context.scene.bgen_tools
            obj_exp = context.object.bgen_expand
            if bgen_tools.pin_obj == True:
                obj = bpy.context.scene.bgen_tools.pinned_obj
            else:
                obj = context.active_object
        else:
                obj = context.active_object

        bgenMod = get_gNode(obj)[0]
        if obj.type == "CURVES":
            mod_sim_data = bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value.name
            bpy.data.collections[mod_sim_data].objects[0].modifiers[0].node_group = bpy.data.node_groups[self.vts_nodes]
        else:
            obj.modifiers[0].node_group = bpy.data.node_groups[self.vts_nodes]
        return{'FINISHED'}

#==================================================================================================
#                                      [CUSTOM PROPERTIES]
#==================================================================================================
class BGEN_PT_bgenProperties(bpy.types.PropertyGroup):
    
    mattren: bpy.props.EnumProperty(
        items=(('EEVEE', "Eevee", "Rendered with Eevee"),
               ('CYCLES', "Cycles", "Rendered with Cycles")),
        default='EEVEE')
    
    utilDrawer: bpy.props.EnumProperty(
        items=(('INITIALIZE', "Initialize", "Set up hair Curve"),
               ('DEFORMERS', "Deformers", "Add deformers to hair curve"),
               ('SIMULATION', "Simulation", "Simulate hair curves")),
        default='INITIALIZE')
    
    material_list:bpy.props.EnumProperty(
        items=lambda self, context: [(m.name, m.name, "") for m in get_materials()],
        name="Bgen Materials",
        description="Select Material",)
    
    my_string1 : bpy.props.StringProperty(name= "")
    my_string2 : bpy.props.StringProperty(name= "")
    
    my_int1 : bpy.props.IntProperty(name= "", soft_min= 0, soft_max= 20, default= (5))

    pinned_obj: bpy.props.PointerProperty(name="Pinned Object", type=bpy.types.Object,)

    def set_pin_obj(self, value):
        if value:
            self.pinned_obj = bpy.context.object
        else:
            self.pinned_obj = None
    
    def get_pin_obj(self):
        return self.pinned_obj is not None

    pin_obj : bpy.props.BoolProperty(name="Pin Object", description="Pins active object", default=False, set=set_pin_obj, get=get_pin_obj)
    
    sim_start : bpy.props.IntProperty(name= "", soft_min= 0, soft_max= 4000, default= (1),description="Bake to cache starts from frame ...")
    sim_end : bpy.props.IntProperty(name= "", soft_min= 0, soft_max= 4000, default= (250),description="Bake to cache end in frame ...")

    my_float1 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 20, default= (0.5))
    my_float2 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 1, default= (1))
    my_float3 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 50, default= (15))
    my_float4 : bpy.props.FloatProperty(name= "", soft_min= 0.01, soft_max= 1, default= (.02))
    my_float5 : bpy.props.FloatProperty(name= "", soft_min= 1, soft_max= 50, default= (1)) #Pin Stiffness Value
    my_float6 : bpy.props.FloatProperty(name= "", soft_min= 0, soft_max= 10, default= (1)) # Air Viscusity
    
    my_float_vector : bpy.props.FloatVectorProperty(name= "", soft_min= 0, soft_max= 20, default= (1,1,1))

    my_enum : bpy.props.EnumProperty(
        name= "",
        description= "sample text",
        items= [])
    
    hair_collection:bpy.props.EnumProperty(
        items=lambda self, context: [(c.name, c.name, "") for c in bpy.data.collections],
        name="Hair Collection",
        description="Select the hair collection",)
        
    sim_collection:bpy.props.EnumProperty(
        items=lambda self, context: [(sc.name, sc.name, "") for sc in get_sim_collection()],
        name="Sim Collections",
        description="List of Sim Collections",)

    col_collection:bpy.props.EnumProperty(
        items=lambda self, context: [(c.name, c.name, "") for c in bpy.data.collections],
        name="Collision Collection",
        description="Select the collision collection",)
    
    vts_mod:bpy.props.EnumProperty(
        items=lambda self, context: [(s, s, "") for s in vts_nodes()],
        name="Sim Mod",
        description="Select sim mod",)
        
    simToggle_: bpy.props.EnumProperty(
        items=(('ON', "Sim On", "Turn simulation on"),
               ('OFF', "Sim Off", "Turn simulation off")),
        default='ON')

class BGEN_PT_bgenExpandProp(bpy.types.PropertyGroup):
    
    menu_exp1 : bpy.props.BoolProperty(default=False)
    menu_exp2 : bpy.props.BoolProperty(default=False)
    menu_exp3 : bpy.props.BoolProperty(default=False)
    menu_exp4 : bpy.props.BoolProperty(default=False)
    menu_exp5 : bpy.props.BoolProperty(default=False)
    menu_exp6 : bpy.props.BoolProperty(default=False)
    menu_exp7 : bpy.props.BoolProperty(default=False) #SIM
    menu_exp8 : bpy.props.BoolProperty(default=False) #Bake to Cache Settings
    
    dd_exp1 : bpy.props.BoolProperty(default=False)
    dd_exp2 : bpy.props.BoolProperty(default=False)
    dd_exp3 : bpy.props.BoolProperty(default=False)
    dd_exp4 : bpy.props.BoolProperty(default=False) # Braid FC
    dd_exp5 : bpy.props.BoolProperty(default=False)
    dd_exp6 : bpy.props.BoolProperty(default=False)
    dd_exp7 : bpy.props.BoolProperty(default=False) # WEIGHT PAINT
    dd_exp8 : bpy.props.BoolProperty(default=False) # Sim Values

    expand_settings1 : bpy.props.BoolProperty(default=False)
    expand_settings2 : bpy.props.BoolProperty(default=False)
    
    my_expT1 : bpy.props.BoolProperty(default=False) # Material

    #Sim Settings
    exp_sim1 : bpy.props.BoolProperty(default=False) # Sim Settings
    exp_sim2 : bpy.props.BoolProperty(default=False) # Weight Paint
    exp_sim3 : bpy.props.BoolProperty(default=False) # Sim Values
    exp_sim4 : bpy.props.BoolProperty(default=False) # Collision Settings
    exp_sim5 : bpy.props.BoolProperty(default=False) # Cache settings

#==================================================================================================
#                                        [ADDON DISPLAY]
#==================================================================================================

class BGEN_ui_panel(bpy.types.Panel):
    
    bl_label = " BGEN Flow"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BGEN HAIR"
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon_value=icons["BGEN_FLOW"].icon_id)

    def draw(self, context):
        addon_updater_ops.update_notice_box_ui(self,context)

        if context.active_object is not None:
            bgen_tools = context.scene.bgen_tools
            obj_exp = context.object.bgen_expand
            if bgen_tools.pin_obj == True:
                obj = bpy.context.scene.bgen_tools.pinned_obj
            else:
                obj = context.active_object
        else:
                obj = context.active_object
        
        if obj is None:
            layout = self.layout                
            col = layout.column()
            box = col.box()
            box1 = box.box()
            
            col_nt = box1.column()
            col_nt.scale_y = 1.4
            row_nt = col_nt.row(align = True)
            row_nt.scale_x = 1.2

            row_nt.alignment = "CENTER"
            row_nt.label(text="[Not Applicable]")

            box = col.box()
            col1 = box.column()
            col1.scale_y = 1
            col1.alignment = "CENTER"
            col1.label(text = "No selected Object", icon = "ERROR")

        elif not get_gNode(obj)[2] == nodeID_1 and not get_gNode(obj)[2] == nodeID_2:
            layout = self.layout                
            col = layout.column()
            box = col.box()
            box1 = box.box()
            
            col_nt = box1.column()
            col_nt.scale_y = 1.4
            row_nt = col_nt.row(align = True)
            row_nt.scale_x = 1.2

            row_nt.alignment = "CENTER"
            row_nt.label(text="[Not Applicable]")

            box = col.box()
            col1 = box.column()
            col1.scale_y = 1
            col1.alignment = "CENTER"
            col1.label(text = obj.name, icon = "OBJECT_DATAMODE")

            box1 = box.box()
            col1 = box1.column()
            col1.separator(factor=.3)
            col1.scale_y = 2
            rows = col1.row()
            
            rows.operator("object.bgen_add_vts_mod", text="Add VTS mod", icon = "ADD",depress=True)
            rows.operator("object.bgen_add_lm_mod", text="Add LM mod", icon = "ADD",depress=True)
            
            col1.separator(factor=.5)
            col1.operator("object.bgen_remove_hair_mod", text="Remove bgen mod", icon = "REMOVE")
            col1.separator(factor=.3)

        elif get_gNode(obj)[2] == nodeID_1 or get_gNode(obj)[2] == nodeID_2:
            bgenMod = get_gNode(obj)[0]
            bgenModName = get_gNode(obj)[1]
            bgenNodeID = get_gNode(obj)[2]
            
            layout = self.layout                
            col = layout.column()
            box = col.box()
            box1 = box.box()
            #box1.scale_y = 1.4
            
            #--------------------------------------------------------------------------------------------
            col_nt = box1.column()
            row_nt = col_nt.row(align = True)
            row_nt.scale_x = 1.2
            row_nt.scale_y = 1.4
            if get_gNode(obj)[2] == nodeID_1:
                row_nt.operator_menu_enum("object.bgen_choose_nodetree",'bgen_hair', text="" , icon = "NODETREE")
            if get_gNode(obj)[2] == nodeID_2:
                row_nt.operator_menu_enum("object.bgen_choose_nodetree",'bgen_braids', text="" , icon = "NODETREE")

            mn = bpy.data.node_groups[bgenModName]
            row_nt.prop(mn,"name", text = "",toggle=True, emboss = True)
            row_nt.prop(mn,"use_fake_user", text = "",toggle=True, emboss = True)
            row_nt.operator("object.bgen_single_user", text="", icon = "DUPLICATE" )
            #--------------------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------------------
            row_main = col.row()
            box_s = row_main.box()
            col_s = box_s.column()
            col_s.scale_y = 1

            row_ss = col_s.row()
            row_s = row_ss.row()
            row_s.alignment = "LEFT"
            row_s.label(text = "[" + obj.type + "]", icon = "OBJECT_DATAMODE")
            row_s.label(text = "",icon = "TRIA_RIGHT")
            row_s.label(text = obj.name, icon = "OUTLINER_OB_CURVES")
            row_s.label(text = "",icon = "TRIA_RIGHT")
            
            obj_t = obj.evaluated_get(context.evaluated_depsgraph_get())
            if get_gNode(obj_t)[0]:
                bgenMod_ = get_gNode(obj_t)[0]
                execTime = str(int(bgenMod_.execution_time *1000))
                row_exec = row_s.row()
                row_exec.alignment = "RIGHT"
                row_exec.label(text = execTime + "ms", icon = "PREVIEW_RANGE")

            row_pin = row_ss.row()
            row_pin.alignment = "RIGHT"
            row_pin.prop(bgen_tools, "pin_obj", text="", icon = "PINNED" if bgen_tools.pin_obj else "UNPINNED", icon_only = True, emboss=False)
            #---------------------------------------------------------------------------------------------
            box1 = box_s.box()
            col1 = box1.column()
            col1.separator(factor=.3)
            col1.scale_y = 2
            rows = col1.row()
            rows.operator("object.bgen_add_vts_mod", text="Add VTS mod", icon = "ADD",depress=True)
            rows.operator("object.bgen_add_lm_mod", text="Add LM mod", icon = "ADD",depress=True)
            
            col1.separator(factor=.5)
            col1.operator("object.bgen_remove_hair_mod", text="Remove bgen mod", icon = "REMOVE")
            col1.separator(factor=.3)

            #---------------------------------------------------------------------------------------------

        
            col = layout.column()
            ubox = col.box()
            col = ubox.column(align=False)
            urow = col.row(align=True)
            urow.scale_y = 1.4


            urow.prop(bgen_tools, "utilDrawer",expand = True)
            urow.separator()
            lowPoly_switch_cntr = bpy.data.node_groups[bgenModName].nodes["ID:bgen_lowPoly_switch"].inputs[0]
            lowPoly_switch_node = bpy.data.node_groups[bgenModName].nodes["ID:bgen_lowPoly_switch"]
            lowPoly_switch_cntr.draw(context, urow, lowPoly_switch_node, text = '')

            utilD = bpy.context.scene.bgen_tools.utilDrawer
            
            # INITIALIZE TAB
            if bpy.context.scene.bgen_tools.utilDrawer == "INITIALIZE":
 
                #INITIALIZE
                #--------------------------------------------------------------------------------------------
                matCntr = bpy.data.node_groups[bgenModName].nodes["ID:bv2_MC_001"].inputs[0]
                matNode = bpy.data.node_groups[bgenModName].nodes["ID:bv2_MC_001"]

                lowPoly_switch_cntr = bpy.data.node_groups[bgenModName].nodes["ID:bgen_lowPoly_switch"].inputs[0]
                lowPoly_switch_node = bpy.data.node_groups[bgenModName].nodes["ID:bgen_lowPoly_switch"]

                box = col.box()
                col1 = box.column(align=True)
                row1 = col1.row()
                row1.scale_y = 1.4

                if obj_exp.menu_exp1 == True:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp1",icon="TRIA_DOWN", text="INITIALIZE", emboss=False)
                        #row1.prop(bgenMod, '["Input_63"]', text = 'Low Poly', icon = "RADIOBUT_ON")
                        lowPoly_switch_cntr.draw(context, row1, lowPoly_switch_node, text = 'Low Poly')
                        row1.prop(lowPoly_switch_node.inputs,'Switch')

                        box_ = col1.box()
                        col_ = box_.column()
                        col_.scale_y = 1.4

                        col_.prop(bgenMod, '["Input_30"]', text = 'Attach To')
                        col_.prop(bgenMod, '["Input_31"]', text = 'Attach Amount')

                        row_ = col_.row()
                        row_.operator("object.bgen_flip_index_order", text="Flip Index Order", icon = "FILE_REFRESH",depress=True)
                        row_.operator("object.bgen_reset_index_order", text="Reset Index Order", icon = "FILE_REFRESH",depress=True)

                        

                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp1",icon="TRIA_DOWN", text="INITIALIZE", emboss=False)
                        #row1.prop(bgenMod, '["Input_63"]', text = 'Low Poly', icon = "RADIOBUT_ON")
                        lowPoly_switch_cntr.draw(context, row1, lowPoly_switch_node, text = 'Low Poly')
                        
                        box_ = col1.box()
                        col_ = box_.column()
                        col_.scale_y = 1.4
                        

                        rowt = col_.row(align = False)
                        if bgenMod["Input_69"] == True:
                            rowt.prop(bgenMod, '["Input_69"]', text = 'Mesh',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                            rowt.prop(bgenMod, '["Input_69"]', text = 'Curve',icon = "OUTLINER_OB_CURVES")
                        else:
                            rowt.prop(bgenMod, '["Input_69"]', text = 'Mesh',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                            rowt.prop(bgenMod, '["Input_69"]', text = 'Curve',icon = "OUTLINER_OB_CURVES")

                        col_.prop(bgenMod, '["Input_30"]', text = 'Attach To')
                        col_.prop(bgenMod, '["Input_31"]', text = 'Attach Amount')
                        row_ = col_.row()
                        row_.operator("object.bgen_flip_index_order", text="Flip Index Order", icon = "FILE_REFRESH",depress=True)
                        row_.operator("object.bgen_reset_index_order", text="Reset Index Order", icon = "FILE_REFRESH",depress=True)

                else:
                    row1.prop(obj_exp, "menu_exp1",icon="TRIA_RIGHT", text="INITIALIZE", emboss=False)
                    #row1.prop(bgenMod, '["Input_63"]', text = 'Low Poly', icon = "RADIOBUT_ON")
                    lowPoly_switch_cntr.draw(context, row1, lowPoly_switch_node, text = 'Low Poly')
                
                box = col.box()
                col1 = box.column(align=True)
                row1 = col1.row()
                row1.scale_y = 1.4

                #MATERIAL CONTROL DATA
                #------------------------------------------------------------------------------------------------
                
                mattName = bpy.data.materials[bpy.context.scene.bgen_tools.material_list].name
                mattData = bpy.data.materials[mattName]
                material_nt_data = bpy.data.materials[mattName].node_tree.nodes
                
                #Eevee Material
                emix1Node = bpy.data.materials[mattName].node_tree.nodes['Eevee Mix']
                ecolvar = bpy.data.materials[mattName].node_tree.nodes['Eevee Variation']
                egrad = bpy.data.materials[mattName].node_tree.nodes['Eevee Gradient']
                ebsdf = bpy.data.materials[mattName].node_tree.nodes['Eevee bsdf']
                
                #Cycles Material
                cgrad = bpy.data.materials[mattName].node_tree.nodes['Cycles Gradient']
                cbsdf = bpy.data.materials[mattName].node_tree.nodes['Cycles bsdf']
                ccolvar = bpy.data.materials[mattName].node_tree.nodes['Cycles Variation']
                
                #MATERIAL DRWAWER
                if obj_exp.my_expT1: #MATERIAL DRAWER OPEN
                    row1.prop(obj_exp, "my_expT1",icon="TRIA_DOWN", text="MATERIAL", emboss=False)
                    matCntr.draw(context, row1, matNode, text = '')
                    col_ = col1.column()
                    col_.scale_y = 1.2
                    mbox1 = col_.box()
                    mcol1 = mbox1.column(align = True)
                    mrow1 = mcol1.row(align = True)
                    mrow1.scale_x = 1.1
                    mrow1.scale_y = 1.2
                    
                    mrow_ = col_.row()
                    bgen_tools = context.scene.bgen_tools

                    mrow1.prop(bgen_tools, "material_list", text = "", icon = "MATERIAL", icon_only = True)
                    mts_ = bpy.data.materials[bpy.context.scene.bgen_tools.material_list]
                    mrow1.prop(mts_,"name", text = "",toggle=True, emboss = True)
                    mrow1.operator("object.bgen_single_user_matt", text="", icon = "DUPLICATE")
                    
                    
                    mrow_.prop(bgen_tools, "mattren",expand = True)
                    if bpy.context.scene.bgen_tools.mattren == 'EEVEE':
                        mbox_ = col_.box()
                        mcol_ = mbox_.column()
                        mrow_ = mcol_.row(align = True)
                        mrow_.alignment = "LEFT"
                        mrow_.label(text = "Hair Color:")

                        if 'color_switch_eevee' in material_nt_data:
                            color_switch_eevee = material_nt_data["color_switch_eevee"]
                            mrow_.label(text = "[Leave Value at 0 for bgen_flow]")
                            color_switch_eevee.inputs[0].draw(context, mrow_, color_switch_eevee, text = '')
                            mcol_.template_color_ramp(egrad, "color_ramp",expand = False)
                        else:
                            mcol_.template_color_ramp(egrad, "color_ramp",expand = False)
                        
                        row_ = col_.row(align = False)
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.4
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                        
                        grid_l.label(text = "Color Variation")
                        grid_l.label(text = "            Metalic")
                        grid_l.label(text = "         Specular")
                        grid_l.label(text = "      Roughness")
                        grid_l.label(text = "   Transmission")
                        
                        ecolvar.inputs[7].draw(context, grid_r, ecolvar, text = '')
                        ebsdf.inputs[6].draw(context, grid_r, emix1Node, text = '')
                        ebsdf.inputs[7].draw(context, grid_r, emix1Node, text = '')
                        ebsdf.inputs[9].draw(context, grid_r, emix1Node, text = '')
                        ebsdf.inputs[17].draw(context, grid_r, emix1Node, text = '')
                    
                    if bpy.context.scene.bgen_tools.mattren == 'CYCLES':
                        mbox_ = col_.box()
                        mcol_ = mbox_.column()
                        
                        mcol_.label(text = "Hair Color:")
                        mcol_.template_color_ramp(cgrad, "color_ramp",expand = False)
                        
                        row_ = col_.row(align = False)
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.2
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                        
                        grid_l.label(text = "      Color Variation")
                        grid_l.label(text = "            Roughness")
                        grid_l.label(text = "Radial Roughness")
                        grid_l.label(text = "                        Coat")
                        grid_l.label(text = "Random Roughness")
                        grid_l.label(text = "                           IOR")
                        
                        ccolvar.inputs[7].draw(context, grid_r, ecolvar, text = '')
                        cbsdf.inputs[5].draw(context, grid_r, emix1Node, text = '')
                        cbsdf.inputs[6].draw(context, grid_r, emix1Node, text = '')
                        cbsdf.inputs[7].draw(context, grid_r, emix1Node, text = '')
                        cbsdf.inputs[11].draw(context, grid_r, emix1Node, text = '')
                        cbsdf.inputs[8].draw(context, grid_r, emix1Node, text = '')
                else: #MATERIAL DRAWER CLOSE
                    row1.prop(obj_exp, "my_expT1",icon="TRIA_RIGHT", text="MATERIAL", emboss=False)
                    matCntr.draw(context, row1, matNode, text = '')

            # DEFORMERS TAB
            if bpy.context.scene.bgen_tools.utilDrawer == "DEFORMERS":

                #============================================================================================
                                                #[STRAND CONTROL: BRAIDS]
                #============================================================================================
        
                box = col.box()
                col1 = box.column()
                row1 = col1.row()
                row1.scale_y = 1.4

                if obj_exp.menu_exp2 == True:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp2",icon="TRIA_DOWN", text="STRAND CONTROL", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                        cols = col1.column(align=True)

                        box_ = cols.box()
                        row_ = box_.row(align = False)
                        row_.scale_y = 1.4
                        row_.prop(bgenMod, '["Input_13"]', text = 'Root Width')
                        row_.prop(bgenMod, '["Input_14"]', text = 'Tip Width')

                        box_ = cols.box()
                        col_ = box_.column()
                        row_ = col_.row(align = False)
                        row_.scale_y = 1.2
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.8
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "          Amount")
                        #grid_l.label(text = "           Density")
                        #grid_l.separator()
                        #grid_l.label(text = "     Point Count")
                        #grid_l.label(text = "      Resolution")
                        #grid_l.separator()
                        grid_l.label(text = "Length Variation")
                        
                        grid_r.prop(bgenMod, '["Input_4"]', text = '')
                        #grid_r.prop(bgenMod, '["Input_12"]', text = '')
                        #grid_r.separator()
                        #grid_r.prop(bgenMod, '["Input_11"]', text = '')
                        #grid_r.prop(bgenMod, '["Input_27"]', text = '')
                        #grid_r.separator()
                        grid_r.prop(bgenMod, '["Input_32"]', text = '')

                        if obj_exp.expand_settings1 == True:
                            col_.prop(obj_exp, "expand_settings1",icon="TRIA_DOWN", text="Less settings", emboss=False)
                            
                            row_ = col_.row(align = False)
                            row_.scale_y = 1.2
                            
                            grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                            grid_l.alignment = "RIGHT"
                            grid_l.scale_x = 1.6
                            grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)

                            grid_l.label(text="   Subdivide Mesh")
                            grid_l.label(text="Hair Strand Type:")

                            grid_r.prop(bgenMod, '["Input_22"]', text = '')

                            
                            rowt = grid_r.row(align = True)
                            if bgenMod["Input_55"] == True:
                                rowt.prop(bgenMod, '["Input_55"]', text = 'Tube',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                                rowt.prop(bgenMod, '["Input_55"]', text = 'Strip',icon = "OUTLINER_OB_CURVES")
                            else:
                                rowt.prop(bgenMod, '["Input_55"]', text = 'Tube',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                                rowt.prop(bgenMod, '["Input_55"]', text = 'Strip',icon = "OUTLINER_OB_CURVES")

                        else:
                            col_.prop(obj_exp, "expand_settings1",icon="TRIA_RIGHT", text="More settings", emboss=False)
                    
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp2",icon="TRIA_DOWN", text="STRAND CONTROL", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                        cols = col1.column(align=True)

                        box_ = cols.box()
                        row_ = box_.row(align = False)
                        row_.scale_y = 1.4
                        row_.prop(bgenMod, '["Input_14"]', text = 'Root Width')
                        row_.prop(bgenMod, '["Input_15"]', text = 'Tip Width')

                        box_ = cols.box()
                        col_ = box_.column()
                        row_ = col_.row(align = False)
                        row_.scale_y = 1.2
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.8
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "          Amount")
                        grid_l.label(text = "      Resolution")
                        grid_l.label(text = "Length Variation")
                        
                        grid_r.prop(bgenMod, '["Input_7"]', text = '')
                        grid_r.prop(bgenMod, '["Input_6"]', text = '')
                        grid_r.prop(bgenMod, '["Input_40"]', text = '')

                        if obj_exp.expand_settings1 == True:
                            col_.prop(obj_exp, "expand_settings1",icon="TRIA_DOWN", text="Less settings", emboss=False)
                            
                            row_ = col_.row(align = False)
                            row_.scale_y = 1.2
                            
                            grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                            grid_l.alignment = "RIGHT"
                            grid_l.scale_x = 1.6
                            grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)

                            grid_l.label(text="Hair Strand Type:")
         
                            rowt = grid_r.row(align = True)
                            if bgenMod["Input_70"] == True:
                                rowt.prop(bgenMod, '["Input_70"]', text = 'Tube',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                                rowt.prop(bgenMod, '["Input_70"]', text = 'Strip',icon = "OUTLINER_OB_CURVES")
                            else:
                                rowt.prop(bgenMod, '["Input_70"]', text = 'Tube',invert_checkbox=True,icon = "OUTLINER_OB_CURVES")
                                rowt.prop(bgenMod, '["Input_70"]', text = 'Strip',icon = "OUTLINER_OB_CURVES")

                        else:
                            col_.prop(obj_exp, "expand_settings1",icon="TRIA_RIGHT", text="More settings", emboss=False)
                
                else:
                    row1.prop(obj_exp, "menu_exp2",icon="TRIA_RIGHT", text="STRAND CONTROL", emboss=False)
                    row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                
                #============================================================================================
                                                #[BRAID or DISPLACEMENT CONTROL: BRAIDS]
                #============================================================================================
                
                box = col.box()
                col1 = box.column(align = True)
                row1 = col1.row()
                row1.scale_y = 1.4
                
                if obj_exp.menu_exp3 == True:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp3",icon="TRIA_DOWN", text="DISPLACEMENT", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                        box_ = col1.box()
                        col_ = box_.column(align = True)
                        #row_ = col_.row(align = False)
                        col_.scale_y = 1.4
                        
                        #row_.prop(bgenMod, '["Input_21"]', text = 'Flat Hair',icon="IPO_LINEAR")
                        col_.prop(bgenMod, '["Input_47"]', text = 'Follow Tilt',icon="CON_FOLLOWPATH")
                        if obj.modifiers[bgenMod.name]["Input_47"] == True:
                            col_.prop(bgenMod, '["Input_46"]', text = 'Tilt Rotation',icon="CON_FOLLOWPATH")

                        box_ = col1.box()
                        col_ = box_.column()
                        row_ = col_.row(align = False)
                        row_.scale_y = 1.2
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.4
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "Displacement X")
                        grid_l.label(text = "                        Y")
                        grid_l.label(text = "                        Z")

                        
                        grid_r.prop(bgenMod, '["Input_7"]', text = '')
                        grid_r.prop(bgenMod, '["Input_24"]', text = '')
                        grid_r.prop(bgenMod, '["Input_28"]', text = '')

                        
                        # ========== Drop Down (4) ========== #
                        boxdd = col1.box()
                        coldd = boxdd.column()
                        rowdd = col1.row()
                        if obj_exp.dd_exp4 == True:
                            coldd.prop(obj_exp, "dd_exp4",icon="TRIA_DOWN", text="CLUMP PROFILE", emboss=False)
                            floatCurve = bpy.data.node_groups[bgenModName].nodes['Clump Profile']
                            floatCurve.draw_buttons_ext(context, coldd)
                        else:
                            coldd.prop(obj_exp, "dd_exp4",icon="TRIA_RIGHT", text="CLUMP PROFILE", emboss=False)
                        
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp3",icon="TRIA_DOWN", text="BRAID CONTROL", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                        box_ = col1.box()
                        col_ = box_.column()
                        row_ = box_.row(align = False)
                        row_.scale_y = 1.2
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.2
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "        Frequency")
                        grid_l.label(text = "      Braid Width")
                        grid_l.label(text = "Braid Thickness")
                        grid_l.label(text = "  Braid Rotation")
                        grid_l.separator()
                        grid_l.label(text = "     Unravel Top")
                        grid_l.label(text = " Unravel Bottom")
                        
                        grid_r.prop(bgenMod, '["Input_4"]', text = '')
                        grid_r.prop(bgenMod, '["Input_9"]', text = '')
                        grid_r.prop(bgenMod, '["Input_8"]', text = '')
                        grid_r.prop(bgenMod, '["Input_16"]', text = '')
                        grid_r.separator()
                        grid_r.prop(bgenMod, '["Input_64"]', text = '')
                        grid_r.prop(bgenMod, '["Input_65"]', text = '')
                        
                        # ========== Drop Down (4) ========== #
                        boxdd = col1.box()
                        coldd = boxdd.column()
                        rowdd = col1.row()
                        if obj_exp.dd_exp4 == True:
                            coldd.prop(obj_exp, "dd_exp4",icon="TRIA_DOWN", text="BRAID PROFILE", emboss=False)
                            floatCurve = bpy.data.node_groups[bgenModName].nodes['Braid Profile']
                            floatCurve.draw_buttons_ext(context, coldd)
                        else:
                            coldd.prop(obj_exp, "dd_exp4",icon="TRIA_RIGHT", text="BRAID PROFILE", emboss=False)
                        
                else:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp3",icon="TRIA_RIGHT", text="DISPLACEMENT", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                    
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp3",icon="TRIA_RIGHT", text="BRAID CONTROL", emboss=False)
                        row1.label(text = "", icon = "OUTLINER_OB_CURVES")
                    
                #============================================================================================
                                                #[CURL CONTROL: BRAIDS]
                #============================================================================================
                
                box = col.box()
                col1 = box.column(align = True)
                row1 = col1.row()
                row1.scale_y = 1.4
                
                if obj_exp.menu_exp4 == True:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp4",icon="TRIA_DOWN", text="CURL CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_51"]', text = '')
                        box_ = col1.box()
                        col_ = box_.column()
                        
                        row_ = box_.row(align = False)
                        row_.scale_y = 1.2
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.8
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        #grid_l.label(text = "        Curl Path")
                        #grid_l.separator()
                        grid_l.label(text = "Curl Frequency")
                        grid_l.label(text = "    Curl Radius")
                        grid_l.label(text = "  Random Offset")
                        
                        #grid_r.prop(bgenMod, '["Input_52"]', text = '')
                        #grid_r.separator()
                        grid_r.prop(bgenMod, '["Input_16"]', text = '')
                        grid_r.prop(bgenMod, '["Input_10"]', text = '')
                        grid_r.prop(bgenMod, '["Input_56"]', text = '')
                        
                        # ========== Drop Down (4) ========== #
                        boxdd = col1.box()
                        coldd = boxdd.column()
                        rowdd = col1.row()
                        if obj_exp.dd_exp3 == True:
                            coldd.prop(obj_exp, "dd_exp3",icon="TRIA_DOWN", text="CURL PROFILE", emboss=False)
                            floatCurve = bpy.data.node_groups[bgenModName].nodes['Curl Profile']
                            floatCurve.draw_buttons_ext(context, coldd)
                        else:
                            coldd.prop(obj_exp, "dd_exp3",icon="TRIA_RIGHT", text="CURL PROFILE", emboss=False)
                    
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp4",icon="TRIA_DOWN", text="CURL CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_68"]', text = '')
                        box_ = col1.box()
                        col_ = box_.column()
                        
                        row_ = box_.row(align = False)
                        row_.scale_y = 1.2
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.2
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "        Curl Path")
                        grid_l.label(text = "Curl Frequency")
                        grid_l.label(text = "    Curl Radius")
                        
                        grid_r.prop(bgenMod, '["Input_66"]', text = '')
                        grid_r.prop(bgenMod, '["Input_24"]', text = '')
                        grid_r.prop(bgenMod, '["Input_25"]', text = '')
                        
                        # ========== Drop Down (4) ========== #
                        boxdd = col1.box()
                        coldd = boxdd.column()
                        rowdd = col1.row()
                        if obj_exp.dd_exp3 == True:
                            coldd.prop(obj_exp, "dd_exp3",icon="TRIA_DOWN", text="CURL PROFILE", emboss=False)
                            floatCurve = bpy.data.node_groups[bgenModName].nodes['Curl Profile']
                            floatCurve.draw_buttons_ext(context, coldd)
                        else:
                            coldd.prop(obj_exp, "dd_exp3",icon="TRIA_RIGHT", text="CURL PROFILE", emboss=False)
                        
                else:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp4",icon="TRIA_RIGHT", text="CURL CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_51"]', text = '')
                    
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp4",icon="TRIA_RIGHT", text="CURL CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_68"]', text = '')
                
                #============================================================================================
                                                #[ROOT / NOISE CONTROL: BRAIDS]
                #============================================================================================
                
                box = col.box()
                col1 = box.column()
                row1 = col1.row()
                row1.scale_y = 1.4
                
                if obj_exp.menu_exp5 == True:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp5",icon="TRIA_DOWN", text="NOISE CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_54"]', text = '')
                        box_ = col1.box()
                        col_ = box_.column()
                        col_.scale_y = 1.2
                        row_ = col_.row(align = False)
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.6
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "Noise Level")
                        grid_l.label(text = "Noise Radius")
                        grid_l.separator()
                        grid_l.label(text = "FA Amount")
                        grid_l.label(text = "FA Displacement")
                        grid_l.label(text = "FA Seed")
                        
                        grid_r.prop(bgenMod, '["Input_9"]', text = '')
                        grid_r.prop(bgenMod, '["Input_29"]', text = '')
                        grid_r.separator()
                        grid_r.prop(bgenMod, '["Input_58"]', text = '')
                        grid_r.prop(bgenMod, '["Input_59"]', text = '')
                        grid_r.prop(bgenMod, '["Input_60"]', text = '')


                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp5",icon="TRIA_DOWN", text="ROOT CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_44"]', text = '')
                        box_ = col1.box()
                        col_ = box_.column()
                        col_.scale_y = 1.1
                        row_ = col_.row(align = False)
                        
                        grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        grid_l.alignment = "RIGHT"
                        grid_l.scale_x = 1.6
                        grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                        
                        grid_l.label(text = "   Root Path")
                        grid_l.label(text = "      Amount")
                        grid_l.separator()
                        grid_l.label(text = "Displace X")
                        grid_l.label(text = "                Y")
                        grid_l.label(text = "                Z")
                        
                        grid_r.prop(bgenMod, '["Input_45"]', text = '')
                        grid_r.prop(bgenMod, '["Input_46"]', text = '')
                        grid_r.separator()
                        grid_r.prop(bgenMod, '["Input_47"]', text = '')
                        grid_r.prop(bgenMod, '["Input_48"]', text = '')
                        grid_r.prop(bgenMod, '["Input_49"]', text = '')
                        
                else:
                    if get_gNode(obj)[2] == nodeID_1:
                        row1.prop(obj_exp, "menu_exp5",icon="TRIA_RIGHT", text="NOISE CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_54"]', text = '')
                    
                    if get_gNode(obj)[2] == nodeID_2:
                        row1.prop(obj_exp, "menu_exp5",icon="TRIA_RIGHT", text="ROOT CONTROL", emboss=False)
                        row1.prop(bgenMod, '["Input_44"]', text = '')
                
                #--------------------------------------------------------------------------------------------
                    
            # SIMULATION TAB
            if bpy.context.scene.bgen_tools.utilDrawer == "SIMULATION":
                #============================================================================================
                                                        #[SIM SETTINGS]
                #============================================================================================
                if obj.type == "CURVES":
                    #----------------------------------------------------------------------------------------------------------------
                    col = col.column(align=True)
                    boxsg = col.box()
                    rowsg = boxsg.row(align = True)
                    boxsg_l = rowsg.box()
                    cols = boxsg_l.column(align = True)
                    cols.scale_y = 1.4
                    cols.operator("object.bgen_create_sim_guides", text="Create Sim Guides", icon = "FORCE_WIND", depress = True)
                    
                    scrow = cols.row(align = True)
                    scrow.scale_x = 1.2
                    scrow.prop(bgen_tools, "sim_collection", text = "", icon = "COLLECTION_COLOR_05")
                    scrow.operator("object.bgen_remove_sim_collection", text="", icon = "CANCEL")
                    #------------------------------------------------------------------------------------
                    boxsg_l = rowsg.box()
                    sgCol = boxsg_l.column(align = True)
                    sgCol.scale_x = 1.2 
                    sgCol.scale_y = 1.4  

                    if get_gNode(obj)[2] == nodeID_1 or get_gNode(obj)[2] == nodeID_2:
                        collCntr = bpy.data.node_groups[bgenModName].nodes["ID:bgen_CC_001"].inputs[1]
                        collNode = bpy.data.node_groups[bgenModName].nodes["ID:bgen_CC_001"] 
                        
                        sgCol.prop(bgenMod, '["Input_67"]', text = 'Use Sim Guides',icon = "OUTLINER_OB_CURVES",expand=True)
                        collCntr.draw(context, sgCol, collNode, text = '')
                    #----------------------------------------------------------------------------------------------------------------

                if is_bgen_sim(obj):
                    col = layout.column(align=True)
                    ubox = col.box()
                    col = ubox.column()

                    if obj.type == "CURVES":
                        box = col.box()
                        vcol = box.column()
                        vcol.scale_x = 1.6
                        vcol.scale_y = 1.8
                        vrow = vcol.row(align = True)

                        mod_sim_data = bgenMod.node_group.nodes["ID:bgen_CC_001"].inputs[1].default_value.name
                        sim_obj_vts = bpy.data.collections[mod_sim_data].objects[0].modifiers[0].node_group
                        sim_obj_data = bpy.data.collections[mod_sim_data].objects[0].modifiers["Cloth"]

                        vrow.operator_menu_enum("object.bgen_choose_vts_nodetree",'vts_nodes', text="" , icon = "NODETREE")
                        vrow.prop(sim_obj_vts,"name", text = "",toggle=True, emboss = True)
                        vrow.prop(sim_obj_vts,"use_fake_user", text = "",toggle=True, emboss = True)
                        vrow.operator("object.bgen_single_user_vts", text="", icon = "DUPLICATE")
                    else:
                        if get_gNode_2(obj)[2] == nodeID_4:
                            box = col.box()
                            vcol = box.column()
                            vcol.scale_x = 1.6
                            vcol.scale_y = 1.8
                            vrow = vcol.row(align = True)

                            sim_obj_vts = get_gNode_2(obj)[0].node_group
                            sim_obj_data = obj.modifiers["Cloth"]

                            vrow.operator_menu_enum("object.bgen_choose_vts_nodetree",'vts_nodes', text="" , icon = "NODETREE")
                            vrow.prop(sim_obj_vts,"name", text = "",toggle=True, emboss = True)
                            vrow.prop(sim_obj_vts,"use_fake_user", text = "",toggle=True, emboss = True)
                            vrow.operator("object.bgen_single_user_vts", text="", icon = "DUPLICATE")
                        else:
                            sim_obj_data = obj.modifiers["Cloth"]

                    

                    boxSv = col.box()
                    colSv = boxSv.column(align = True)
                    colSv.scale_y = 1.2
                    rowSv = colSv.row(align = True)
                    rowSv.scale_x = 1.2
                    
                    if obj_exp.exp_sim1: #Sim Settings
                        rowSv.prop(obj_exp, "exp_sim1",icon="TRIA_DOWN", text="Simulation Settings", emboss=False)
                        rowSv.prop(sim_obj_data, "show_viewport", text = "")
                        rowSv.prop(sim_obj_data, "show_render", text = "")

                        boxss = colSv.box()
                        colss = boxss.column(align = False)
                        colss.scale_y = 1
                        rowss = colss.row(align = True)
                        rowss.scale_x = 1.2
                        rowss.alignment = "LEFT"

                        if obj_exp.exp_sim2: # Weight Paint
                            rowss.prop(obj_exp, "exp_sim2",icon="DOWNARROW_HLT", text="Weigth Paint", emboss=False)
                            if get_gNode_2(obj)[2] == nodeID_4:
                                fc_wp = bpy.data.node_groups[sim_obj_vts.name].nodes['Vertex_Paint_FC'] 
                                fc_wp.draw_buttons_ext(context, colss)
                            else:
                                if obj.type == "CURVES":
                                    fc_wp = bpy.data.node_groups[sim_obj_vts.name].nodes['Vertex_Paint_FC'] 
                                    fc_wp.draw_buttons_ext(context, colss)
                                else:
                                    colss.label(text = "[VTS NODE NOT AVIALABLE]")
                        else:
                            
                            rowss.prop(obj_exp, "exp_sim2",icon="RIGHTARROW", text="Weigth Paint", emboss=False)

                        boxss = colSv.box()
                        colss = boxss.column(align = False)
                        colss.scale_y = 1
                        rowss = colss.row(align = True)
                        rowss.scale_x = 1.2
                        rowss.alignment = "LEFT"
                        if obj_exp.exp_sim3: #Sim Values
                            rowss.prop(obj_exp, "exp_sim3",icon="DOWNARROW_HLT", text="Sim Values", emboss=False)
                            row_ = colss.row()
                            row_.scale_y = 1.2
                            grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                            grid_l.alignment = "RIGHT"
                            grid_l.scale_x = 1.8
                            grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=False)
                                
                            grid_l.label(text = "      Quality")
                            grid_l.label(text = "Air Viscusity")
                            grid_l.label(text = "         Mass")
                            grid_l.label(text = "      Gravity")
                            grid_l.label(text = "      Tension")

                            grid_r.prop(sim_obj_data.settings, "quality", text = "")
                            grid_r.prop(sim_obj_data.settings, "air_damping", text = "")
                            grid_r.prop(sim_obj_data.settings, "mass", text = "")
                            grid_r.prop(sim_obj_data.settings.effector_weights, "gravity", text = "")
                            grid_r.prop(sim_obj_data.settings, "tension_stiffness", text = "")
                        else:
                            rowss.prop(obj_exp, "exp_sim3",icon="RIGHTARROW", text="Sim Values", emboss=False)

                        boxss = colSv.box()
                        colss = boxss.column(align = False)
                        colss.scale_y = 1
                        rowss = colss.row(align = True)
                        rowss.scale_x = 1.2
                        rowss.alignment = "LEFT"
                        if obj_exp.exp_sim4: #Collision Settings
                            rowss.prop(obj_exp, "exp_sim4",icon="DOWNARROW_HLT", text="Collision Settings", emboss=False)
                            row_ = colss.row(align = False)

                            grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                            grid_l.alignment = "RIGHT"
                            grid_l.scale_x = 1.6
                            grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)

                            grid_l.label(text = "Collision Collection")

                            grid_r.prop(sim_obj_data.collision_settings, "collection", text = "")
                        else:
                            rowss.prop(obj_exp, "exp_sim4",icon="RIGHTARROW", text="Collision Settings", emboss=False)


                        boxss = colSv.box()
                        colss = boxss.column(align = False)
                        colss.scale_y = 1
                        rowss = colss.row(align = True)
                        rowss.scale_x = 1.2
                        rowss.alignment = "LEFT"
                        if obj_exp.exp_sim5: # Bake Cache Settings
                            rowss.prop(obj_exp, "exp_sim5",icon="DOWNARROW_HLT", text="Bake to Cache Settings", emboss=False)
                            row_ = colss.row(align = False)

                            grid_l = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)
                            grid_l.alignment = "RIGHT"
                            grid_l.scale_x = 1.6
                            grid_r = row_.grid_flow(row_major=False, columns=1, even_columns=False, even_rows=False, align=True)

                            grid_l.label(text = "Simulation Start")
                            grid_l.label(text = "               End")
                            grid_l.label(text = "")
                            
                            grid_r.prop(sim_obj_data.point_cache, "frame_start", text = "")
                            grid_r.prop(sim_obj_data.point_cache, "frame_end", text = "")
                            grid_r.prop(sim_obj_data.point_cache, "use_disk_cache", text = "Use Disk Cache")

                            colss.prop(sim_obj_data.point_cache, "info", text = "")
                            rowss = colss.row()
                            rowss.scale_y = 1.4
                            rowss.operator("object.bgen_bake_hair_sim",text="Bake all Physics")

                            if sim_obj_data.point_cache.is_baked == True:
                                rowss.operator("ptcache.free_bake_all",depress=True)
                            else:
                                rowss.operator("ptcache.free_bake_all",depress=False)
                        else:
                            rowss.prop(obj_exp, "exp_sim5",icon="RIGHTARROW", text="Bake to Cache Settings", emboss=False)

                    else:
                        rowSv.prop(obj_exp, "exp_sim1",icon="TRIA_RIGHT", text="Simulation Settings", emboss=False)
                        rowSv.prop(sim_obj_data, "show_viewport", text = "")
                        rowSv.prop(sim_obj_data, "show_render", text = "") 
                else:
                    boxns = col.box()
                    colns = boxns.column()
                    colns.alignment = "CENTER"
                    colns.label(text = "[ Simulation not applicable here ]", icon="X")
@addon_updater_ops.make_annotations
class BGEN_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Addon updater preferences.
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True)

    updater_interval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=1,
        min=0,
        max=31)

    updater_interval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        box = col.box()
        col1 = box.column()
        col1.label(text= "Prefereces go here")  
        
        addon_updater_ops.update_settings_ui(self,context)

        

#==================================================================================================
#                                         [REGISTERS]
#==================================================================================================

bgenClasses = (BGEN_PT_bgenProperties, BGEN_PT_bgenExpandProp, BGEN_ui_panel, BGEN_OT_choose_nodeTree,  
               BGEN_OT_single_user, BGEN_OT_execute_cloth_settings,BGEN_OT_single_user_vts, BGEN_OT_create_sim_guides, 
               BGEN_OT_single_user_matt, BGEN_OT_add_VTS_mod,BGEN_OT_remove_bgen_mod,BGEN_OT_add_LM_mod, BGEN_OT_remove_sim_collection,
               BGEN_OT_reset_index_order, BGEN_OT_flip_index_order,BGEN_preferences,BGEN_OT_bake_hair_sim,BGEN_OT_choose_vts_nodeTree)
                
def register():  
    addon_updater_ops.register(bl_info)
    for cls in bgenClasses:
        addon_updater_ops.make_annotations(cls)
        bpy.utils.register_class(cls)
    bpy.types.Scene.bgen_tools = bpy.props.PointerProperty(type= BGEN_PT_bgenProperties)
    bpy.types.Object.bgen_expand = bpy.props.PointerProperty(type= BGEN_PT_bgenExpandProp)

                           
def unregister(): 
    addon_updater_ops.unregister()
    for cls in bgenClasses:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.bgen_tools
    del bpy.types.Object.bgen_expand



'''                    
if __name__ == "__main__":
    register()
    unregister()
'''
