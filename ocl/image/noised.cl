#include "hipie/utils.h"
#include "hipie/noise/noise.h"
#include "hipie/image.h"




kernel void image_noise_derivatives(
	int noise_stride_x,
	int noise_stride_y,
	int noise_stride_z,
	int noise_stride_offset,
	int noise_res_x,
	int noise_res_y,
	int noise_res_z,
	float noise_voxelsize_x,
	float noise_voxelsize_y,
	float noise_voxelsize_z,
	global float * noise_x,
	int noise_y_stride_x,
	int noise_y_stride_y,
	int noise_y_stride_z,
	int noise_y_stride_offset,
	global float * noise_y,
	int noise_z_stride_x,
	int noise_z_stride_y,
	int noise_z_stride_z,
	int noise_z_stride_offset,
	global float * noise_z,
#ifdef HAS_warp_offset
	int warp_offset_stride_x,
	int warp_offset_stride_y,
	int warp_offset_stride_z,
	int warp_offset_stride_offset,
	int warp_offset_res_x,
	int warp_offset_res_y,
	int warp_offset_res_z,
	float warp_offset_voxelsize_x,
	float warp_offset_voxelsize_y,
	float warp_offset_voxelsize_z,
	global float * warp_offset,
#endif
#ifdef HAS_warp_offset_vec_x
	int warp_offset_vec_stride_x,
	int warp_offset_vec_stride_y,
	int warp_offset_vec_stride_z,
	int warp_offset_vec_stride_offset,
	int warp_offset_vec_res_x,
	int warp_offset_vec_res_y,
	int warp_offset_vec_res_z,
	float warp_offset_vec_voxelsize_x,
	float warp_offset_vec_voxelsize_y,
	float warp_offset_vec_voxelsize_z,
	global float * warp_offset_vec_x,
	int warp_offset_vec_y_stride_x,
	int warp_offset_vec_y_stride_y,
	int warp_offset_vec_y_stride_z,
	int warp_offset_vec_y_stride_offset,
	global float * warp_offset_vec_y,
	int warp_offset_vec_z_stride_x,
	int warp_offset_vec_z_stride_y,
	int warp_offset_vec_z_stride_z,
	int warp_offset_vec_z_stride_offset,
	global float * warp_offset_vec_z,
#endif
#ifdef HAS_roughness_map
	int roughness_map_stride_x,
	int roughness_map_stride_y,
	int roughness_map_stride_z,
	int roughness_map_stride_offset,
	int roughness_map_res_x,
	int roughness_map_res_y,
	int roughness_map_res_z,
	float roughness_map_voxelsize_x,
	float roughness_map_voxelsize_y,
	float roughness_map_voxelsize_z,
	global float * roughness_map,
#endif
	int scale,
	float seed,
	int octaves,
	float roughness,
	int is_ridged,
	int is_inverted,
	float3 warp_offset_direction
)
{
DEF_IMAGEV_STRUCT(noise)
#ifdef HAS_warp_offset
DEF_IMAGE_STRUCT(warp_offset)
#endif
#ifdef HAS_warp_offset_vec_x
DEF_IMAGEV_STRUCT(warp_offset_vec)
#endif
#ifdef HAS_roughness_map
DEF_IMAGE_STRUCT(roughness_map)
#endif
int __sys_ix = get_global_id(0);
int __sys_iy = get_global_id(1);
int __sys_iz = get_global_id(2);
int __sys_elemnum = noise_stride_offset + noise_stride_x * __sys_ix
	+ noise_stride_y * __sys_iy
	+ noise_stride_z * __sys_iz;
int3 __sys_voxel_index = {__sys_ix, __sys_iy, __sys_iz};
int2 __sys_pixel_index = (int2)(__sys_ix, __sys_iy);
float2 __sys_pixel_pos = convert_float2(__sys_pixel_index) / noise_image.fresolution + noise_image.pixel_size_half;
// TODO: no static optimization, need more investigation on compile time
int2 period = (int2)(scale, scale);

float3 noise_value = {0.f, 0.f, 0.f};

float weight = 1.f;
float total_weight = 0.f;

float2 woffset = {0.f, 0.f};

#ifdef HAS_warp_offset
    woffset = warp_offset_direction.xy * bsample(warp_offset, __sys_pixel_pos); 
#endif

#ifdef HAS_warp_offset_vec_x
    woffset = bsamplev(warp_offset_vec, __sys_pixel_pos).xy;
#endif

float rough_map = 1.f;

#ifdef HAS_roughness_map
    rough_map = bsample(roughness_map, __sys_pixel_pos);
#endif

for (int i = 0; i < octaves; i++) {

    total_weight += weight;

    float3 octave_value = {0.f, 0.f, 0.f};
    octave_value = pnoise2d(seed, __sys_pixel_pos + woffset, period);

    noise_value += octave_value * weight;
        
    period *= 2;
    weight *= (roughness * rough_map );

    seed += 1.f;
}

if (is_ridged > 0) {
    noise_value = fabs(noise_value);
}

if (is_inverted > 0) {
    noise_value = {1.f, 1.f, 1.f} - noise_value;
}

volumestore3(noise_value, __sys_elemnum, (float3)(noise.yz, 0.f));

}


