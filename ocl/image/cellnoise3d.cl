#include "hipie/utils.h"
#include "hipie/noise/vnoise.h"
#include "hipie/image.h"




kernel void image_cellnoise3d(
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
	global float * noise,
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
#ifdef HAS_position_map_x
	int position_map_stride_x,
	int position_map_stride_y,
	int position_map_stride_z,
	int position_map_stride_offset,
	int position_map_res_x,
	int position_map_res_y,
	int position_map_res_z,
	float position_map_voxelsize_x,
	float position_map_voxelsize_y,
	float position_map_voxelsize_z,
	global float * position_map_x,
	int position_map_y_stride_x,
	int position_map_y_stride_y,
	int position_map_y_stride_z,
	int position_map_y_stride_offset,
	global float * position_map_y,
	int position_map_z_stride_x,
	int position_map_z_stride_y,
	int position_map_z_stride_z,
	int position_map_z_stride_offset,
	global float * position_map_z,
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
	int is_inverted,
	int is_ridged,
	int cell_mode,
	int distance_metric,
	float jitter,
	float bound_threshold,
	float minkowksy_number,
	float3 warp_offset_direction
)
{
DEF_IMAGE_STRUCT(noise)
#ifdef HAS_warp_offset
DEF_IMAGE_STRUCT(warp_offset)
#endif
#ifdef HAS_warp_offset_vec_x
DEF_IMAGEV_STRUCT(warp_offset_vec)
#endif
#ifdef HAS_position_map_x
DEF_IMAGEV_STRUCT(position_map)
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
#define OCTAVE_VALUE switch (cell_mode) { \
    case 0: \
        octave_value = f1; \
        break; \
    case 1: \
        octave_value = f2; \
        break; \
    case 2: \
        octave_value = f2 - f1; \
        break; \
    case 3: \
        octave_value = f2 * f1; \
        break; \
    case 4: \
        octave_value = f1 / f2; \
        break; \
    case 5: \
        octave_value = cell_value; \
        break; \
    case 6: \
        octave_value = dot(noise_pos - .5f * (p1 + p2), normalize(p1 - p2) ); \
        break; \
    default: \
        break; \
} \



int3 period = (int3)(scale, scale, scale);

float noise_value = 0.f;

float weight = 1.f;
float total_weight = 0.f;

float3 woffset = {0.f, 0.f, 0.f};

#ifdef HAS_warp_offset
    woffset = warp_offset_direction * bsample(warp_offset, __sys_pixel_pos); 
#endif

#ifdef HAS_warp_offset_vec_x
    woffset = bsamplev(warp_offset_vec, __sys_pixel_pos);
#endif 

float rough_map = 1.f;

#ifdef HAS_roughness_map
    rough_map = bsample(roughness_map, __sys_pixel_pos);
#endif

float cell_value, f1, f2;
float3 p1, p2;
float3 noise_pos = (float3)(__sys_pixel_pos, 0.f) + woffset;

#ifdef HAS_position_map_x
    noise_pos = bsamplev(position_map, __sys_pixel_pos);
#endif


switch (distance_metric) {

    case 0:
        for (int i = 0; i < octaves; i++) {

            total_weight += weight;
            pvnoise3(seed, noise_pos, jitter, &cell_value, &f1, &f2, &p1, &p2, period);
            float octave_value = 0.f;

            OCTAVE_VALUE

            noise_value += octave_value * weight;
            period *= 2;
            weight *= (roughness * rough_map );

            seed += 1.f;
        }
        break;

    case 1:
        for (int i = 0; i < octaves; i++) {

            total_weight += weight;
            pmvnoise3(seed, noise_pos, jitter, &cell_value, &f1, &f2, &p1, &p2, period);
            float octave_value = 0.f;

            OCTAVE_VALUE

            noise_value += octave_value * weight;
            period *= 2;
            weight *= (roughness * rough_map );

            seed += 1.f;
        }
        break;

    case 2:
        for (int i = 0; i < octaves; i++) {

            total_weight += weight;
            pcvnoise3(seed, noise_pos, jitter, &cell_value, &f1, &f2, &p1, &p2, period);
            float octave_value = 0.f;

            OCTAVE_VALUE

            noise_value += octave_value * weight;
            period *= 2;
            weight *= (roughness * rough_map );

            seed += 1.f;
        }
        break;

    case 3:
        for (int i = 0; i < octaves; i++) {

            total_weight += weight;
            pmkvnoise3(seed, noise_pos, jitter, &cell_value, &f1, &f2, &p1, &p2, period, minkowksy_number);
            float octave_value = 0.f;

            OCTAVE_VALUE

            noise_value += octave_value * weight;
            period *= 2;
            weight *= (roughness * rough_map );

            seed += 1.f;
        }
        break;


    default:
        break;
}

if (is_inverted > 0) {
    noise_value = 1.f - noise_value;
}

if (is_ridged > 0) {
    noise_value = fabs(noise_value);
}

noise[__sys_elemnum] = noise_value / total_weight;

}


