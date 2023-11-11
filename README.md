# Houdini Tools  <!-- omit in toc --> 

Compatible only with Python 3 builds

- [Pen Tool](#pen-tool)
- [OpenCL+](#opencl)
- [SOP Subnetwork Verbifier](#sop-subnetwork-verbifier)
- [Gradient Picker](#gradient-picker)
- [Ramp Sketch](#ramp-sketch)
- [Parametric Ramps](#parametric-ramps)


## Pen Tool
**DEPRECATED. This tool was created for Houdini 18.0. Since 19.0 Houdini has native Curve SOP with better functionality**
![Pen Tool](help/images/tentacle.png)

Draw bezier curves as in other DCCs

## OpenCL+
**DEPRECATED. Since Houdini 20.0 OpenCL SOP introduced this changes and much more: https://www.sidefx.com/docs/houdini/vex/ocl.html**
![OpenCL+](help/images/opencl_title.png)

OpenCL SOP wrapper to automate most of the boilerplate work.
More info: [OpenCL+ Readme](help/OpenCL_Plus.md)

## SOP Subnetwork Verbifier
**DEPRECATED. Since Houdini 19.0 Invoke Compile Graph SOP provides much more flexible approach**

Generate SOP Verb function from arbitrary network (considering all the nodes have verbs)
More info: [Verbifier](help/verbifier.md)

## Gradient Picker
**NOTICE: SideFX LABs has the same tool since its introduction. Though this tool has color picking function missing in LABs**

![Gradient Picker](help/images/gradient_picker.gif)

Pick gradient from screen for color ramps.
Hold Shift for picking raw color without gamma corrections (2.2 Gamma adjusted by default)

Also works as a color picker from screen for color parms

## Ramp Sketch

![Ramp Sketch](help/images/ramp_sketch.gif)

Draw a ramp on screen.
Hold Shift for creating a BSpline ramp (Linear by default)

## Parametric Ramps

![Parametric Ramp](help/images/ramp_parametric.gif)

Setup ramp control parameters for common remapping functions. 
