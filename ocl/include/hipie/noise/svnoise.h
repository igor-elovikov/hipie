#ifndef __ie_svnoise_h
#define __ie_svnoise_h

#include "hash_impl.h"
// Smooth Voronoi Noise

// 2d
static float svnoise2(float seed, float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = length(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float msvnoise2(float seed, float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float csvnoise2(float seed, float2 pos, float jitter, float falloff    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float mksvnoise2(float seed, float2 pos, float jitter, float falloff,
    float minkowski_number    )
{
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = id + offset;
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float psvnoise2(float seed, float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = length(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmsvnoise2(float seed, float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = manhattan_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pcsvnoise2(float seed, float2 pos, float jitter, float falloff,
    int2 period    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = chebyshev_dist2(d);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmksvnoise2(float seed, float2 pos, float jitter, float falloff,
    int2 period,
    float minkowski_number    )
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 id;
    float2 p = fract(pos, &id);

    const float2 half_one = (float2)(.5f);

    float res = 0.f;
    
    for (int x = -2; x < 3; x++)
    {
        for (int y = -2; y < 3; y++)
        {
                float2 offset = (float2)(x, y);
                float2 hc = fmod2r((id + offset), fperiod);
                float2 h = zchash_2_2(seed, hc) * jitter * .5f;
                h += offset;

                float2 d = p - h;
                float dist = minkowski_dist2(d, minkowski_number);
                
                res += exp(-falloff * dist);
                
        }
    }

    return -(1.f / falloff) * log(res);
}

// 3d
static float svnoise3(float seed, float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float msvnoise3(float seed, float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float csvnoise3(float seed, float3 pos, float jitter, float falloff    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float mksvnoise3(float seed, float3 pos, float jitter, float falloff,
    float minkowski_number    )
{
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = id + offset;
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float psvnoise3(float seed, float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = length(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmsvnoise3(float seed, float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = manhattan_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pcsvnoise3(float seed, float3 pos, float jitter, float falloff,
    int3 period    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = chebyshev_dist(d);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

static float pmksvnoise3(float seed, float3 pos, float jitter, float falloff,
    int3 period,
    float minkowski_number    )
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 id;
    float3 p = fract(pos, &id);

    const float3 half_one = (float3)(.5f);
    float res = 0.f;

    for (int x = -1; x < 2; x++)
    {
        for (int y = -1; y < 2; y++)
        {
            for (int z = -1; z < 2; z++)
            {
                float3 offset = (float3)(x, y, z);
                float3 hc = fmod3r((id + offset), fperiod);
                float3 h = zchash_3_3(seed, hc) * jitter * .5f;
                h += offset;

                float3 d = p - h;
                float dist = minkowski_dist(d, minkowski_number);

                res += exp(-falloff * dist);
            }
        }
    }

    return -(1.f / falloff) * log(res);
}

#endif