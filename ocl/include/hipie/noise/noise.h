#ifndef __ie_noise_h
#define __ie_noise_h

#include "hash_impl.h"


// Gradient Noise

// 2d
static float noise2(float seed, float2 pos)
{
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 ga = zchash_2_2(seed, p + (float2)(0.f, 0.f));
    float2 gb = zchash_2_2(seed, p + (float2)(1.f, 0.f));
    float2 gc = zchash_2_2(seed, p + (float2)(0.f, 1.f));
    float2 gd = zchash_2_2(seed, p + (float2)(1.f, 1.f));
    
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
static float3 noise2d(float seed, float2 pos)
{
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float2 ga = zchash_2_2(seed, p + (float2)(0.f, 0.f));
    float2 gb = zchash_2_2(seed, p + (float2)(1.f, 0.f));
    float2 gc = zchash_2_2(seed, p + (float2)(0.f, 1.f));
    float2 gd = zchash_2_2(seed, p + (float2)(1.f, 1.f));
    
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
static float pnoise2(float seed, float2 pos, int2 period)
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 ga = zchash_2_2(seed, fmod2r(p + (float2)(0.f, 0.f), fperiod));
    float2 gb = zchash_2_2(seed, fmod2r(p + (float2)(1.f, 0.f), fperiod));
    float2 gc = zchash_2_2(seed, fmod2r(p + (float2)(0.f, 1.f), fperiod));
    float2 gd = zchash_2_2(seed, fmod2r(p + (float2)(1.f, 1.f), fperiod));
    
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
static float3 pnoise2d(float seed, float2 pos, int2 period)
{
    float2 fperiod = convert_float2(period);
    pos *= fperiod;
    float2 p;
    float2 w = fract(pos, &p);
    
    float2 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float2 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float2 ga = zchash_2_2(seed, fmod2r(p + (float2)(0.f, 0.f), fperiod));
    float2 gb = zchash_2_2(seed, fmod2r(p + (float2)(1.f, 0.f), fperiod));
    float2 gc = zchash_2_2(seed, fmod2r(p + (float2)(0.f, 1.f), fperiod));
    float2 gd = zchash_2_2(seed, fmod2r(p + (float2)(1.f, 1.f), fperiod));
    
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
static float noise3(float seed, float3 pos)
{
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 ga = zchash_3_3(seed, p + (float3)(0.f, 0.f, 0.f));
    float3 gb = zchash_3_3(seed, p + (float3)(1.f, 0.f, 0.f));
    float3 gc = zchash_3_3(seed, p + (float3)(0.f, 1.f, 0.f));
    float3 gd = zchash_3_3(seed, p + (float3)(1.f, 1.f, 0.f));
    float3 ge = zchash_3_3(seed, p + (float3)(0.f, 0.f, 1.f));
    float3 gf = zchash_3_3(seed, p + (float3)(1.f, 0.f, 1.f));
    float3 gg = zchash_3_3(seed, p + (float3)(0.f, 1.f, 1.f));
    float3 gh = zchash_3_3(seed, p + (float3)(1.f, 1.f, 1.f));
    
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
static float4 noise3d(float seed, float3 pos)
{
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float3 ga = zchash_3_3(seed, p + (float3)(0.f, 0.f, 0.f));
    float3 gb = zchash_3_3(seed, p + (float3)(1.f, 0.f, 0.f));
    float3 gc = zchash_3_3(seed, p + (float3)(0.f, 1.f, 0.f));
    float3 gd = zchash_3_3(seed, p + (float3)(1.f, 1.f, 0.f));
    float3 ge = zchash_3_3(seed, p + (float3)(0.f, 0.f, 1.f));
    float3 gf = zchash_3_3(seed, p + (float3)(1.f, 0.f, 1.f));
    float3 gg = zchash_3_3(seed, p + (float3)(0.f, 1.f, 1.f));
    float3 gh = zchash_3_3(seed, p + (float3)(1.f, 1.f, 1.f));
    
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
static float pnoise3(float seed, float3 pos, int3 period)
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 ga = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 0.f, 0.f), fperiod));
    float3 gb = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 0.f, 0.f), fperiod));
    float3 gc = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 1.f, 0.f), fperiod));
    float3 gd = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 1.f, 0.f), fperiod));
    float3 ge = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 0.f, 1.f), fperiod));
    float3 gf = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 0.f, 1.f), fperiod));
    float3 gg = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 1.f, 1.f), fperiod));
    float3 gh = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 1.f, 1.f), fperiod));
    
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
static float4 pnoise3d(float seed, float3 pos, int3 period)
{
    float3 fperiod = convert_float3(period);
    pos *= fperiod;
    float3 p;
    float3 w = fract(pos, &p);
    
    float3 u = w * w * w * (w * (w * 6.f - 15.f) + 10.f);
    float3 du = 30.f * w * w * (w * (w - 2.f) + 1.f);
    float3 ga = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 0.f, 0.f), fperiod));
    float3 gb = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 0.f, 0.f), fperiod));
    float3 gc = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 1.f, 0.f), fperiod));
    float3 gd = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 1.f, 0.f), fperiod));
    float3 ge = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 0.f, 1.f), fperiod));
    float3 gf = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 0.f, 1.f), fperiod));
    float3 gg = zchash_3_3(seed, fmod3r(p + (float3)(0.f, 1.f, 1.f), fperiod));
    float3 gh = zchash_3_3(seed, fmod3r(p + (float3)(1.f, 1.f, 1.f), fperiod));
    
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
#endif