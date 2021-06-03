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
## System Variables
## Noises
## Jinja
## HDA Embedding
## Limitations
Currently only 32-bit precision is fully supported