# OpenCL+

OpenCL SOP wrapper to simplify writing kernels.

The main goal - you don't have to ever touch *Generate Kernel* button to write your code.

Features:
- Semi-auto inputs binding from source as preprocessor directives
- Parameters like in VEX wrangles
- Vector volumes support
- Vector ramps support
- Additional context to work with 2D volumes as images
- More noises
- Jinja as an optional preprocessor

## Inputs Binding
There are two types of bindings supported: auto and manual. 

### Auto binding

Best for quick snippets.

```
#(bind|work) input_name{[options...]}
```

This binding resolved at compile-time based on input. Parser tries to find data with the same name and bind it accordingly. Basically it means you don't have to specify what kind of data you want to bind (whether it's attribute, volume or VDB). For attributes it also fills all the attribute type information.

**Example:**
```c
#work P
#bind Cd{writeonly}
#bind density{voxelsize, xformtoworld}
```

#### Worksets
`#work` specifies data to _Run Over_ in OpenCL SOP terms. You don't have to care about declaration order, parser will put the work data as the first writeable binding. Also `#work P` is just a shortcut for `#bind P{work}`.

For custom worksets use `#worksets worksets_begin, worksets_length` where *worksets_begin* and *worksets_length* are detail attributes names with workset data (refer to OpenCL SOP manual for more information)

#### Options

**General**

| Option | Description |
|---|:----------------------------------:|
|writeable| Bound data is writeable
|writeonly| Bound data is read only
|work| Data to *Run Over* |
|optional| Data is optional (surrounded by guards provided by SOP) |


**Volumes**

| Option | Description |
|---|:----------------------------------:|
|noalignment| Disable force alignment
|image| Bind 2D Volume as an image
|resolution| Include volume resolution as a parameter
|voxelsize| Include voxel size parameters (also supported for VDBs) |
|xformtoworld| Include matrix to convert from voxel to world space (also supported for VDBs) |
|xformtovoxel| Include matrix to convert from world to voxel space (also supported for VDBs) |

*Note:* Force alignment will be disabled if any additional information about volume is included or volume is bound as an image

### Manual binding

Best for embedding

```
#bindattr name{[work], class=(point|primitive|vertex|detail), type=(int|float|intarray|floatarray), size=typesize, [options...]}
#bindvolume name{[work], rank=(scalar|vector), [options...]}
#bindvdb name{[options...]}
```

Essentially this is the same as OpenCL SOP binding, it's just promoted to text form as a directive.

With this one you have to specify what exactly you want to bind. Then the actual binding name will be promoted as a parameter. 

## Parameters

To declare a kernel parameter:
```c
#parm float_parm // float parameter
#parmi int_parm // integer parameter
#parmv vector_parm // vector parameter
#parmp vector4_parm // vector4 parameter
#ramp float_ramp // float ramp parameter
#rampv vector_ramp // vector ramp parameter
```

For all the kernel parameters parser will create a spare parameter on the node so you can control them from one place.

## System Variables

Similar to VEX in snippet you have access to couple of *system* variables

| Variable | Description |
|---|:----------------------------------:|
|int @elemnum| Current element number |
|int3 @voxel_index| Current voxel index as int3 vector (volumes or images only) |
|int @ix, @iy, @iz| Current voxel index (volumes or images only) |
|int2 @pixel_index| Current pixel index (images only)
|float2 @pixel_pos| Normalized pixel position inside image (images only)

*Note*: Some variables are available only when you work on certain data

## Noises

In `ie_noise.cl.h` you can find additional noises. Most of them are ports of Inigo Quilez awesome work: https://www.iquilezles.org/

All distance based noises have variants with Manhattan, Chebyshev and Minkowski metrics.

The usual signature for noise is `[p][m|c|mk]noise_func[2|3]` where **p** stands for periodic noise, **m|c|mk** for optional distance metric (Manhattan, Chebyshev and Minkowsky) and **2|3** for input type (2d or 3d). 
For example:
* *mvnoise3* - Voronoi 3D noise with Manhattan metric
* *pnoise2* - Periodic 2D gradient noise
* *mksvnoise3* - Smooth 3D Voronoi noise with Minkowski metric

**Voronoi noise**
```c
// 2D
void [p][m|c|mk]vnoise2(float2 pos, float jitter, float* cell_value, float* f1, float* f2, float2* p1, float2* p2, [int2 period], [float minkowski_number])
// 3D
void [p][m|c|mk]vnoise3(float3 pos, float jitter, float* cell_value, float* f1, float* f2, float3* p1, float3* p2, [int3 period], [float minkowski_number])
```

**Smooth voronoi noise**: https://www.iquilezles.org/www/articles/smoothvoronoi/smoothvoronoi.htm
```c
// 2D
float [p][m|c|mk]svnoise2(float2 pos, float jitter, float falloff, [int2 period], [float minkowski_number])
// 3D
float [p][m|c|mk]svnoise3(float3 pos, float jitter, float falloff, [int3 period], [float minkowski_number])
```

**Gradient noise**: https://www.iquilezles.org/www/articles/gradientnoise/gradientnoise.htm
```c
// 2D
float [p]noise2(float2 pos, [int2 period])
// 3D
float [p]noise3(float3 pos, [int3 period])
```

**Gradient noise with analytical derivatives**: https://www.iquilezles.org/www/articles/gradientnoise/gradientnoise.htm 

```c
// 2D
float3 [p]noise2d(float2 pos, [int2 period])
// 3D
float4 [p]noise3d(float3 pos, [int3 period])
```
Return format is *(noise_value, derivative)*

**Voronoise**: https://www.iquilezles.org/www/articles/voronoise/voronoise.htm
```c
// 2D
float [p][m|c|mk]voronoise2(float2 pos, float u, float v, [int2 period], [float minkowski_number])
// 3D
float [p][m|c|mk]voronoise3(float3 pos, float u, float v, [int3 period], [float minkowski_number])
```

*Note*: All periodic noises are automatically downscaled to normalized range


## Jinja
## HDA Embedding
## Limitations
Currently only 32-bit precision is fully supported