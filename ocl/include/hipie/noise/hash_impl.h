#ifndef __ie_hash_h
#define __ie_hash_h

#include "random.h"

// hash wrappers (+ zero centered and periodic hashes)

static float hash_1_1(float seed, float v)
{
    v += VEXrandom_1_1(seed) * 5000000.f;
    return VEXrandom_1_1(v);
}

static float phash_1_1(float seed, float v, float period)
{
    return hash_1_1(seed, fmodr(v, period));
}

static float zchash_1_1(float seed, float v)
{
    return hash_1_1(seed, v) * 2.f - 1.f;
}

static float pzchash_1_1(float seed, float v, float period)
{
    return zchash_1_1(seed, fmodr(v, period));
}

static float2 hash_1_2(float seed, float v)
{
    v += VEXrandom_1_1(seed) * 5000000.f;
    return VEXrandom_1_2(v);
}

static float2 phash_1_2(float seed, float v, float period)
{
    return hash_1_2(seed, fmodr(v, period));
}

static float2 zchash_1_2(float seed, float v)
{
    return hash_1_2(seed, v) * 2.f - 1.f;
}

static float2 pzchash_1_2(float seed, float v, float period)
{
    return zchash_1_2(seed, fmodr(v, period));
}

static float3 hash_1_3(float seed, float v)
{
    v += VEXrandom_1_1(seed) * 5000000.f;
    return VEXrandom_1_3(v);
}

static float3 phash_1_3(float seed, float v, float period)
{
    return hash_1_3(seed, fmodr(v, period));
}

static float3 zchash_1_3(float seed, float v)
{
    return hash_1_3(seed, v) * 2.f - 1.f;
}

static float3 pzchash_1_3(float seed, float v, float period)
{
    return zchash_1_3(seed, fmodr(v, period));
}

static float4 hash_1_4(float seed, float v)
{
    v += VEXrandom_1_1(seed) * 5000000.f;
    return VEXrandom_1_4(v);
}

static float4 phash_1_4(float seed, float v, float period)
{
    return hash_1_4(seed, fmodr(v, period));
}

static float4 zchash_1_4(float seed, float v)
{
    return hash_1_4(seed, v) * 2.f - 1.f;
}

static float4 pzchash_1_4(float seed, float v, float period)
{
    return zchash_1_4(seed, fmodr(v, period));
}

static float hash_2_1(float seed, float2 v)
{
    v += VEXrandom_1_2(seed) * 5000000.f;
    return VEXrandom_2_1(v.x, v.y);
}

static float phash_2_1(float seed, float2 v, float2 period)
{
    return hash_2_1(seed, fmod2r(v, period));
}

static float zchash_2_1(float seed, float2 v)
{
    return hash_2_1(seed, v) * 2.f - 1.f;
}

static float pzchash_2_1(float seed, float2 v, float2 period)
{
    return zchash_2_1(seed, fmod2r(v, period));
}

static float2 hash_2_2(float seed, float2 v)
{
    v += VEXrandom_1_2(seed) * 5000000.f;
    return VEXrandom_2_2(v.x, v.y);
}

static float2 phash_2_2(float seed, float2 v, float2 period)
{
    return hash_2_2(seed, fmod2r(v, period));
}

static float2 zchash_2_2(float seed, float2 v)
{
    return hash_2_2(seed, v) * 2.f - 1.f;
}

static float2 pzchash_2_2(float seed, float2 v, float2 period)
{
    return zchash_2_2(seed, fmod2r(v, period));
}

static float3 hash_2_3(float seed, float2 v)
{
    v += VEXrandom_1_2(seed) * 5000000.f;
    return VEXrandom_2_3(v.x, v.y);
}

static float3 phash_2_3(float seed, float2 v, float2 period)
{
    return hash_2_3(seed, fmod2r(v, period));
}

static float3 zchash_2_3(float seed, float2 v)
{
    return hash_2_3(seed, v) * 2.f - 1.f;
}

static float3 pzchash_2_3(float seed, float2 v, float2 period)
{
    return zchash_2_3(seed, fmod2r(v, period));
}

static float4 hash_2_4(float seed, float2 v)
{
    v += VEXrandom_1_2(seed) * 5000000.f;
    return VEXrandom_2_4(v.x, v.y);
}

static float4 phash_2_4(float seed, float2 v, float2 period)
{
    return hash_2_4(seed, fmod2r(v, period));
}

static float4 zchash_2_4(float seed, float2 v)
{
    return hash_2_4(seed, v) * 2.f - 1.f;
}

static float4 pzchash_2_4(float seed, float2 v, float2 period)
{
    return zchash_2_4(seed, fmod2r(v, period));
}

static float hash_3_1(float seed, float3 v)
{
    v += VEXrandom_1_3(seed) * 5000000.f;
    return VEXrandom_3_1(v.x, v.y, v.z);
}

static float phash_3_1(float seed, float3 v, float3 period)
{
    return hash_3_1(seed, fmod3r(v, period));
}

static float zchash_3_1(float seed, float3 v)
{
    return hash_3_1(seed, v) * 2.f - 1.f;
}

static float pzchash_3_1(float seed, float3 v, float3 period)
{
    return zchash_3_1(seed, fmod3r(v, period));
}

static float2 hash_3_2(float seed, float3 v)
{
    v += VEXrandom_1_3(seed) * 5000000.f;
    return VEXrandom_3_2(v.x, v.y, v.z);
}

static float2 phash_3_2(float seed, float3 v, float3 period)
{
    return hash_3_2(seed, fmod3r(v, period));
}

static float2 zchash_3_2(float seed, float3 v)
{
    return hash_3_2(seed, v) * 2.f - 1.f;
}

static float2 pzchash_3_2(float seed, float3 v, float3 period)
{
    return zchash_3_2(seed, fmod3r(v, period));
}

static float3 hash_3_3(float seed, float3 v)
{
    v += VEXrandom_1_3(seed) * 5000000.f;
    return VEXrandom_3_3(v.x, v.y, v.z);
}

static float3 phash_3_3(float seed, float3 v, float3 period)
{
    return hash_3_3(seed, fmod3r(v, period));
}

static float3 zchash_3_3(float seed, float3 v)
{
    return hash_3_3(seed, v) * 2.f - 1.f;
}

static float3 pzchash_3_3(float seed, float3 v, float3 period)
{
    return zchash_3_3(seed, fmod3r(v, period));
}

static float4 hash_3_4(float seed, float3 v)
{
    v += VEXrandom_1_3(seed) * 5000000.f;
    return VEXrandom_3_4(v.x, v.y, v.z);
}

static float4 phash_3_4(float seed, float3 v, float3 period)
{
    return hash_3_4(seed, fmod3r(v, period));
}

static float4 zchash_3_4(float seed, float3 v)
{
    return hash_3_4(seed, v) * 2.f - 1.f;
}

static float4 pzchash_3_4(float seed, float3 v, float3 period)
{
    return zchash_3_4(seed, fmod3r(v, period));
}

static float hash_4_1(float seed, float4 v)
{
    v += VEXrandom_1_4(seed) * 5000000.f;
    return VEXrandom_4_1(v.x, v.y, v.z, v.w);
}

static float phash_4_1(float seed, float4 v, float4 period)
{
    return hash_4_1(seed, fmod4r(v, period));
}

static float zchash_4_1(float seed, float4 v)
{
    return hash_4_1(seed, v) * 2.f - 1.f;
}

static float pzchash_4_1(float seed, float4 v, float4 period)
{
    return zchash_4_1(seed, fmod4r(v, period));
}

static float2 hash_4_2(float seed, float4 v)
{
    v += VEXrandom_1_4(seed) * 5000000.f;
    return VEXrandom_4_2(v.x, v.y, v.z, v.w);
}

static float2 phash_4_2(float seed, float4 v, float4 period)
{
    return hash_4_2(seed, fmod4r(v, period));
}

static float2 zchash_4_2(float seed, float4 v)
{
    return hash_4_2(seed, v) * 2.f - 1.f;
}

static float2 pzchash_4_2(float seed, float4 v, float4 period)
{
    return zchash_4_2(seed, fmod4r(v, period));
}

static float3 hash_4_3(float seed, float4 v)
{
    v += VEXrandom_1_4(seed) * 5000000.f;
    return VEXrandom_4_3(v.x, v.y, v.z, v.w);
}

static float3 phash_4_3(float seed, float4 v, float4 period)
{
    return hash_4_3(seed, fmod4r(v, period));
}

static float3 zchash_4_3(float seed, float4 v)
{
    return hash_4_3(seed, v) * 2.f - 1.f;
}

static float3 pzchash_4_3(float seed, float4 v, float4 period)
{
    return zchash_4_3(seed, fmod4r(v, period));
}

static float4 hash_4_4(float seed, float4 v)
{
    v += VEXrandom_1_4(seed) * 5000000.f;
    return VEXrandom_4_4(v.x, v.y, v.z, v.w);
}

static float4 phash_4_4(float seed, float4 v, float4 period)
{
    return hash_4_4(seed, fmod4r(v, period));
}

static float4 zchash_4_4(float seed, float4 v)
{
    return hash_4_4(seed, v) * 2.f - 1.f;
}

static float4 pzchash_4_4(float seed, float4 v, float4 period)
{
    return zchash_4_4(seed, fmod4r(v, period));
}

#endif