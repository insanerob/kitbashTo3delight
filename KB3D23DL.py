# https://github.com/insanerob/kitbashTo3delight
# Searches for principled shader nodes in a path and tries to recreate them as 
# 3Delight Substance and Glass materials
# Add a primitive wrangle to alter the material paths 
# @shop_materialpath = replace(s@shop_materialpath , '/obj/KB3D_HOK/matnet' , '/obj/3dlmatnet') ;
# @shop_materialpath += "/dlTerminal1" ;
        
import hou

ior_default = 1.52 #Glass IOR

def get_kb3d_materials(shader_path):
    # Returns all the principled shader nodes in the path

    in_materials = []
    root = hou.node(shader_path)
    node_type = "principledshader"
    
    for child in root.allSubChildren():
        if node_type in child.type().name():
            print(child.parent().name())
            in_materials.append(child)

    print(str(len(in_materials)) + " Shaders Found") 
    
    return in_materials
    
    
def split_substance_glass(in_materials):
    # Returns the materials split by type substance or glass (has transparency_texture param)
    out_materials = []
    substance_materials = []
    glass_materials = []
    print(str(len(in_materials)) + " materials to convert")
    
    for material in in_materials:
        parent_material = material.parent().name()
        parm_transparency_tex = material.parm('transparency_texture').eval()
        if len(parm_transparency_tex) > 0:
            glass_materials.append(material)
            out_materials.append({'mat_node': material, 'type': "glass", 'parent_name': material.parent().name()})
            print("Glass: " + parent_material + " " + parm_transparency_tex)
        else:
            substance_materials.append(material)
            out_materials.append({'mat_node': material, 'type': "substance", 'parent_name': material.parent().name()})
            print("Substance: " + parent_material)
            
    print("Substance materials = " + str(len(substance_materials)))
    print("Glass materials = " + str(len(glass_materials))) 
    print("Total materials in dict list: " + str(len(out_materials)))
    
    return out_materials
        
        
def parse_kb3d_substance(material):
    # Populates the paramaters in the kb3d principled shader specific to the 3dl Substance shader
    material_dict = {}
    
    mat_node = material["mat_node"]
    material_dict["name"] = material["parent_name"]
    material_dict["base"] = mat_node.parm('basecolor_texture').eval()
    material_dict["rough"] = mat_node.parm('rough_texture').eval()
    material_dict["metallic"] = mat_node.parm('metallic_texture').eval()
    material_dict["opacity"] = mat_node.parm('opaccolor_texture').eval()
    material_dict["normal"] = mat_node.parm('baseNormal_texture').eval()
    material_dict["displacement"] = mat_node.parm('dispTex_texture').eval()
    
    return material_dict
    
    
def parse_kb3d_glass(material):
    # Populates the paramaters in the kb3d principled shader specific to the 3dl Glass shader
    material_dict = {}
    
    mat_node = material["mat_node"]
    material_dict["name"] = material["parent_name"]
    material_dict["base"] = mat_node.parm('basecolor_texture').eval()
    material_dict["rough"] = mat_node.parm('rough_texture').eval()
    material_dict["metallic"] = mat_node.parm('metallic_texture').eval()
    material_dict["refract"] = mat_node.parm('transparency_texture').eval()
    material_dict["normal"] = mat_node.parm('baseNormal_texture').eval()
    material_dict["displacement"] = mat_node.parm('dispTex_texture').eval()
    
    return material_dict
    
    
def create_matnet(matnet_name):
# Check if the Material Network already exists
    matnet_path = "/obj/" + matnet_name
    if not hou.node(matnet_path):
        # If it doesn't exist, create it
        obj = hou.node("/obj")
        matnet = obj.createNode("matnet", matnet_name)
        matnet.cook()
        print("matnet created " + matnet_name)


def create_substance(texture_dict, matnet_name):
    # creates the 3dl material network with a substance shader
    matnet = hou.node(matnet_name)
    
    # create 3dl material builder
    matbuilder = matnet.createNode("3Delight::dlMaterialBuilder", texture_dict['name'])
    terminal = matbuilder.children()[0]
    
    # create 3dl substance node
    substance = matbuilder.createNode("3Delight::dlSubstance", "dlSubstance_" + texture_dict['name'])
    terminal.setInput(0, substance, 0)
    substance_parm = substance.parm("disp_normal_bump_type")
    substance_parm.set("2")

    # create 3dl uv
    uv = matbuilder.createNode("3Delight::dlUV", "UV")

    # create 3dl base texture
    if (texture_dict["base"] != ""):
        base_texture = matbuilder.createNode("3Delight::dlTexture", "base")
        base_texture_parm = base_texture.parm("textureFile")
        base_texture_parm.set(texture_dict["base"])
        base_texture_parm2 = base_texture.parm("textureFile_meta_colorspace")
        base_texture_parm2.set("sRGB")
        base_texture.setInput(20, uv, 0)
        substance.setInput(0, base_texture, 0)
    
    # create 3dl rough texture
    if (texture_dict["rough"] != ""):
        rough_texture = matbuilder.createNode("3Delight::dlTexture", "rough")
        rough_texture_parm = rough_texture.parm("textureFile")
        rough_texture_parm.set(texture_dict["rough"])
        rough_texture_parm2 = rough_texture.parm("textureFile_meta_colorspace")
        rough_texture_parm2.set("linear")
        rough_texture.setInput(20, uv, 0)
        substance.setInput(1, rough_texture, 1)

    # create 3dl metallic texture
    if (texture_dict["metallic"] != ""):
        metallic_texture = matbuilder.createNode("3Delight::dlTexture", "metallic")
        metallic_texture_parm =  metallic_texture.parm("textureFile")
        metallic_texture_parm.set(texture_dict["metallic"])
        metallic_texture_parm2 = metallic_texture.parm("textureFile_meta_colorspace")
        metallic_texture_parm2.set("linear")
        metallic_texture.setInput(20, uv, 0)
        substance.setInput(3, metallic_texture, 1)

    # create 3dl opactiy texture
    if (texture_dict["opacity"] != ""):
        opacity_texture = matbuilder.createNode("3Delight::dlTexture", "opacity")
        opacity_texture_parm =  opacity_texture.parm("textureFile")
        opacity_texture_parm.set(texture_dict["opacity"])
        opacity_texture_parm2 = opacity_texture.parm("textureFile_meta_colorspace")
        opacity_texture_parm2.set("linear")
        opacity_texture.setInput(20, uv, 0)
        substance.setInput(4, opacity_texture, 1)
        
    # create 3dl normal texture
    if (texture_dict["normal"] != ""):
        normal_texture = matbuilder.createNode("3Delight::dlTexture", "normal")
        normal_texture_parm =  normal_texture.parm("textureFile")
        normal_texture_parm.set(texture_dict["normal"])
        normal_texture_parm2 = normal_texture.parm("textureFile_meta_colorspace")
        normal_texture_parm2.set("linear")
        normal_texture.setInput(20, uv, 0)
        substance.setInput(9, normal_texture, 0)
    
    # create 3dl displacement texture
    if (texture_dict["normal"] != ""):
        displacement_texture = matbuilder.createNode("3Delight::dlTexture", "displacement")
        displacement_texture_parm =  displacement_texture.parm("textureFile")
        displacement_texture_parm.set(texture_dict["displacement"])
        displacement_texture_parm2 = displacement_texture.parm("textureFile_meta_colorspace")
        displacement_texture_parm2.set("linear")
        displacement_texture.setInput(20, uv, 0)
        
        # create 3dl displacement node
        displacement_node = matbuilder.createNode("3Delight::dlDisplacement", "3DLdisplacement")
        displacement_node.setInput(10, uv, 0)
        displacement_node_parm1 = displacement_node.parm("vectorSpace")
        displacement_node_parm1.set("0")
        displacement_node_parm2 = displacement_node.parm("vectorScale")
        displacement_node_parm2.set("0.05")
        displacement_node_parm3 = displacement_node.parm("vectorCenter")
        displacement_node_parm3.set("-0.5")
        
        # connect displacement texture and node
        displacement_node.setInput(0, displacement_texture, 0)
        
        # connect displacement to terminal
        terminal.setInput(2, displacement_node, 0)

    
    # Tidy up node layout
    matnet.layoutChildren()
    matbuilder.layoutChildren()
    
    
def create_glass(texture_dict, matnet_name):
    # creates the 3dl material network with a glass shader
    matnet = hou.node(matnet_name)
    
    # create 3dl material builder
    matbuilder = matnet.createNode("3Delight::dlMaterialBuilder", texture_dict['name'])
    terminal = matbuilder.children()[0]
    
    # create 3dl glass shader
    glass = matbuilder.createNode("3Delight::dlGlass", "dlGlass_" + texture_dict['name'])
    terminal.setInput(0, glass, 0)
    glass_parm1 = glass.parm("reflect_ior")
    glass_parm1.set(ior_default)
    glass_parm2 = glass.parm("refract_ior")
    glass_parm2.set(ior_default)
    
    # create 3dl uv
    uv = matbuilder.createNode("3Delight::dlUV", "UV")

    # create 3dl base texture
    if (texture_dict["base"] != ""):
        base_texture = matbuilder.createNode("3Delight::dlTexture", "base")
        base_texture_parm = base_texture.parm("textureFile")
        base_texture_parm.set(texture_dict["base"])
        base_texture_parm2 = base_texture.parm("textureFile_meta_colorspace")
        base_texture_parm2.set("sRGB")
        base_texture.setInput(20, uv, 0)
        glass.setInput(0, base_texture, 0)
        glass.setInput(6, base_texture, 0)
    
    # create 3dl rough texture
    if (texture_dict["rough"] != ""):
        rough_texture = matbuilder.createNode("3Delight::dlTexture", "rough")
        rough_texture_parm = rough_texture.parm("textureFile")
        rough_texture_parm.set(texture_dict["rough"])
        rough_texture_parm2 = rough_texture.parm("textureFile_meta_colorspace")
        rough_texture_parm2.set("linear")
        rough_texture.setInput(20, uv, 0)
        glass.setInput(1, rough_texture, 1)

    # create 3dl refract texture
    if (texture_dict["refract"] != ""):
        refract_texture = matbuilder.createNode("3Delight::dlTexture", "refract")
        refract_texture_parm =  refract_texture.parm("textureFile")
        refract_texture_parm.set(texture_dict["refract"])
        refract_texture_parm2 = refract_texture.parm("textureFile_meta_colorspace")
        refract_texture_parm2.set("linear")
        refract_texture.setInput(20, uv, 0)
        if (dont_use_refract_texture == 1):
            glass.setInput(2, refract_texture, 1)
            glass.setInput(8, refract_texture, 1)
        
    # create 3dl normal texture
    if (texture_dict["normal"] != ""):
        normal_texture = matbuilder.createNode("3Delight::dlTexture", "normal")
        normal_texture_parm =  normal_texture.parm("textureFile")
        normal_texture_parm.set(texture_dict["normal"])
        normal_texture_parm2 = normal_texture.parm("textureFile_meta_colorspace")
        normal_texture_parm2.set("linear")
        normal_texture.setInput(20, uv, 0)
        glass.setInput(18, normal_texture, 0)
    
    # create 3dl displacement texture
    if (texture_dict["normal"] != ""):
        displacement_texture = matbuilder.createNode("3Delight::dlTexture", "displacement")
        displacement_texture_parm =  displacement_texture.parm("textureFile")
        displacement_texture_parm.set(texture_dict["displacement"])
        displacement_texture_parm2 = displacement_texture.parm("textureFile_meta_colorspace")
        displacement_texture_parm2.set("linear")
        displacement_texture.setInput(20, uv, 0)
        
        # create 3dl displacement node
        displacement_node = matbuilder.createNode("3Delight::dlDisplacement", "3DLdisplacement")
        displacement_node.setInput(10, uv, 0)
        displacement_node_parm1 = displacement_node.parm("vectorSpace")
        displacement_node_parm1.set("0")
        displacement_node_parm2 = displacement_node.parm("vectorScale")
        displacement_node_parm2.set("0.053")
        displacement_node_parm3 = displacement_node.parm("vectorCenter")
        displacement_node_parm3.set("0.5")
    
        # connect displacement texture and node
        displacement_node.setInput(0, displacement_texture, 0)
        
        # connect displacement to terminal
        terminal.setInput(2, displacement_node, 0)
    

    # Tidy up node layout
    matnet.layoutChildren()
    matbuilder.layoutChildren()
        
    
def process_substance(material, matnet_name):
    # handles converting substance materials
    print("Substance processing: " + material["parent_name"] + " " + material["type"])
    texture_dict = parse_kb3d_substance(material)
    create_substance(texture_dict, matnet_name)
    
    
def process_glass(material, matnet_name):
    # handles converting glass materials
    print("Glass processing: " + material["parent_name"] + " " + material["type"])
    texture_dict = parse_kb3d_glass(material)
    create_glass(texture_dict, matnet_name)
        
        
def process_materials(materials_list, matnet_name):
    # takes each material and calls is processor by type
    
    # create material network if it doesn't exist
    create_matnet(matnet_name)
    matnet_name = "/obj/" + matnet_name
    # itterate through materials
    for material in materials_list:
        if material["type"] == "substance":
            process_substance(material, matnet_name)
        if material["type"] == "glass":
            process_glass(material, matnet_name)
        

def main():
    input_material_path = hou.selectedNodes()[0].path()
    matnet_name="3dlmatnet"
    in_materials = get_kb3d_materials(input_material_path)
    materials_list = split_substance_glass(in_materials)
    process_materials(materials_list, matnet_name)
    print("Finished Processing")

    
dont_use_refract_texture = hou.ui.displayMessage(
    "Use IOR of Glass rather than refraction texture?",
    buttons=("Yes", "No"),
    close_choice=1 
)
print(dont_use_refract_texture)
    
main()

    

