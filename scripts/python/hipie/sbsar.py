from __future__ import annotations
from sys import stdin
from typing import Any, NamedTuple, Type, Union

import subprocess
import json
import re
import os
import itertools as it
import hou

sbsrender_path = R"C:\Program Files\Adobe\Adobe Substance 3D Designer\sbsrender.exe"

inputs_regex = re.compile(r"^\s*[ \t]*INPUT[ \t]+([$\w]+)[ \t]+(\w+)", re.MULTILINE)
outputs_regex = re.compile(r"^\s*[ \t]*OUTPUT[ \t]+([$\w]+)", re.MULTILINE)
presets_regex = re.compile(r"^\s*[ \t]*PRESET[ \t]+([^\n\r]+)", re.MULTILINE)
graphs_regex = re.compile(r"^[ \t]*GRAPH-URL[ \t]+pkg://(\S*)", re.MULTILINE)
blank_line_regex = re.compile(r"(?:\r?\n){2,}")

SBSAR_USERDATA_KEY = "__sbsar_json_cache"

def _error(message, exception_class):
    if hou.isUIAvailable():
        hou.ui.displayMessage(message, severity=hou.severityType.Error)
    else:
        print(message)

    raise exception_class(message)

value_map = {
    "FLOAT1": "float1_value{}",
    "FLOAT2": "float2_value{}",
    "FLOAT3": "float3_value{}",
    "FLOAT4": "float4_value{}",
    "INTEGER1": "int1_value{}",
    "INTEGER2": "int2_value{}",
    "INTEGER3": "int3_value{}",
    "INTEGER4": "int4_value{}",
    "STRING": "str_value{}"
}

class SBSARInput(NamedTuple):
    input_type: int
    name: str
    usage: str
    path: str

    _parms_meta = ("input_type{}", "input_name{}", "input_usage{}", "input_path{}")

class SBSAROutput(NamedTuple):
    output_type: int
    name: str
    usage: str
    out_format: str
    bitdepth: str
    colorspace: str

    _parms_meta = ("output_type{}", "output_name{}", "output_usage{}", 
        "graph_output_format{}", "graph_output_bitdepth{}", "graph_output_colorspace{}")
    _eval_as_string = ("graph_output_format{}", "graph_output_bitdepth{}")


def get_multiparm_instances(multiparm: hou.Parm, parm_name: str, eval_as_string: list[str] = []) -> list[Any]:
    node: hou.Node = multiparm.node()
    num_instances = multiparm.evalAsInt()
    start_index = multiparm.multiParmStartOffset()

    result = []

    for i in range(start_index, start_index + num_instances):
        instance_name = parm_name.format(i)
        string_names = [s.format(i) for s in eval_as_string]
        parm_instance: hou.Parm = node.parm(instance_name)
        if parm_instance is not None:
            if instance_name in string_names:
                result.append(parm_instance.evalAsString())
            else:
                result.append(parm_instance.eval())

    return result

def get_multiparm_tuples(multiparm: hou.Parm, parm_names: list[str], eval_as_string: list[str] = []) -> list[Any]:
    return list(zip(*[get_multiparm_instances(multiparm, parm, eval_as_string) for parm in parm_names]))


def get_multiparm_namedtuples(multiparm: hou.Parm, tuple_class: Type) -> list[tuple]:
    eval_as_string = []
    if hasattr(tuple_class, "_eval_as_string"):
        eval_as_string = tuple_class._eval_as_string
    tuples = get_multiparm_tuples(multiparm, tuple_class._parms_meta, eval_as_string)
    return [tuple_class(*t) for t in tuples]


def menu_from_list(l: list[str]):
    return [i for item in l for i in it.repeat(item, 2)] 

def get_sbsar_info(sbsar_path: str) -> str:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    result = subprocess.run([sbsrender_path, "info", sbsar_path], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    out = result.stdout.decode("utf-8")
    return out
    
def get_sbsar_json(sbsar_info: str) -> str:
    lines = [s for s in blank_line_regex.split(sbsar_info) if len(s) > 0]

    sbsar_info_dict = {
        "graphs": {},
        "metadata": {}
    }

    graphs = sbsar_info_dict["graphs"]
    sbsar_metadata = sbsar_info_dict["metadata"]

    for line in lines:
        graph_id_match = graphs_regex.match(line)

        if graph_id_match:
            graph_id = graph_id_match.group(1)
            graphs[graph_id] = {
                "parms": {},
                "inputs": [],
                "outputs": [],
                "presets": []
            }

            graph = graphs[graph_id]

            for graph_input in inputs_regex.findall(line):
                if graph_input[1] == "IMAGE":
                    graph["inputs"].append(graph_input[0])
                else:
                    graph["parms"][graph_input[0]] = graph_input[1]

            for graph_preset in presets_regex.findall(line):
                graph["presets"].append(graph_preset)

            for graph_output in outputs_regex.findall(line):
                graph["outputs"].append(graph_output)

    sbsar_metadata["all_parms"] = list(set(it.chain.from_iterable(graphs[graph]["parms"].items() for graph in graphs)))
    sbsar_metadata["all_inputs"] = list(set(it.chain.from_iterable(graphs[graph]["inputs"] for graph in graphs)))
    sbsar_metadata["all_outputs"] = list(set(it.chain.from_iterable(graphs[graph]["outputs"] for graph in graphs)))
    sbsar_metadata["all_presets"] = list(set(it.chain.from_iterable(graphs[graph]["presets"] for graph in graphs)))

    return json.dumps(sbsar_info_dict)

def load_sbsar_json(node: hou.Node) -> dict:
    sbsar_json = node.userData(SBSAR_USERDATA_KEY)
    if sbsar_json is not None:
        return json.loads(sbsar_json)
    return {
        "graphs": {},
        "metadata": {}
    }

def cache_sbsar_json(node: hou.Node, sbsar_json: str):
    node.setUserData(SBSAR_USERDATA_KEY, sbsar_json)

def refresh_sbsar_cache(node: hou.Node):
    sbsar_path = node.parm("sbsar").evalAsString()
    sbsar_info = get_sbsar_info(sbsar_path)
    sbsar_json = get_sbsar_json(sbsar_info)
    cache_sbsar_json(node, sbsar_json)

def get_sbsar_all_graphs_menu(node: hou.Node):
    sbsar_json = load_sbsar_json(node)
    graphs = sbsar_json["graphs"].keys()
    return menu_from_list(graphs)

def get_sbsar_all_presets_menu(node: hou.Node):
    sbsar_json = load_sbsar_json(node)
    presets = sbsar_json["metadata"]["all_presets"]
    return menu_from_list(presets)     

def get_matched_graphs(node: hou.Node, sbsar_json: dict) -> list[str]:
    graphs = sbsar_json["graphs"]
    pattern = node.parm("output_graphs").evalAsString()
    pattern = pattern.strip()
    if not pattern or pattern == "*":
        return sbsar_json["graphs"].keys()

    return [graph for graph in graphs if hou.text.patternMatch(pattern, graph)]

def fill_parms_from_json(node: hou.Node):
    sbsar_json = load_sbsar_json(node)
    sbs_graphs = sbsar_json["graphs"]

    graphs = get_matched_graphs(node, sbsar_json)
    parms = list(set(it.chain.from_iterable(sbs_graphs[graph]["parms"].items() for graph in graphs)))

    parms_multiparm: hou.Parm = node.parm("params")
    names = get_multiparm_instances(parms_multiparm, "graph_parm_name{}")

    for parm in parms:
        if parm[0] not in names and parm[0] != "$outputsize":
            last_index = parms_multiparm.eval()
            parms_multiparm.insertMultiParmInstance(last_index)
            parm_name: str = parm[0]
            if parm_name.startswith("$"):
                parm_name = "\\" + parm_name
            node.parm(f"graph_parm_name{last_index + 1}").set(parm_name)
            node.parm(f"graph_parm_type{last_index + 1}").set(parm[1])

def fill_inputs_from_json(node: hou.Node):
    sbsar_json = load_sbsar_json(node)
    sbs_graphs = sbsar_json["graphs"]

    graphs = get_matched_graphs(node, sbsar_json)
    inputs_multiparm: hou.Parm = node.parm("inputs")
    input_names = get_multiparm_tuples(inputs_multiparm, ("input_name{}", "input_type{}"))
    
    inputs = list(set(it.chain.from_iterable(sbs_graphs[graph]["inputs"] for graph in graphs)))

    for entry in inputs:
        if (entry, 0) not in input_names:
            last_index = inputs_multiparm.eval()
            inputs_multiparm.insertMultiParmInstance(last_index)
            node.parm(f"input_name{last_index + 1}").set(entry)

def fill_outputs_from_json(node: hou.Node):
    sbsar_json = load_sbsar_json(node)
    sbs_graphs = sbsar_json["graphs"]

    graphs = get_matched_graphs(node, sbsar_json)
    outputs_multiparm: hou.Parm = node.parm("graph_outputs")
    output_names = get_multiparm_tuples(outputs_multiparm, ("output_name{}", "output_type{}"))
    
    outputs = list(set(it.chain.from_iterable(sbs_graphs[graph]["outputs"] for graph in graphs)))

    for outp in outputs:
        if (outp, 0) not in output_names:
            last_index = outputs_multiparm.eval()
            outputs_multiparm.insertMultiParmInstance(last_index)
            node.parm(f"output_name{last_index + 1}").set(outp)


def get_inputs_commandline(node: hou.Node) -> list[str]:
    inputs_multiparm: hou.Parm = node.parm("inputs")

    inputs: list[SBSARInput] = get_multiparm_namedtuples(inputs_multiparm, SBSARInput)
    result = []

    for i in inputs:
        if i.input_type == 0:
            result += ["--set-entry", f"{i.name}@{i.path}"]
        else:
            result += ["--set-entry-usage", f"{i.usage}@{i.path}"]

    return result

def get_outputs_commandline(node: hou.Node) -> list[str]:
    inputs_multiparm: hou.Parm = node.parm("graph_outputs")

    outputs: list[SBSAROutput] = get_multiparm_namedtuples(inputs_multiparm, SBSAROutput)
    print(outputs)
    result = []

    for o in outputs:
        if o.output_type == 0:
            result += ["--input-graph-output", o.name]
            if o.out_format != "default":
                result += ["--set-output-format", f"{o.name}@{o.out_format}"]
            if o.bitdepth != "default":
                result += ["--set-output-bit-depth",  f"{o.name}@{o.bitdepth}"]
            if o.colorspace.strip():
                result += ["--set-output-colorspace", o.colorspace]
        else:
            result += ["--input-graph-output-usage", o.usage]


    return result


def get_parms_commandline(node: hou.Node) -> list[str]:
    parms_multiparm: hou.Parm = node.parm("params")

    start_index = parms_multiparm.multiParmStartOffset()
    num_parms = parms_multiparm.evalAsInt()

    value_command = []

    for i in range(start_index, start_index + num_parms):
        parm_type = node.parm(f"graph_parm_type{i}").evalAsString()
        parm_name = node.parm(f"graph_parm_name{i}").evalAsString()
        parm_value_name = value_map[parm_type].format(i)
        use_color = node.parm(f"use_color_editor{i}").evalAsInt()

        if parm_type == "FLOAT3" and use_color:
            parm_value_name = f"rgb_value{i}"

        if parm_type == "FLOAT4" and use_color:
            parm_value_name = f"rgba_value{i}"

        value_parm: hou.ParmTuple = node.parmTuple(parm_value_name)

        value = value_parm.eval()
        value_command += ["--set-value", f"{parm_name}@{','.join((str(v) for v in value))}"]

    return value_command

def get_output_graphs_commandline(node: hou.Node, sbsar_json: dict) -> list[str]:
    matched_graphs = get_matched_graphs(node, sbsar_json)
    result = []
    for graph in matched_graphs:
        result += ["--input-graph", graph]
    return result

def get_settings_commandline(node: hou.Node):
    result = []

    if node.evalParm("settings_format"):
        result += ["--output-format", node.parm("output_format").evalAsString()]

    if node.evalParm("settings_compression"):
        result += ["--png-format-compression", node.parm("png_compression").evalAsString()]

    if node.evalParm("settings_colorspace"):
        result += ["--output-colorspace", node.parm("color_space").evalAsString()]

    if node.evalParm("settings_cachedir"):
        result += ["--cache-dir", node.parm("cache_dir").evalAsString()]

    if node.evalParm("settings_cpucount"):
        result += ["--cpu-count", str(node.parm("cpu_count").eval())]

    if node.evalParm("settings_memorybudget"):
        result += ["--memory-budget", str(node.parm("memory_budget").eval())]

    if node.evalParm("settings_ocioconfig"):
        result += ["--ocio", node.parm("ocio_config").evalAsString()]

    if node.evalParm("use_ace"):
        result += ["--ace"]
        result += ["--ace-render-intent", node.parm("ace_render_intent").evalAsString()]
        result += ["--ace-working-space", node.parm("ace_working_space").evalAsString()]

        icc_path = node.evalParm("icc_profiles_path")
        if icc_path.strip():
            result += ["--icc-profiles-path", icc_path]

    return result

def get_time_commandline(node: hou.Node):
    time_type = node.parm("time_type").evalAsString()

    time = 0.0
    (frame_start, frame_end, _) = node.parmTuple("f").eval()
    frame = hou.frame()

    if time_type == "range":
        time = (frame - frame_start) / (frame_end - frame_start)
    elif time_type == "range_loop":
        time = (frame - frame_start) / (frame_end - frame_start + 1.0)
    elif time_type == "custom":
        time = node.evalParm("time")

    return ["--set-value", f"$time@{time}"]

def run_sbsrender(node: hou.Node):
    sbsar_json = load_sbsar_json(node)

    cl = [sbsrender_path]
    cl += ["render"]
    cl += [node.parm("sbsar").evalAsString()]

    output_path: str = node.evalParm("output_path")
    if output_path.strip():
        cl += ["--output-path", output_path]

    output_name: str = node.evalParm("output_name")
    if output_name.strip():
        cl += ["--output-name", output_name]

    if node.evalParm("engine_override"):
        cl += ["--engine", node.parm("engine").evalAsString()]

    cl += get_settings_commandline(node)

    pattern = node.parm("output_graphs").evalAsString()
    pattern = pattern.strip()
    if pattern and pattern != "*":
        cl += get_output_graphs_commandline(node, sbsar_json)

    cl += get_time_commandline(node)

    cl += get_inputs_commandline(node)
    if node.evalParm("use_graph_outputs"):
        cl += get_outputs_commandline(node)

    size_type = node.evalParm("size_type")
    size_x = node.parm("size_x").evalAsString()
    size_y = node.parm("size_y").evalAsString()

    if size_type == 0:
        cl += ["--set-value", f"$outputsize@{size_x},{size_x}"]
    else:
        cl += ["--set-value", f"$outputsize@{size_x},{size_y}"]

    if node.evalParm("use_random_seed"):
        cl += ["--set-value", f"$randomseed@{node.evalParm('random_seed')}"]

    cl += get_parms_commandline(node)

    if node.parm("use_preset").eval():
        cl += ["--use-preset", node.parm("preset").evalAsString()]

    print(cl)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    result = subprocess.run(cl, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

    if (result.returncode != 0):
        message = result.stderr.decode("utf-8")
        _error(message, hou.NodeError)

