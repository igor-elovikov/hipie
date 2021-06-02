#ifndef __ie_noise_h
#define __ie_noise_h

#include "random.h"

static float manhattan_dist(float3 p)
{
    float3 ap = fabs(p);
    return ap.x + ap.y + ap.z;
}

static float chebyshev_dist(float3 p)
{
    float3 ap = fabs(p);
    return fmax(ap.x, fmax(ap.y, ap.z));
}

static float minkowski_dist(float3 p, float mp)
{
    float3 ap = fabs(p);
    return pow(pow(ap.x, mp) + pow(ap.y, mp) + pow(ap.z, mp), 1.0f / mp);
}

static float manhattan_dist2(float2 p)
{
    float2 ap = fabs(p);
    return ap.x + ap.y;
}

static float chebyshev_dist2(float2 p)
{
    float2 ap = fabs(p);
    return fmax(ap.x, ap.y);
}

static float minkowski_dist2(float2 p, float mp)
{
    float2 ap = fabs(p);
    return pow(pow(ap.x, mp) + pow(ap.y, mp), 1.0f / mp);
}

// hash wrappers (+ zero centered)

static float hash_1_1(float v)
{
    return VEXrandom_1_1(v);
}

static float zchash_1_1(float v)
{
    return VEXrandom_1_1(v) * 2.f - 1.f;
}
static float2 hash_1_2(float v)
{
    return VEXrandom_1_2(v);
}

static float2 zchash_1_2(float v)
{
    return VEXrandom_1_2(v) * 2.f - 1.f;
}
static float3 hash_1_3(float v)
{
    return VEXrandom_1_3(v);
}

static float3 zchash_1_3(float v)
{
    return VEXrandom_1_3(v) * 2.f - 1.f;
}
static float4 hash_1_4(float v)
{
    return VEXrandom_1_4(v);
}

static float4 zchash_1_4(float v)
{
    return VEXrandom_1_4(v) * 2.f - 1.f;
}
static float hash_2_1(float2 v)
{
    return VEXrandom_2_1(v.x, v.y);
}

static float zchash_2_1(float2 v)
{
    return VEXrandom_2_1(v.x, v.y) * 2.f - 1.f;
}
static float2 hash_2_2(float2 v)
{
    return VEXrandom_2_2(v.x, v.y);
}

static float2 zchash_2_2(float2 v)
{
    return VEXrandom_2_2(v.x, v.y) * 2.f - 1.f;
}
static float3 hash_2_3(float2 v)
{
    return VEXrandom_2_3(v.x, v.y);
}

static float3 zchash_2_3(float2 v)
{
    return VEXrandom_2_3(v.x, v.y) * 2.f - 1.f;
}
static float4 hash_2_4(float2 v)
{
    return VEXrandom_2_4(v.x, v.y);
}

static float4 zchash_2_4(float2 v)
{
    return VEXrandom_2_4(v.x, v.y) * 2.f - 1.f;
}
static float hash_3_1(float3 v)
{
    return VEXrandom_3_1(v.x, v.y, v.z);
}

static float zchash_3_1(float3 v)
{
    return VEXrandom_3_1(v.x, v.y, v.z) * 2.f - 1.f;
}
static float2 hash_3_2(float3 v)
{
    return VEXrandom_3_2(v.x, v.y, v.z);
}

static float2 zchash_3_2(float3 v)
{
    return VEXrandom_3_2(v.x, v.y, v.z) * 2.f - 1.f;
}
static float3 hash_3_3(float3 v)
{
    return VEXrandom_3_3(v.x, v.y, v.z);
}

static float3 zchash_3_3(float3 v)
{
    return VEXrandom_3_3(v.x, v.y, v.z) * 2.f - 1.f;
}
static float4 hash_3_4(float3 v)
{
    return VEXrandom_3_4(v.x, v.y, v.z);
}

static float4 zchash_3_4(float3 v)
{
    return VEXrandom_3_4(v.x, v.y, v.z) * 2.f - 1.f;
}
static float hash_4_1(float4 v)
{
    return VEXrandom_4_1(v.x, v.y, v.z, v.w);
}

static float zchash_4_1(float4 v)
{
    return VEXrandom_4_1(v.x, v.y, v.z, v.w) * 2.f - 1.f;
}
static float2 hash_4_2(float4 v)
{
    return VEXrandom_4_2(v.x, v.y, v.z, v.w);
}

static float2 zchash_4_2(float4 v)
{
    return VEXrandom_4_2(v.x, v.y, v.z, v.w) * 2.f - 1.f;
}
static float3 hash_4_3(float4 v)
{
    return VEXrandom_4_3(v.x, v.y, v.z, v.w);
}

static float3 zchash_4_3(float4 v)
{
    return VEXrandom_4_3(v.x, v.y, v.z, v.w) * 2.f - 1.f;
}
static float4 hash_4_4(float4 v)
{
    return VEXrandom_4_4(v.x, v.y, v.z, v.w);
}

static float4 zchash_4_4(float4 v)
{
    return VEXrandom_4_4(v.x, v.y, v.z, v.w) * 2.f - 1.f;
}
// Voronoi Noise

// 2d
static void vnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void cvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mkvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    float minkowski_number    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void pvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pcvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmkvnoise2(float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period,
    float minkowski_number    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(0.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_2_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

// 3d
static void vnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void cvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mkvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    float minkowski_number    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void pvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pcvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmkvnoise3(float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period,
    float minkowski_number    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = 1000.f;
    float F2 = 1000.f;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(0.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? hash_3_1(hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? hc : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? hc : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

// Smooth Voronoi Noise

// 2d
static float svnoise2(float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = length(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float msvnoise2(float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float csvnoise2(float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float mksvnoise2(float2 pos, float jitter, float falloff,
    float minkowski_number    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float psvnoise2(float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = length(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmsvnoise2(float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pcsvnoise2(float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmksvnoise2(float2 pos, float jitter, float falloff,
    int2 period,
    float minkowski_number    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(0.5f);

    float res = 0.f;
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = (hash_2_2(hc) - half_one) * jitter + half_one;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

// 3d
static float svnoise3(float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float msvnoise3(float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float csvnoise3(float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float mksvnoise3(float3 pos, float jitter, float falloff,
    float minkowski_number    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float psvnoise3(float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmsvnoise3(float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pcsvnoise3(float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmksvnoise3(float3 pos, float jitter, float falloff,
    int3 period,
    float minkowski_number    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(0.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = (hash_3_3(hc) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

// Gradient Noise

// 2d
static float noise2(float2 pos)
{
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 ga = zchash_2_2(p + (float2)(0.f, 0.f));
    float2 gb = zchash_2_2(p + (float2)(1.f, 0.f));
    float2 gc = zchash_2_2(p + (float2)(0.f, 1.f));
    float2 gd = zchash_2_2(p + (float2)(1.f, 1.f));
    
    float va = dot(ga, w - (float2)(0.f, 0.f));
    float vb = dot(gb, w - (float2)(1.f, 0.f));
    float vc = dot(gc, w - (float2)(0.f, 1.f));
    float vd = dot(gd, w - (float2)(1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.x * u.y * (va - vb - vc + vd);

    return nv;
}
static float3 noise2d(float2 pos)
{
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float2 ga = zchash_2_2(p + (float2)(0.f, 0.f));
    float2 gb = zchash_2_2(p + (float2)(1.f, 0.f));
    float2 gc = zchash_2_2(p + (float2)(0.f, 1.f));
    float2 gd = zchash_2_2(p + (float2)(1.f, 1.f));
    
    float va = dot(ga, w - (float2)(0.f, 0.f));
    float vb = dot(gb, w - (float2)(1.f, 0.f));
    float vc = dot(gc, w - (float2)(0.f, 1.f));
    float vd = dot(gd, w - (float2)(1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.x * u.y * (va - vb - vc + vd);

    float2 d = ga + 
             u.x * (gb - ga) + 
             u.y * (gc - ga) + 
             u.x * u.y * (ga - gb - gc + gd) + 
             du * (u.yx * (va - vb - vc + vd) + (float2)(vb, vc) - va);

    return (float3)(nv, d);
}
static float pnoise2(float2 pos, int2 period)
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 ga = zchash_2_2(fmod2r(p + (float2)(0.f, 0.f), fperiod));
    float2 gb = zchash_2_2(fmod2r(p + (float2)(1.f, 0.f), fperiod));
    float2 gc = zchash_2_2(fmod2r(p + (float2)(0.f, 1.f), fperiod));
    float2 gd = zchash_2_2(fmod2r(p + (float2)(1.f, 1.f), fperiod));
    
    float va = dot(ga, w - (float2)(0.f, 0.f));
    float vb = dot(gb, w - (float2)(1.f, 0.f));
    float vc = dot(gc, w - (float2)(0.f, 1.f));
    float vd = dot(gd, w - (float2)(1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.x * u.y * (va - vb - vc + vd);

    return nv;
}
static float3 pnoise2d(float2 pos, int2 period)
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float2 ga = zchash_2_2(fmod2r(p + (float2)(0.f, 0.f), fperiod));
    float2 gb = zchash_2_2(fmod2r(p + (float2)(1.f, 0.f), fperiod));
    float2 gc = zchash_2_2(fmod2r(p + (float2)(0.f, 1.f), fperiod));
    float2 gd = zchash_2_2(fmod2r(p + (float2)(1.f, 1.f), fperiod));
    
    float va = dot(ga, w - (float2)(0.f, 0.f));
    float vb = dot(gb, w - (float2)(1.f, 0.f));
    float vc = dot(gc, w - (float2)(0.f, 1.f));
    float vd = dot(gd, w - (float2)(1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.x * u.y * (va - vb - vc + vd);

    float2 d = ga + 
             u.x * (gb - ga) + 
             u.y * (gc - ga) + 
             u.x * u.y * (ga - gb - gc + gd) + 
             du * (u.yx * (va - vb - vc + vd) + (float2)(vb, vc) - va);

    return (float3)(nv, d);
}
// 3d
static float noise3(float3 pos)
{
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 ga = hash_3_3(p + (float3)(0.f, 0.f, 0.f)) * 2.f - 1.f;
    float3 gb = hash_3_3(p + (float3)(1.f, 0.f, 0.f)) * 2.f - 1.f;
    float3 gc = hash_3_3(p + (float3)(0.f, 1.f, 0.f)) * 2.f - 1.f;
    float3 gd = hash_3_3(p + (float3)(1.f, 1.f, 0.f)) * 2.f - 1.f;
    float3 ge = hash_3_3(p + (float3)(0.f, 0.f, 1.f)) * 2.f - 1.f;
    float3 gf = hash_3_3(p + (float3)(1.f, 0.f, 1.f)) * 2.f - 1.f;
    float3 gg = hash_3_3(p + (float3)(0.f, 1.f, 1.f)) * 2.f - 1.f;
    float3 gh = hash_3_3(p + (float3)(1.f, 1.f, 1.f)) * 2.f - 1.f;
    
    float va = dot(ga, w - (float3)(0.f, 0.f, 0.f));
    float vb = dot(gb, w - (float3)(1.f, 0.f, 0.f));
    float vc = dot(gc, w - (float3)(0.f, 1.f, 0.f));
    float vd = dot(gd, w - (float3)(1.f, 1.f, 0.f));
    float ve = dot(ge, w - (float3)(0.f, 0.f, 1.f));
    float vf = dot(gf, w - (float3)(1.f, 0.f, 1.f));
    float vg = dot(gg, w - (float3)(0.f, 1.f, 1.f));
    float vh = dot(gh, w - (float3)(1.f, 1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
    return nv;
}
static float4 noise3d(float3 pos)
{
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float3 ga = hash_3_3(p + (float3)(0.f, 0.f, 0.f)) * 2.f - 1.f;
    float3 gb = hash_3_3(p + (float3)(1.f, 0.f, 0.f)) * 2.f - 1.f;
    float3 gc = hash_3_3(p + (float3)(0.f, 1.f, 0.f)) * 2.f - 1.f;
    float3 gd = hash_3_3(p + (float3)(1.f, 1.f, 0.f)) * 2.f - 1.f;
    float3 ge = hash_3_3(p + (float3)(0.f, 0.f, 1.f)) * 2.f - 1.f;
    float3 gf = hash_3_3(p + (float3)(1.f, 0.f, 1.f)) * 2.f - 1.f;
    float3 gg = hash_3_3(p + (float3)(0.f, 1.f, 1.f)) * 2.f - 1.f;
    float3 gh = hash_3_3(p + (float3)(1.f, 1.f, 1.f)) * 2.f - 1.f;
    
    float va = dot(ga, w - (float3)(0.f, 0.f, 0.f));
    float vb = dot(gb, w - (float3)(1.f, 0.f, 0.f));
    float vc = dot(gc, w - (float3)(0.f, 1.f, 0.f));
    float vd = dot(gd, w - (float3)(1.f, 1.f, 0.f));
    float ve = dot(ge, w - (float3)(0.f, 0.f, 1.f));
    float vf = dot(gf, w - (float3)(1.f, 0.f, 1.f));
    float vg = dot(gg, w - (float3)(0.f, 1.f, 1.f));
    float vh = dot(gh, w - (float3)(1.f, 1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
    float3 d = ga + 
             u.x * (gb - ga) + 
             u.y * (gc - ga) + 
             u.z * (ge - ga) + 
             u.x * u.y * (ga - gb - gc + gd) + 
             u.y * u.z * (ga - gc - ge + gg) + 
             u.z * u.x * (ga - gb - ge + gf) + 
             u.x * u.y * u.z * (-ga + gb + gc - gd + ge - gf - gg + gh) +   
             
             du * ((float3)(vb - va, vc - va, ve - va) + 
                   u.yzx * (float3)(va - vb - vc + vd, va - vc - ve + vg, va - vb - ve + vf) + 
                   u.zxy * (float3)(va - vb - ve + vf, va - vb - vc + vd, va - vc - ve + vg) + 
                   u.yzx * u.zxy*(-va + vb + vc - vd + ve - vf - vg + vh) );

    return (float4)(nv, d);
}
static float pnoise3(float3 pos, int3 period)
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 ga = hash_3_3(fmod3r(p + (float3)(0.f, 0.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gb = hash_3_3(fmod3r(p + (float3)(1.f, 0.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gc = hash_3_3(fmod3r(p + (float3)(0.f, 1.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gd = hash_3_3(fmod3r(p + (float3)(1.f, 1.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 ge = hash_3_3(fmod3r(p + (float3)(0.f, 0.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gf = hash_3_3(fmod3r(p + (float3)(1.f, 0.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gg = hash_3_3(fmod3r(p + (float3)(0.f, 1.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gh = hash_3_3(fmod3r(p + (float3)(1.f, 1.f, 1.f), fperiod)) * 2.f - 1.f;
    
    float va = dot(ga, w - (float3)(0.f, 0.f, 0.f));
    float vb = dot(gb, w - (float3)(1.f, 0.f, 0.f));
    float vc = dot(gc, w - (float3)(0.f, 1.f, 0.f));
    float vd = dot(gd, w - (float3)(1.f, 1.f, 0.f));
    float ve = dot(ge, w - (float3)(0.f, 0.f, 1.f));
    float vf = dot(gf, w - (float3)(1.f, 0.f, 1.f));
    float vg = dot(gg, w - (float3)(0.f, 1.f, 1.f));
    float vh = dot(gh, w - (float3)(1.f, 1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
    return nv;
}
static float4 pnoise3d(float3 pos, int3 period)
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float3 ga = hash_3_3(fmod3r(p + (float3)(0.f, 0.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gb = hash_3_3(fmod3r(p + (float3)(1.f, 0.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gc = hash_3_3(fmod3r(p + (float3)(0.f, 1.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 gd = hash_3_3(fmod3r(p + (float3)(1.f, 1.f, 0.f), fperiod)) * 2.f - 1.f;
    float3 ge = hash_3_3(fmod3r(p + (float3)(0.f, 0.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gf = hash_3_3(fmod3r(p + (float3)(1.f, 0.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gg = hash_3_3(fmod3r(p + (float3)(0.f, 1.f, 1.f), fperiod)) * 2.f - 1.f;
    float3 gh = hash_3_3(fmod3r(p + (float3)(1.f, 1.f, 1.f), fperiod)) * 2.f - 1.f;
    
    float va = dot(ga, w - (float3)(0.f, 0.f, 0.f));
    float vb = dot(gb, w - (float3)(1.f, 0.f, 0.f));
    float vc = dot(gc, w - (float3)(0.f, 1.f, 0.f));
    float vd = dot(gd, w - (float3)(1.f, 1.f, 0.f));
    float ve = dot(ge, w - (float3)(0.f, 0.f, 1.f));
    float vf = dot(gf, w - (float3)(1.f, 0.f, 1.f));
    float vg = dot(gg, w - (float3)(0.f, 1.f, 1.f));
    float vh = dot(gh, w - (float3)(1.f, 1.f, 1.f));
	
    float nv = va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
    float3 d = ga + 
             u.x * (gb - ga) + 
             u.y * (gc - ga) + 
             u.z * (ge - ga) + 
             u.x * u.y * (ga - gb - gc + gd) + 
             u.y * u.z * (ga - gc - ge + gg) + 
             u.z * u.x * (ga - gb - ge + gf) + 
             u.x * u.y * u.z * (-ga + gb + gc - gd + ge - gf - gg + gh) +   
             
             du * ((float3)(vb - va, vc - va, ve - va) + 
                   u.yzx * (float3)(va - vb - vc + vd, va - vc - ve + vg, va - vb - ve + vf) + 
                   u.zxy * (float3)(va - vb - ve + vf, va - vb - vc + vd, va - vc - ve + vg) + 
                   u.yzx * u.zxy*(-va + vb + vc - vd + ve - vf - vg + vh) );

    return (float4)(nv, d);
}
// Voronoise

// 2d
static float voronoise2(float2 pos, 
    float u, float v )
{
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3( p + g )*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = length(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float mvoronoise2(float2 pos, 
    float u, float v )
{
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3( p + g )*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = manhattan_dist2(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float cvoronoise2(float2 pos, 
    float u, float v )
{
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3( p + g )*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = chebyshev_dist2(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float mkvoronoise2(float2 pos, 
    float u, float v,
    float minkowski_number )
{
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3( p + g )*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = minkowski_dist2(r, minkowski_number);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float pvoronoise2(float2 pos, 
    float u, float v,
    int2 period )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3(fmod2r( p + g , fperiod))*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = length(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float pmvoronoise2(float2 pos, 
    float u, float v,
    int2 period )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3(fmod2r( p + g , fperiod))*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = manhattan_dist2(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float pcvoronoise2(float2 pos, 
    float u, float v,
    int2 period )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3(fmod2r( p + g , fperiod))*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = chebyshev_dist2(r);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
static float pmkvoronoise2(float2 pos, 
    float u, float v,
    int2 period,
    float minkowski_number )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
        {
            float2  g = (float2)(x, y);
            float3  o = hash_2_3(fmod2r( p + g , fperiod))*(float3)(u,u,1.0);
            float2  r = g - f + o.xy;
            float d = minkowski_dist2(r, minkowski_number);
            float w = pow( 1.f - smoothstep(0.f, 1.414f, d), k );
            va += w*o.z;
            wt += w;
        }

    return va/wt;
}
// 3d
static float voronoise3(float3 pos, 
    float u, float v )
{
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4( p + g )*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = length(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float mvoronoise3(float3 pos, 
    float u, float v )
{
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4( p + g )*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = manhattan_dist(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float cvoronoise3(float3 pos, 
    float u, float v )
{
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4( p + g )*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = chebyshev_dist(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float mkvoronoise3(float3 pos, 
    float u, float v,
    float minkowski_number )
{
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4( p + g )*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = minkowski_dist(r, minkowski_number);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float pvoronoise3(float3 pos, 
    float u, float v,
    int3 period )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4(fmod3r( p + g , fperiod))*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = length(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float pmvoronoise3(float3 pos, 
    float u, float v,
    int3 period )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4(fmod3r( p + g , fperiod))*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = manhattan_dist(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float pcvoronoise3(float3 pos, 
    float u, float v,
    int3 period )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4(fmod3r( p + g , fperiod))*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = chebyshev_dist(r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
static float pmkvoronoise3(float3 pos, 
    float u, float v,
    int3 period,
    float minkowski_number )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 f = fract(pos, &p);

    float k = 1.0 + 63.0*pow(1.0-v,4.0);
    float va = 0.0;
    float wt = 0.0;

    for( int x=-2; x<=2; x++ )
        for( int y=-2; y<=2; y++ )
            for( int z=-2; z<=2; z++ )
            {
                float3  g = (float3)(x, y, z);
                float4  o = hash_3_4(fmod3r( p + g , fperiod))*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = minkowski_dist(r, minkowski_number);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, d), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}
#endif