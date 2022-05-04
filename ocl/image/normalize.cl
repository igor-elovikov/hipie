#include "hipie/utils.h"
#include "hipie/image.h"




kernel void image_normalize(
	int data_stride_x,
	int data_stride_y,
	int data_stride_z,
	int data_stride_offset,
	int data_res_x,
	int data_res_y,
	int data_res_z,
	float data_voxelsize_x,
	float data_voxelsize_y,
	float data_voxelsize_z,
	global float * data,
	int minmax_length,
	global float * minmax
)
{
DEF_IMAGE_STRUCT(data)
int __sys_ix = get_global_id(0);
int __sys_iy = get_global_id(1);
int __sys_iz = get_global_id(2);
int __sys_elemnum = data_stride_offset + data_stride_x * __sys_ix
	+ data_stride_y * __sys_iy
	+ data_stride_z * __sys_iz;
int3 __sys_voxel_index = {__sys_ix, __sys_iy, __sys_iz};
int2 __sys_pixel_index = (int2)(__sys_ix, __sys_iy);
float2 __sys_pixel_pos = convert_float2(__sys_pixel_index) / data_image.fresolution + data_image.pixel_size_half;
float v = data[__sys_elemnum];
float min = minmax[0];
float max = minmax[1];

data[__sys_elemnum] = (v - min) / (max - min);
}


