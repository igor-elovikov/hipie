import hou

def is_vector_name(name):
    # type: (str) -> bool
    return name.endswith(".x") or name.endswith(".y") or name.endswith(".z")

def all_components_exist(name, volume_names):
    # type: (str, list[str]) -> bool
    name_x = name + ".x"
    name_y = name + ".y"
    name_z = name + ".z"
    return name_x in volume_names and name_y in volume_names and name_z in volume_names

def get_geo_volumes(geo):
    # type: (hou.Geometry) -> Dict[str, hou.Volume]
    name_attrib = geo.findPrimAttrib("name")
    if name_attrib is not None and geo is not None:
        return {name: volume for name, volume in ((v.attribValue(name_attrib), v) 
                        for v in geo.globPrims("@intrinsic:typeid==20"))}
    return []

def get_vector_volumes(volumes):
    vector_volumes = []

    for volume in volumes:
        if is_vector_name(volume):
            name = volume[:-2]
            if name not in vector_volumes and all_components_exist(name, volumes):
                vector_volumes.append(name)

    return vector_volumes
                    
def first_vector_volume(node, input_index=0):
    # type: (hou.SopNode) -> str

    node_input = node.input(input_index) # type: hou.SopNode

    if node_input is not None:

        input_geo = node_input.geometry() # type: hou.Geometry
        input_volumes = get_geo_volumes(input_geo)

        if input_volumes:
            vector_volumes = get_vector_volumes(input_volumes)
            
            if vector_volumes:
                return vector_volumes[0]
    
    return ""



def generate_image_menu(node, input_index=0):
    # type: (hou.SopNode) -> List[str]

    node_input = node.input(input_index) # type: hou.SopNode
    
    if node_input is not None:

        input_geo = node_input.geometry() # type: hou.Geometry
        input_volumes = get_geo_volumes(input_geo)

        if input_volumes:

            vector_volumes = get_vector_volumes(input_volumes)
            output = []

            for name in input_volumes:
                if not is_vector_name(name):
                    resolution = input_volumes[name].resolution()
                    label = "{name} {res} {type}".format(
                        name=name,
                        type="Grayscale",
                        res="{}x{}".format(resolution[0], resolution[1])
                    )
                    output.append(name)
                    output.append(label)

            for name in vector_volumes:
                resolution = input_volumes[name+".x"].resolution()
                label = "{name} {res} {type}".format(
                    name=name,
                    type="Color",
                    res="{}x{}".format(resolution[0], resolution[1])
                )
                output.append(name)
                output.append(label)

            return output 

    return []
                
def generate_group_from_name(node, name, input_index=0):
    # type: (hou.SopNode) -> str
    node_input = node.input(input_index) # type: hou.SopNode
    
    if node_input is not None:

        input_geo = node_input.geometry() # type: hou.Geometry
        input_volumes = get_geo_volumes(input_geo)

        if input_volumes:

            vector_volumes = get_vector_volumes(input_volumes)
            
            if name in input_volumes:
                return "@name="+name
            
            if name in vector_volumes:
                return "@name="+name+".*"
    
    return ""

def prim_from_name(node, name, input_index=0):
    # type: (hou.SopNode) -> int
    node_input = node.input(input_index) # type: hou.SopNode
    
    if node_input is not None:

        input_geo = node_input.geometry() # type: hou.Geometry
        prims = input_geo.globPrims("@name=" + name)
        if prims:
            prim = prims[0] # type: hou.Prim
            return prim.number()

        return 0
