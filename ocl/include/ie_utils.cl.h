#ifndef __ie_utils_h
#define __ie_utils_h

#define INTERSECT_TOLERANCE 0.00001f


// modulo without negative remainder

static float3 fmod3r(float3 lhs, float3 rhs)
{
    return lhs - floor(lhs / rhs);  
}

static float2 fmod2r(float2 lhs, float2 rhs)
{
    return lhs - floor(lhs / rhs); 
}

static float fmodr(float lhs, float rhs)
{
    return lhs - floor(lhs / rhs); 
}


static int imodr(int lhs, int rhs)
{
    int mod = lhs % rhs;
    return mod < 0 ? rhs + mod : mod;
}

static int2 imod2r(int2 lhs, int2 rhs)
{
    int2 mod = lhs % rhs;
    return (int2) (
        mod.x < 0 ? rhs.x + mod.x : mod.x,
        mod.y < 0 ? rhs.y + mod.y : mod.y
    );
}

static int3 imod3r(int3 lhs, int3 rhs)
{
    int3 mod = lhs % rhs;
    return (int3) (
        mod.x < 0 ? rhs.x + mod.x : mod.x,
        mod.y < 0 ? rhs.y + mod.y : mod.y,
        mod.z < 0 ? rhs.z + mod.z : mod.z
    );
}


static bool tri_intersect(float3 ray_origin, float3 ray_direction,
                float3 p0, float3 p1, float3 p2,
                float* hit_dist, float3* uvw, float3* tri_normal)
{
    float3 e0 = p1 - p0;
    float3 e1 = p0 - p2;

    (*tri_normal) = cross(e1, e0);

    float3 e2 = (1.0f / dot((*tri_normal), ray_direction )) * (p0 - ray_origin);
    float3 i = cross(ray_direction, e2);

    (*uvw).y = dot(i, e1);
    (*uvw).z = dot(i, e0);
    (*uvw).x = 1.0f - ((*uvw).y + (*uvw).z);

    (*hit_dist) = dot(*tri_normal, e2);

    return ((*hit_dist) > INTERSECT_TOLERANCE) && all((*uvw) > 0.0f);
}

#define ramp(name, pos) lerpConstant(name##_vals, name##_size, pos)

#define rampv(name, pos) (float3)(lerpConstant(name##_x_vals, name##_x_size, pos), lerpConstant(name##_y_vals, name##_y_size, pos), lerpConstant(name##_z_vals, name##_z_size, pos))

#define volumeload3(idx, name) (float3)(name##_x[idx], name##_y[idx], name##_z[idx])

#define volumestore3(value, idx, name) \
name##_x[idx] = value.x; \
name##_y[idx] = value.y; \
name##_z[idx] = value.z;

#define vdb_sample(name, pos) cnanovdb_sampleF(name##_grid, &name##_acc, pos)
#define vdb_samplev(name, pos) cnanovdb_sampleV(name##_grid, &name##_acc, pos)

#endif