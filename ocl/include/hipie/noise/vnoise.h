#ifndef __ie_vnoise_h
#define __ie_vnoise_h

#include "hash_impl.h"

// Voronoi Noise

// 2d
static void vnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = zchash_2_2(seed, hc) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = length(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? hash_2_1(seed, hc) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = zchash_2_2(seed, hc) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = manhattan_dist2(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? hash_2_1(seed, hc) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void cvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = zchash_2_2(seed, hc) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = chebyshev_dist2(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? hash_2_1(seed, hc) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mkvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    float minkowski_number    )
{
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = zchash_2_2(seed, hc) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = minkowski_dist2(d, minkowski_number);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? hash_2_1(seed, hc) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void pvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = pzchash_2_2(seed, hc, fperiod) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = length(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? phash_2_1(seed, hc, fperiod) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = pzchash_2_2(seed, hc, fperiod) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = manhattan_dist2(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? phash_2_1(seed, hc, fperiod) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pcvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = pzchash_2_2(seed, hc, fperiod) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = chebyshev_dist2(d);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? phash_2_1(seed, hc, fperiod) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmkvnoise2(float seed, float2 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float2* p1, float2* p2,
    int2 period,
    float minkowski_number    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float2 pos1, pos2;

    const float2 half_one = (float2)(.5f);
    
    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            float2 offset = (float2)(x, y);
            float2 hc = id + offset;
            float2 h = pzchash_2_2(seed, hc, fperiod) * jitter * .5f + half_one;
            h += offset;

            float2 d = p - h;
            float dist = minkowski_dist2(d, minkowski_number);

            bool pass = dist < F1;
            bool pass2 = dist < F2;

            cell = pass ? phash_2_1(seed, hc, fperiod) : cell;                
            F2 = pass2 ? dist : F2;
            F2 = pass ? F1 : F2;
            F1 = pass ? dist : F1;
            pos2 = pass2 ? h + id : pos2;
            pos2 = pass ? pos1 : pos2;
            pos1 = pass ? h + id : pos1;
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

// 3d
static void vnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? hash_3_1(seed, hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? hash_3_1(seed, hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void cvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? hash_3_1(seed, hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void mkvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    float minkowski_number    )
{
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? hash_3_1(seed, hc) : cell;                
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1 ;
    (*p2) = pos2 ;
    (*cell_value) = cell;
}

static void pvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = pzchash_3_3(seed, hc, fperiod) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? phash_3_1(seed, hc, fperiod) : cell;
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = pzchash_3_3(seed, hc, fperiod) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? phash_3_1(seed, hc, fperiod) : cell;
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pcvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = pzchash_3_3(seed, hc, fperiod) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? phash_3_1(seed, hc, fperiod) : cell;
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

static void pmkvnoise3(float seed, float3 pos, float jitter, float* cell_value, 
    float* f1, float* f2, float3* p1, float3* p2,
    int3 period,
    float minkowski_number    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    float F1 = FLT_MAX;
    float F2 = FLT_MAX;
    float cell; 

    float3 pos1, pos2;

    const float3 half_one = (float3)(.5f);
    

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = pzchash_3_3(seed, hc, fperiod) * jitter * .5f + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                bool pass = dist < F1;
                bool pass2 = dist < F2;
                cell = pass ? phash_3_1(seed, hc, fperiod) : cell;
                F2 = pass2 ? dist : F2;
                F2 = pass ? F1 : F2;
                F1 = pass ? dist : F1;
                pos2 = pass2 ? h + id : pos2;
                pos2 = pass ? pos1 : pos2;
                pos1 = pass ? h + id : pos1;

            }
        }
    }

    (*f1) = F1;
    (*f2) = F2;
    (*p1) = pos1  / fperiod;
    (*p2) = pos2  / fperiod;
    (*cell_value) = cell;
}

#endif