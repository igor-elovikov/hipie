#ifndef __ie_svnoise_h
#define __ie_svnoise_h

#include "hash_impl.h"

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