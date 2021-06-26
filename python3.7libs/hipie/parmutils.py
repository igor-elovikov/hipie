from __future__ import annotations
from typing import Optional, Union
from collections import Iterable
import hou

def _unpack_parm_from_kwargs(parms: Union[hou.Parm, hou.ParmTuple, list[hou.ParmTuple]]) -> Optional[hou.Parm]:
    if isinstance(parms, hou.Parm) or isinstance(parms, hou.ParmTuple):
        return parms
    if isinstance(parms, Iterable):
        if not parms:
            return None
        return parms[0]
    return None


def is_color_ramp(parms) -> bool:
    parm: hou.Parm = _unpack_parm_from_kwargs(parms)
    if parm is None:
        return False
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if parm_template.type() == hou.parmTemplateType.Ramp and parm_template.parmType() == hou.rampParmType.Color:
        return True
    
    return False

def is_color_parm(parms) -> bool:
    parm: hou.Parm = _unpack_parm_from_kwargs(parms)
    if parm is None:
        return False
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if (parm_template.type() == hou.parmTemplateType.Float and
            parm_template.numComponents() == 3 and
            parm_template.namingScheme() == hou.parmNamingScheme.RGBA):
        return True
    
    return False

def is_float_ramp(parms) -> bool:
    parm: hou.Parm = _unpack_parm_from_kwargs(parms)
    if parm is None:
        return False
    parm_template = parm.parmTemplate() # type: hou.ParmTemplate

    if parm_template.type() == hou.parmTemplateType.Ramp and parm_template.parmType() == hou.rampParmType.Float:
        return True
    
    return False

def get_multiparm_top_parent(parm: hou.Parm) -> hou.Parm:
    parent = parm 
    while parent.isMultiParmInstance():
        parent = parent.parentMultiParm()
    return parent

def is_multiparm_folder(parm: Union[hou.Parm, hou.ParmTuple]) -> bool:
    pt: hou.ParmTemplate = parm.parmTemplate()

    if not isinstance(pt, hou.FolderParmTemplate):
        return False

    ptf: hou.FolderParmTemplate = pt
    if ptf.folderType() in (hou.folderType.MultiparmBlock, hou.folderType.ScrollingMultiparmBlock, hou.folderType.TabbedMultiparmBlock):
        return True
    
    return False

def ramp_to_string(ramp: hou.Ramp) -> str:
    basis = ramp.basis()
    basis = ", ".join(f"hou.{b}" for b in basis)
    return f"hou.Ramp(({basis}), {ramp.keys()}, {ramp.values()})"

def parm_value_string(parm: hou.Parm):
    # that way I can evaluate ordered menus as integers
    try:
        expression = parm.expression()
        return expression
    except hou.OperationFailed:
        value = parm.eval()
        if isinstance(value, str):
            value = f'"{value}"'
        return str(value)

def parm_tuple_value_string(parm_tuple: hou.ParmTuple) -> str:
    return parm_value_string(parm_tuple[0]) if len(parm_tuple) == 1 else f"({', '.join(parm_value_string(p) for p in parm_tuple)})"

def multiparm_to_string(parm: Union[hou.Parm, hou.ParmTuple]) -> str:

    node: hou.SopNode = parm.node()

    template: hou.FolderParmTemplate = parm.parmTemplate()

    child_templates: list[hou.ParmTemplate] = template.parmTemplates()

    child_names: list[str] = [t.name() for t in child_templates]
    child_names: list[str] = [n.replace("#", "{}") for n in child_names]

    num_instances = parm.eval()[0] # no nested multiparms (yet)
    
    offset = parm.multiParmStartOffset()

    dict_strings = []

    for i in range(num_instances):

        multiparm_index = offset + i

        instance_output = []
        for cti, ct in enumerate(child_templates):
            parm_name = child_names[cti].format(multiparm_index)
            parm_instance = node.parmTuple(parm_name)
            instance_output.append(parm_tuple_as_dict_item(parm_instance, ct))

        dict_strings.append(f"{{{','.join(instance_output)}}}")

    return f"({','.join(dict_strings)},)"

def parm_tuple_as_dict_item(parm_tuple: hou.ParmTuple, parm_template: hou.ParmTemplate = None) -> str:

    parm_template: hou.ParmTemplate = parm_tuple.parmTemplate() if parm_template is None else parm_template
    
    if is_multiparm_folder(parm_tuple):
        value = multiparm_to_string(parm_tuple)
    else:
        value = parm_tuple_value_string(parm_tuple)

    if not isinstance(value, hou.Ramp):
        return f'"{parm_template.name()}": {value}'

def node_verb_parms(node: hou.SopNode, num_tabs = 1, tab="    ") -> str:

    verb_parms = node.verb().parms()

    parm_tuples: list[hou.ParmTuple] = node.parmTuples()
    
    output = "{"
    tabs = tab * num_tabs
    
    for parm_tuple in parm_tuples:

        parent: hou.Parm = parm_tuple.parentMultiParm()
        is_ramp_parm = (parent is not None and parent.parmTemplate().type() == hou.parmTemplateType.Ramp) or isinstance(parm_tuple.parmTemplate(), hou.RampParmTemplate)

        is_at_default = not is_multiparm_folder(parm_tuple) and parm_tuple.isAtDefault()

        if not is_ramp_parm and parm_tuple.name() in verb_parms and not is_at_default:
            output += f"\n{tabs}{parm_tuple_as_dict_item(parm_tuple)},"

    parms: list[hou.Parm] = node.parms()
    ramps = [p for p in parms if p.parmTemplate().type() == hou.parmTemplateType.Ramp]
    for ramp in ramps:
        try:
            ramp.expression()
            continue
        except hou.OperationFailed:
            if ramp.name() in verb_parms and not ramp.isAtDefault():
                output += f'\n{tabs}"{ramp.name()}": {ramp_to_string(ramp.eval())}'

    output += "}"

    return output