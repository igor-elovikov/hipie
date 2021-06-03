# OpenCL+

  - [Before You Start](#before-you-start)
  - [Inputs Binding](#inputs-binding)
    - [Auto binding](#auto-binding)
    - [Manual binding](#manual-binding)
    - [Worksets](#worksets)
    - [Options](#options)
  - [Parameters](#parameters)
  - [System Variables](#system-variables)
  - [Noises](#noises)
  - [Utilities](#utilities)
  - [Jinja](#jinja)
  - [HDA Embedding and promoting snippet](#hda-embedding-and-promoting-snippet)
  - [Limitations](#limitations)

OpenCL SOP wrapper to simplify writing kernels.

![Title](images/opencl_title.png)

The main goal - you don't have to ever touch *Generate Kernel* button to write your code.

Features:
- Semi-auto inputs binding from source as preprocessor directives
- Parameters like in VEX wrangles
- Vector volumes support
- Vector ramps support
- Additional context to work with 2D volumes as images
- More noises
- Jinja as an optional preprocessor

## Before You Start

The best overview of OpenCL SOP: https://vimeo.com/241568199

The very first advice actually still stands. You're most likely don't need to use OpenCL. 

However with this wrapper playing with OpenCL is a little bit more fun. Just don't expect magical performance gain over the VEX, especially if you're not crunching millions of points.

I think the most practical scenario is solvers and any algorithms where you can chain several OpenCL SOPs into compiled block. This wrapper contains only one OpenCL SOP node and just gives you a high-level control over it. So it's perfectly safe to put it into compiled block and expect no copying to the host.

For examples check `examples/opencl_plus_examples.hip` 

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

### Manual binding

Best for embedding

```
#bindattr name{[work], class=(point|primitive|vertex|detail), type=(int|float|intarray|floatarray), size=typesize, [options...]}
#bindvolume name{[work], rank=(scalar|vector), [options...]}
#bindvdb name{[options...]}
```

Essentially this is the same as OpenCL SOP binding, it's just promoted to text form as a directive.

With this one you have to specify what exactly you want to bind. Then the actual binding name will be promoted as a parameter.

### Worksets
`#work` specifies data to _Run Over_ in OpenCL SOP terms. You don't have to care about declaration order, parser will put the work data as the first writeable binding. Also `#work P` is just a shortcut for `#bind P{work}`.

For custom worksets use `#worksets worksets_begin, worksets_length` where *worksets_begin* and *worksets_length* are detail attributes names with workset data (refer to OpenCL SOP manual for more information)

### Options

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

In `hipie/noise.h` you can find additional noises. Most of them are ports of Inigo Quilez awesome work: https://www.iquilezles.org/

All distance based noises have variants with Manhattan, Chebyshev and Minkowski metrics.

The usual signature for noise is `[p][m|c|mk]noise_func[2|3]` where **p** stands for periodic noise, **m|c|mk** for optional distance metric (Manhattan, Chebyshev and Minkowsky) and **2|3** for input type (2d or 3d). 
For example:
* *mvnoise3* - Voronoi 3D noise with Manhattan metric
* *pnoise2* - Periodic 2D gradient noise
* *mksvnoise3* - Smooth 3D Voronoi noise with Minkowski metric

**Voronoi noise**
```c
// 2D
void [p][m|c|mk]vnoise2(float2 pos, float jitter, 
    float* cell_value, float* f1, float* f2, float2* p1, float2* p2, 
    [int2 period], [float minkowski_number])
// 3D
void [p][m|c|mk]vnoise3(float3 pos, float jitter, 
    float* cell_value, float* f1, float* f2, float3* p1, float3* p2, 
    [int3 period], [float minkowski_number])
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

## Utilities

Utility macros and functions available in snippets.

```c
// Evaluate ramp at position
float ramp(name, float pos)

// Evaluate vector ramp at position
float3 rampv(name, float pos)

// Equivalent of vload3 for vector volumes
float3 volumeload3(int index, name)

// Equivalent of vstore3 for vector volumes
void volumestore3(float3 value, int index, name)

// Sample scalar VDB at position
float vdb_sample(name, float3 pos)

// Sample vector VDB at position
float3 vdb_samplev(name, float3 pos)

// Bilinear sampling from image with normalized position
float bsample(name, float2 position)

// Bilinear sampling from vector image with normalized position
float3 bsamplev(name, float2 position)

// Nearest neighbor sampling from image with normalized position
float nsample(name, float2 position)

// Nearest neighbor sampling from vector image with normalized position
float3 nsamplev(name, float2 position)

// Sampling from image by index
float isample(name, int2 index)

// Bilinear sampling from vector image with normalized position
float3 isamplev(name, int2 index)
```

*Note*: Currently images are working only in repeated addressing (like tileable textures)

## Jinja

You can use Jinja template engine: https://jinja.palletsprojects.com/ for metaprogramming.

Please refer to Jinja example in `examples/opencl_plus_examples.hip` to see how you can utilize Jinja and python environment to generate convolution kernel. 

## HDA Embedding and promoting snippet

For better UX most of the edits are currently automated, i.e. snippet recompiled as soon as you make some changes (except rewiring, where you're probably have to recompile manually). 

However that won't work if you want to embed asset into another HDA and want to have more control over the snippet code. If you really want to do that you have to promote all the parameters to the HDA level (refer to Attribute Paint Masterclass: https://vimeo.com/375839266 from 53:45).

When you promote all the parameters you'll lose all callbacks (so you won't be able to compile snippet). Also as SOPs callback would still refer to the original OpenCL+ SOP node any attempt to recompile snippet will break the permission and won't work on a locked node.

To fix that you have to turn on *Manual Compilation* parameter and put this to your *Recompile Snippet* button callback:
```python
kwargs["node"].node("PATH_TO_SOP_INSIDE_HDA").hm().on_snippet_changed(kwargs["node"], True)
```
*Note*: This callback has to be on the HDAs level button

With this trick you can embed this SOP to HDA without marking it as an editable node. The only thing that you'll have to manually compile the snippet after changes by hitting *Recompile Snippet* button.

*Tip*: You can still use editable nodes and just ignore all the above. Also for options and compile-time branching you can utilize preprocessor conditionals, OpenCL SOP even supports detail attribute for compiler options (meaning that you can easily gives it preprocessor definitions).

## Limitations
Currently only 32-bit precision is fully supported
