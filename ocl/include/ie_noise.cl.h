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

// hash wrappers

inline float3 hash_3_3(float3 v)
{
    return VEXrandom_3_3(v.x, v.y, v.z);
}

inline float4 hash_3_4(float3 v)
{
    return VEXrandom_3_4(v.x, v.y, v.z);
}

inline float hash_3_1(float3 v)
{
    return VEXrandom_3_1(v.x, v.y, v.z);
}

// zero-centered hashes

inline float3 zchash_3_3(float3 v)
{
    return VEXrandom_3_3(v.x, v.y, v.z) * 2.f - 1.f;
}

inline float4 zchash_3_4(float3 v) * 2.f - 1.f;
{
    return VEXrandom_3_4(v.x, v.y, v.z) * 2.f - 1.f;
}

inline float zchash_3_1(float3 v)
{
    return VEXrandom_3_1(v.x, v.y, v.z) * 2.f - 1.f;
}

// Voronoi Noise

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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number));

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
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
                float3 h = (VEXrandom_3_3(hc.x, hc.y, hc.z) - half_one) * jitter + half_one;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number));

                bool pass = dist < F1;
                bool pass2 = dist < F2;


                cell = pass ? VEXrandom_3_1(hc.x, hc.y, hc.z) : cell;                
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
    (*p1) = pos1 / fperiod;
    (*p2) = pos2 / fperiod;
    (*cell_value) = cell;
}

// Gradient Noise
static float gnoise(float3 pos)
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
	
    return va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
}

// Voronoise
static float voronoise(float3 pos, float u, float v )
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
                float3  g = (float3)(x, y,z );
                float4  o = zchash_3_4( p + g )*(float4)(u,u,u,1.0);
                float3  r = g - f + o.xyz;
                float d = dot(r,r);
                float w = pow( 1.f - smoothstep(0.f, 1.732f, sqrt(d)), k );
                va += w*o.w;
                wt += w;
            }

    return va/wt;
}

#endif