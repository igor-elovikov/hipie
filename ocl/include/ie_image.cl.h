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

static int2 wrap_position(int2 position, int2 resolution)
{
    int2 mod_pos = position % resolution;
    return (int2) (
        mod_pos.x < 0 ? resolution.x + mod_pos.x : mod_pos.x,
        mod_pos.y < 0 ? resolution.y + mod_pos.y : mod_pos.y
    );
}

static float2 fmod_repeat(float2 lv, float2 rv)
{
    float2 out = fmod(lv, rv);
    return (float2) (
        out.x < 0.f ? rv.x + out.x : out.x,
        out.y < 0.f ? rv.y + out.y : out.y
    );
}

#define index_from_position(image, pos) image->stride_offset \
    + pos.x * image->stride_x \
    + pos.y * image->stride_y \
    + image->idz * image->stride_z 

// nearest neighbor sampling (normalized pos)
static float nsample(cl_image* image, float2 pos)
{
    int2 ipos = convert_int2((fmod_repeat(pos, (float2)(1.0f, 1.0f)) * image->fresolution));
    int index = index_from_position(image, ipos);
    return image->data[index];
}

// index position sampling
static float isample(cl_image* image, int2 pos)
{
    int2 ipos = wrap_position(pos, image->resolution);

    int index = image->stride_offset 
                    + ipos.x * image->stride_x
                    + ipos.y * image->stride_y
                    + image->idz * image->stride_z;
    
    return image->data[index];
}

// bilinear sampling (normalized pos)
static float bsample(cl_image* image, float2 pos)
{
    float2 corner_pos = floor((pos - image->pixel_size_half) / image->pixel_size) * image->pixel_size + image->pixel_size_half;
    float2 q11_pos = fmod_repeat(pos - image->pixel_size_half, (float2)(1.0f, 1.0f));

    int2 q11_ipos = convert_int2(q11_pos * image->fresolution);
    int2 q12_ipos = wrap_position((q11_ipos + (int2)(0, 1)), image->resolution);
    int2 q21_ipos = wrap_position((q11_ipos + (int2)(1, 0)), image->resolution);
    int2 q22_ipos = wrap_position((q11_ipos + (int2)(1, 1)), image->resolution);

    int q11_index = index_from_position(image, q11_ipos);
    int q12_index = index_from_position(image, q12_ipos);
    int q21_index = index_from_position(image, q21_ipos);
    int q22_index = index_from_position(image, q22_ipos);

    float2 np = (pos - corner_pos) / image->pixel_size;

    float q11 = image->data[q11_index];
    float q12 = image->data[q12_index];
    float q21 = image->data[q21_index];
    float q22 = image->data[q22_index];

    return (q11 * (1.0f - np.x) + q21 * np.x) * (1.0f - np.y) + (q12 * (1.0f - np.x) + q22 * np.x) * np.y;
}

// bilinear sampling (normalized pos)
static float3 bsample3(cl_imagev* image, float2 pos)
{
    float2 corner_pos = floor((pos - image->pixel_size_half) / image->pixel_size) * image->pixel_size + image->pixel_size_half;
    float2 q11_pos = fmod_repeat(pos - image->pixel_size_half, (float2)(1.0f, 1.0f));

    int2 q11_ipos = convert_int2(q11_pos * image->fresolution);
    int2 q12_ipos = wrap_position((q11_ipos + (int2)(0, 1)), image->resolution);
    int2 q21_ipos = wrap_position((q11_ipos + (int2)(1, 0)), image->resolution);
    int2 q22_ipos = wrap_position((q11_ipos + (int2)(1, 1)), image->resolution);

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

    return (q11 * (1.0f - np.x) + q21 * np.x) * (1.0f - np.y) + (q12 * (1.0f - np.x) + q22 * np.x) * np.y;
}

static void image_write(cl_image* image, int2 pos, float value)
{
    int2 ipos = wrap_position(pos, image->resolution);
    int index = index_from_position(image, ipos);
    image->data[index] = value;
}

static void image_write3(cl_imagev* image, int2 pos, float3 value)
{
    int2 ipos = wrap_position(pos, image->resolution);
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
name##_image.pixel_size_half = (float2) (name##_voxelsize_x / 2.0f, name##_voxelsize_y / 2.0f);

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
name##_image.pixel_size_half = (float2) (name##_voxelsize_x / 2.0f, name##_voxelsize_y / 2.0f);
