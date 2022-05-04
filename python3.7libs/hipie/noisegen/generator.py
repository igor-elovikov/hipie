from __future__ import annotations

from enum import Enum, auto
from typing import NamedTuple

class NoiseType(Enum):
    Perlin = auto()
    Simplex = auto()
    Phasor = auto()    
    Gradient = auto()
    Flow = auto()
    GradientWithDerivatives = auto()
    Voronoi = auto()
    SmoothVoronoi = auto()
    Voronoise = auto()
    Alligator = auto()

class Dimension(Enum):
    D1D = auto()
    D2D = auto()
    D3D = auto()
    D4D = auto()

class DistanceMetric(Enum):
    Euclidean = auto()
    Manhattan = auto()
    Chebyshev = auto()
    Minkowsky = auto()

class FbmSettings(NamedTuple):
    num_octaves: int
    roughness: float

class NoiseSettings:

    def __init__(self) -> None:

        self.type: NoiseType = NoiseType.Gradient
        self.dimension: Dimension = Dimension.D2D
        self.output_dimension: Dimension = Dimension.D1D

        self.fbm_octaves: int = 0
        self.is_ridged: bool = False
        self.is_periodic: bool = True

        self.domain_warp_settings: NoiseSettings = None

        self.minkowsky_number: float = 1.0
      
function_names = {
    NoiseType.Gradient: "noise",
    NoiseType.GradientWithDerivatives: "noise",
    NoiseType.Voronoi: "vnoise",
    NoiseType.SmoothVoronoi: "svnoise",
    NoiseType.Voronoise: "voronoise"
}

function_signatures = {
    NoiseType.Gradient: "(float seed, {})",
    NoiseType.GradientWithDerivatives: "noise",
    NoiseType.Voronoi: "vnoise",
    NoiseType.SmoothVoronoi: "svnoise",
    NoiseType.Voronoise: "voronoise"
}

dimension_types = {
    Dimension.D1D: "float",
    Dimension.D2D: "float2",
    Dimension.D3D: "float3",
    Dimension.D4D: "float4",
}

cell_noise_mode = {
    "f1": "f1",
    "f2minusf1": "f2 - f1",
    "f2plusf1": "f2 + f1",
    "f2multf1": "f2 * f1",
    "f2divf1": "f1 / f2",
    "cell_value": "random(seed)",
    "cell_bound": "(f2 - f1 < bound_threshold ? 1.0f : 0.0f)",
    "cell_bound_voronoi": "( (f2 - f1 < bound_threshold * (distance(cpos1, cpos2) / (f1 + f2))) ? 1.0f : 0.0f)"
}

grid_fmb_snippet = """
noise_pos = pos * {freq} + offset;
{octave_variable} = {noise_func}(noise_pos, oscale, oscale, oscale);
{noise_variable} += {octave_variable} * weight;
oscale *= 2;
weight *= roughness;
"""

voronoi_fbm_snippet = """
noise_pos = pos * {freq} + offset;
{noise_func}(noise_pos, jitter, seed, f1, f2, cpos1, cpos2, oscale, oscale, oscale);
{octave_variable} = {cell_noise_mode};
{noise_variable} += {octave_variable} * weight;
oscale *= 2;
weight *= roughness;
"""

def _get_ocl_base_noise_function(noise_settings: NoiseSettings, noise_variable: str) -> str:

    if noise_settings.fbm_octaves > 0:
        ...
    else:
        ...

def get_ocl_noise_function(noise_settings: NoiseSettings, func_name: str) -> str:
    
    out: str = ""

    out += f"static {dimension_types[noise_settings.output_dimension]} "
    out += f"{func_name}(float seed, {dimension_types[noise_settings.dimension]} pos"

    if noise_settings.fbm_octaves > 0:
        out += ", float roughness"

    if noise_settings.domain_warp_settings is not None and noise_settings.domain_warp_settings.fbm_octaves > 0:
        out += ", float domain_warp_roughness"
    
    out += ") {\n"

