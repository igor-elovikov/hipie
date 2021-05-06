import hou
import numpy as np
from collections import namedtuple

name_prefix_format = "__{}_ctrl_"
label_format = "{}: {}"

# Parametric ramp utils

def get_multiparm_top_parent(parm):
    # type: (hou.Parm) -> hou.Parm
    parent = parm 
    while parent.isMultiParmInstance():
        parent = parent.parentMultiParm()
    return parent

def clean_parametric_spare_parms(node, ramp_parm):
    # type: (hou.Node, hou.Parm) -> None
    ramp_name = ramp_parm.name()
    ptg = node.parmTemplateGroup() # type: hou.ParmTemplateGroup
    parm_entries = ptg.entriesWithoutFolders()

    name_prefix = name_prefix_format.format(ramp_name)

    for parm_template in parm_entries: # type: hou.ParmTemplate
        parm_name = parm_template.name() # type: str

        if parm_name.startswith(name_prefix):
            ptg.remove(parm_template)

    node.setParmTemplateGroup(ptg)

ParametricSpareParm = namedtuple("ParametricSpareParm", "name label default_value")
ParametricRamp = namedtuple("ParametricRamp", "spare_parms callback num_keys")

bias_callback = """
k = 1.0 - bias
v = bias
node.parm(ramp_name+"2pos").set(k)
node.parm(ramp_name+"2value").set(v)
node.parm(ramp_name+"3pos").set(k)
node.parm(ramp_name+"3value").set(v)
"""

parametric_ramps = {
    "Bias": ParametricRamp((ParametricSpareParm("bias", "Bias", 0.5),), bias_callback, 4)
}

def setup_parametric_ramp(node, ramp_parm, parametric_ramp_type):
    # type: (hou.Node, hou.Parm, str) -> None

    if parametric_ramp_type not in parametric_ramps:
        return

    ramp_name = ramp_parm.name()
    clean_parametric_spare_parms(node, ramp_parm)

    parametric_ramp = parametric_ramps[parametric_ramp_type] 
    spare_parms = parametric_ramp.spare_parms

    name_prefix = name_prefix_format.format(ramp_name)

    callback = "node = kwargs['node']\n"
    callback += "ramp_name = '{}'\n".format(ramp_name)

    for parm in spare_parms: # type: ParametricSpareParm
        callback += "{} = node.parm('{}').eval()\n".format(parm.name, name_prefix + parm.name)

    callback += parametric_ramp.callback

    ptg = node.parmTemplateGroup() # type: hou.ParmTemplateGroup

    insert_parm = get_multiparm_top_parent(ramp_parm)
    insert_parm_template = ptg.find(insert_parm.name())

    ramp = hou.Ramp(
        (hou.rampBasis.Bezier,) * parametric_ramp.num_keys,
        np.linspace(0.0, 1.0, parametric_ramp.num_keys),
        np.linspace(0.0, 1.0, parametric_ramp.num_keys)
    )

    ramp_parm.set(ramp)

    for parm in spare_parms: # type: ParametricSpareParm
        parm_template = hou.FloatParmTemplate(
            name_prefix + parm.name,
            label_format.format(ramp_name, parm.label),
            1,
            (parm.default_value,),
            min=0.0, max=1.0,
            script_callback=callback,
            script_callback_language=hou.scriptLanguage.Python
        )

        ptg.insertAfter(insert_parm_template, parm_template)

    node.setParmTemplateGroup(ptg)

    node.parm(name_prefix + spare_parms[0].name).pressButton()
