import hou
import numpy as np
from collections import namedtuple

def update_float_from_color(node, color_parm, float_names):
    parent = color_parm.parentMultiParm()
    color_parm = parent if parent is not None else color_parm

    color_ramp = color_parm.eval() # type: hou.Ramp
    basis = color_ramp.basis()
    keys = color_ramp.keys()
    values = color_ramp.values()

    for idx in range(3):
        color_ramp_comp = hou.Ramp(basis, keys, tuple(v[idx] for v in values))
        linked_ramp = node.parm(float_names[idx])
        linked_ramp.set(color_ramp_comp)
    

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
\tk = 1.0 - bias
\tv = bias
\tnode.parm(ramp_name+"2pos").set(k)
\tnode.parm(ramp_name+"2value").set(v)
\tnode.parm(ramp_name+"3pos").set(k)
\tnode.parm(ramp_name+"3value").set(v)
"""

gain_callback = """
\tk1 = 0.5 - gain * 0.5
\tv1 = gain * 0.5
\tk2 = 0.5 + gain * 0.5
\tv2 = 1.0 - gain * 0.5
\t
\tnode.parm(ramp_name+"2pos").set(k1)
\tnode.parm(ramp_name+"2value").set(v1)
\tnode.parm(ramp_name+"3pos").set(k1)
\tnode.parm(ramp_name+"3value").set(v1)
\t
\tnode.parm(ramp_name+"5pos").set(k2)
\tnode.parm(ramp_name+"5value").set(v2)
\tnode.parm(ramp_name+"6pos").set(k2)
\tnode.parm(ramp_name+"6value").set(v2)
"""

easein_callback = """
\tk = easein
\tv = 0.0
\tnode.parm(ramp_name+"2pos").set(k)
\tnode.parm(ramp_name+"2value").set(v)
\tnode.parm(ramp_name+"3pos").set(k)
\tnode.parm(ramp_name+"3value").set(v)
"""

easeout_callback = """
\tk = 1.0 - easeout
\tv = 1.0
\tnode.parm(ramp_name+"2pos").set(k)
\tnode.parm(ramp_name+"2value").set(v)
\tnode.parm(ramp_name+"3pos").set(k)
\tnode.parm(ramp_name+"3value").set(v)
"""

smoothstep_callback = """
\td = min(center, 1.0 - center) * slope
\tk1 = center - d
\tk2 = center + d
\t
\tnode.parm(ramp_name+"2pos").set(k1)
\tnode.parm(ramp_name+"2value").set(0.0)
\tnode.parm(ramp_name+"3pos").set(k1)
\tnode.parm(ramp_name+"3value").set(0.0)
\t
\tnode.parm(ramp_name+"5pos").set(k2)
\tnode.parm(ramp_name+"5value").set(1.0)
\tnode.parm(ramp_name+"6pos").set(k2)
\tnode.parm(ramp_name+"6value").set(1.0)
\t
\tnode.parm(ramp_name+"4pos").set(center)
\tnode.parm(ramp_name+"4value").set(0.5)
"""

bell_callback = """
\twidth = 0.0001 if width < 0.0001 else width
\td = min(center, 1.0 - center) * width
\tk1 = center - d
\tk2 = center + d
\t
\tnode.parm(ramp_name+"2pos").set(k1-0.0001)
\tnode.parm(ramp_name+"2value").set(0.0)
\tnode.parm(ramp_name+"3pos").set(k1+0.0001)
\tnode.parm(ramp_name+"3value").set(1.0)
\t
\tnode.parm(ramp_name+"5pos").set(k2-0.0001)
\tnode.parm(ramp_name+"5value").set(1.0)
\tnode.parm(ramp_name+"6pos").set(k2+0.0001)
\tnode.parm(ramp_name+"6value").set(0.0)
\t
\tnode.parm(ramp_name+"4pos").set(center)
\tnode.parm(ramp_name+"4value").set(1.0)
\tnode.parm(ramp_name+"7value").set(0.0)
"""

bounce_callback = """
\twidth = 0.0001 if width < 0.0001 else width
\tk1 = center - center * width
\tk2 = center + (1.0 - center) * width
\t
\tnode.parm(ramp_name+"2pos").set(0.0)
\tnode.parm(ramp_name+"2value").set(speed)
\tnode.parm(ramp_name+"3pos").set(k1+0.0001)
\tnode.parm(ramp_name+"3value").set(1.0)
\t
\tnode.parm(ramp_name+"5pos").set(k2-0.0001)
\tnode.parm(ramp_name+"5value").set(1.0)
\tnode.parm(ramp_name+"6pos").set(1.0)
\tnode.parm(ramp_name+"6value").set(speed)
\t
\tnode.parm(ramp_name+"4pos").set(center)
\tnode.parm(ramp_name+"4value").set(1.0)
\tnode.parm(ramp_name+"7value").set(0.0)
"""

pulse_callback = """
\twidth = 0.0001 if width < 0.0001 else width
\td = min(center, 1.0 - center) * width
\tk1 = center - d
\tk2 = center + d
\t
\tnode.parm(ramp_name+"2pos").set(k1-0.0001)
\tnode.parm(ramp_name+"2value").set(0.0)
\tnode.parm(ramp_name+"3pos").set(k1+0.0001)
\tnode.parm(ramp_name+"3value").set(0.0)
\t
\tnode.parm(ramp_name+"5pos").set(k2-0.0001)
\tnode.parm(ramp_name+"5value").set(0.0)
\tnode.parm(ramp_name+"6pos").set(k2+0.0001)
\tnode.parm(ramp_name+"6value").set(0.0)
\t
\tnode.parm(ramp_name+"4pos").set(center)
\tnode.parm(ramp_name+"4value").set(1.0)
\tnode.parm(ramp_name+"7value").set(0.0)
"""


parametric_ramps = {
    "Bias": ParametricRamp((ParametricSpareParm("bias", "Bias", 0.5),), bias_callback, 4),
    "EaseIn": ParametricRamp((ParametricSpareParm("easein", "Ease In", 0.5),), easein_callback, 4),
    "EaseOut": ParametricRamp((ParametricSpareParm("easeout", "Ease Out", 0.5),), easeout_callback, 4),
    "Gain": ParametricRamp((ParametricSpareParm("gain", "Gain", 0.5),), gain_callback, 7),
    "Smoothstep": ParametricRamp(
        (ParametricSpareParm("slope", "Slope", 0.5), ParametricSpareParm("center", "Center", 0.5)), 
        smoothstep_callback, 7),
    "Bell": ParametricRamp(
        (ParametricSpareParm("width", "Width", 0.5), ParametricSpareParm("center", "Center", 0.5)), 
        bell_callback, 7),
    "Bounce": ParametricRamp(
        (ParametricSpareParm("width", "Width", 0.5), ParametricSpareParm("speed", "Speed", 0.5), ParametricSpareParm("center", "Center", 0.5)), 
        bounce_callback, 7),
    "Pulse": ParametricRamp(
        (ParametricSpareParm("width", "Width", 0.5), ParametricSpareParm("center", "Center", 0.5)), 
        pulse_callback, 7),
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
    callback += """
ramp = node.parm(ramp_name)
if not (ramp is None or ramp.evalAsInt() < {}):
""".format(parametric_ramp.num_keys)

    for parm in spare_parms: # type: ParametricSpareParm
        callback += "\t{} = node.parm('{}').eval()\n".format(parm.name, name_prefix + parm.name)

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
            label_format.format(ramp_parm.description(), parm.label),
            1,
            (parm.default_value,),
            min=0.0, max=1.0,
            script_callback=callback,
            script_callback_language=hou.scriptLanguage.Python
        )

        ptg.insertAfter(insert_parm_template, parm_template)

    node.setParmTemplateGroup(ptg)

    node.parm(name_prefix + spare_parms[0].name).pressButton()
