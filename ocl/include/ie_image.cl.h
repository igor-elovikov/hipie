#ifndef __ie_image_h
#define __ie_image_h

// workaround to use in opencl sop
typedef struct cl_fimage_t
{
    global float *data;

    int2 resolution;
    float2 fresolution;
    float2 pixel_size;
    float2 pixel_size_half;

    int stride_offset;
    int stride_x;
    int stride_y;
    int stride_z;

    int idz; // is it needed? probably I can bind images as slices
    
} cl_image;

typedef struct cl_vimage_t
{
    global float *data_x;
    global float *data_y;
    global float *data_z;

    int2 resolution;
    float2 fresolution;
    float2 pixel_size;
    float2 pixel_size_half;

    int stride_offset;
    int stride_x;
    int stride_y;
    int stride_z;

    int idz; // is it needed? probably I can bind images as slices
    
} cl_imagev;

#define index_from_position(image, pos) image->stride_offset + pos.x * image->stride_x + pos.y * image->stride_y + image->idz * image->stride_z 

// nearest neighbor sampling (normalized pos)
static float nsample_impl(cl_image* image, float2 pos)
{
    int2 ipos = convert_int2((fmod2r(pos, (float2)(1.f, 1.f)) * image->fresolution));
    int index = index_from_position(image, ipos);
    return image->data[index];
}

static float3 nsamplev_impl(cl_imagev* image, float2 pos)
{
    int2 ipos = convert_int2((fmod2r(pos, (float2)(1.f, 1.f)) * image->fresolution));
    int index = index_from_position(image, ipos);

    return (float3) (
        image->data_x[index],
        image->data_y[index],
        image->data_z[index]
    );
}

// index position sampling
static float isample_impl(cl_image* image, int2 pos)
{
    int2 ipos = imod2r(pos, image->resolution);
    int index = index_from_position(image, ipos);
    
    return image->data[index];
}

static float3 isamplev_impl(cl_imagev* image, int2 pos)
{
    int2 ipos = imod2r(pos, image->resolution);
    int index = index_from_position(image, ipos);

    return (float3) (
        image->data_x[index],
        image->data_y[index],
        image->data_z[index]
    );
}

// bilinear sampling (normalized pos)
static float bsample_impl(cl_image* image, float2 pos)
{
    float2 corner_pos = floor((pos - image->pixel_size_half) / image->pixel_size) * image->pixel_size + image->pixel_size_half;
    float2 q11_pos = fmod2r(pos - image->pixel_size_half, (float2)(1.f, 1.f));

    int2 q11_ipos = convert_int2(q11_pos * image->fresolution);
    int2 q12_ipos = imod2r((q11_ipos + (int2)(0, 1)), image->resolution);
    int2 q21_ipos = imod2r((q11_ipos + (int2)(1, 0)), image->resolution);
    int2 q22_ipos = imod2r((q11_ipos + (int2)(1, 1)), image->resolution);

    int q11_index = index_from_position(image, q11_ipos);
    int q12_index = index_from_position(image, q12_ipos);
    int q21_index = index_from_position(image, q21_ipos);
    int q22_index = index_from_position(image, q22_ipos);

    float2 np = (pos - corner_pos) / image->pixel_size;

    float q11 = image->data[q11_index];
    float q12 = image->data[q12_index];
    float q21 = image->data[q21_index];
    float q22 = image->data[q22_index];

    return (q11 * (1.f - np.x) + q21 * np.x) * (1.f - np.y) + (q12 * (1.f - np.x) + q22 * np.x) * np.y;
}

// bilinear sampling (normalized pos)
static float3 bsamplev_impl(cl_imagev* image, float2 pos)
{
    float2 corner_pos = floor((pos - image->pixel_size_half) / image->pixel_size) * image->pixel_size + image->pixel_size_half;
    float2 q11_pos = fmod2r(pos - image->pixel_size_half, (float2)(1.f, 1.f));

    int2 q11_ipos = convert_int2(q11_pos * image->fresolution);
    int2 q12_ipos = imod2r((q11_ipos + (int2)(0, 1)), image->resolution);
    int2 q21_ipos = imod2r((q11_ipos + (int2)(1, 0)), image->resolution);
    int2 q22_ipos = imod2r((q11_ipos + (int2)(1, 1)), image->resolution);

    int q11_index = index_from_position(image, q11_ipos);
    int q12_index = index_from_position(image, q12_ipos);
    int q21_index = index_from_position(image, q21_ipos);
    int q22_index = index_from_position(image, q22_ipos);

    float2 np = (pos - corner_pos) / image->pixel_size;

    float q11x = image->data_x[q11_index];
    float q12x = image->data_x[q12_index];
    float q21x = image->data_x[q21_index];
    float q22x = image->data_x[q22_index];

    float q11y = image->data_y[q11_index];
    float q12y = image->data_y[q12_index];
    float q21y = image->data_y[q21_index];
    float q22y = image->data_y[q22_index];

    float q11z = image->data_z[q11_index];
    float q12z = image->data_z[q12_index];
    float q21z = image->data_z[q21_index];
    float q22z = image->data_z[q22_index];

    float3 q11 = (float3)(q11x, q11y, q11z);
    float3 q12 = (float3)(q12x, q12y, q12z);
    float3 q21 = (float3)(q21x, q21y, q21z);
    float3 q22 = (float3)(q22x, q22y, q22z);

    return (q11 * (1.f - np.x) + q21 * np.x) * (1.f - np.y) + (q12 * (1.f - np.x) + q22 * np.x) * np.y;
}

static void image_write_impl(cl_image* image, int2 pos, float value)
{
    int2 ipos = imod2r(pos, image->resolution);
    int index = index_from_position(image, ipos);
    image->data[index] = value;
}

static void image_writev_impl(cl_imagev* image, int2 pos, float3 value)
{
    int2 ipos = imod2r(pos, image->resolution);
    int index = index_from_position(image, ipos);

    image->data_x[index] = value.x;
    image->data_y[index] = value.y;
    image->data_z[index] = value.z;
}

#define DEF_IMAGE_STRUCT(name) \
cl_image name##_image; \
name##_image.data = name; \
name##_image.stride_x = name##_stride_x; \
name##_image.stride_y = name##_stride_y; \
name##_image.stride_z = name##_stride_z; \
name##_image.stride_offset = name##_stride_offset; \
name##_image.idz = 0; \
name##_image.resolution = (int2) (name##_res_x, name##_res_y); \
name##_image.fresolution = convert_float2(name##_image.resolution); \
name##_image.pixel_size = (float2) (name##_voxelsize_x, name##_voxelsize_y); \
name##_image.pixel_size_half = (float2) (name##_voxelsize_x / 2.f, name##_voxelsize_y / 2.f);

#define DEF_IMAGEV_STRUCT(name) \
cl_imagev name##_image; \
name##_image.data_x = name##_x; \
name##_image.data_y = name##_y; \
name##_image.data_z = name##_z; \
name##_image.stride_x = name##_stride_x; \
name##_image.stride_y = name##_stride_y; \
name##_image.stride_z = name##_stride_z; \
name##_image.stride_offset = name##_stride_offset; \
name##_image.idz = 0; \
name##_image.resolution = (int2) (name##_res_x, name##_res_y); \
name##_image.fresolution = convert_float2(name##_image.resolution); \
name##_image.pixel_size = (float2) (name##_voxelsize_x, name##_voxelsize_y); \
name##_image.pixel_size_half = (float2) (name##_voxelsize_x / 2.f, name##_voxelsize_y / 2.f);

#define bsample(name, pos) bsample_impl(&name##_image, pos)
#define bsamplev(name, pos) bsamplev_impl(&name##_image, pos)
#define nsample(name, pos) nsample_impl(&name##_image, pos)
#define nsamplev(name, pos) nsamplev_impl(&name##_image, pos)
#define isample(name, pos) isample_impl(&name##_image, pos)
#define isamplev(name, pos) isamplev_impl(&name##_image, pos)
#define image_write(name, pos, value) image_write_impl(&name##_image, pos, value)
#define image_writev(name, pos, value) image_writev_impl(&name##_image, pos, value)

#define image_pixel_size(name) name##_image.pixel_size
#define image_pixel_size_half(name) name##_image.pixel_size_half
#define image_resolution(name) name##_image.resolution
#define image_fresolution(name) name##_image.fresolution

#endif