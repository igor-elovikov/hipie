// SDF Primitives by Inigo Quilez

float ndot( float2 a, float2 b ) { return a.x*b.x - a.y*b.y; }

float sd_sphere(float3 p, float s)
{
    return length(p) - s;
}

float sd_box(float3 p, float3 b)
{
    float3 q = fabs(p) - b;
    return length(fmax(q, 0.0f)) + fmin(fmax(q.x, fmax(q.y, q.z)), 0.0f);
}

float sd_round_box(float3 p, float3 b, float r)
{
    float3 q = fabs(p) - b;
    return length(fmax(q, 0.0f)) + fmin(fmax(q.x, fmax(q.y, q.z)), 0.0f) - r;    
}

float sd_bounding_box(float3 p, float b, float e)
{
    p = fabs(p) - b;
    float3 q = fabs(p + e) - e;
    return fmin(fmin(
        length(fmax((float3)(p.x, q.y, q.z), 0.0f)) + min(max(p.x, max(q.y, q.z)), 0.0f),
        length(fmax((float3)(q.x, p.y, q.z), 0.0f)) + min(max(q.x, max(p.y, q.z)), 0.0f)),
        length(fmax((float3)(q.x, q.y, p.z), 0.0f)) + min(max(q.x, max(q.y, p.z)), 0.0f)); 
}

float sd_torus(float3 p, float2 t)
{
    float2 q = (float2)(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

float sd_capped_torus(float3 p, float2 sc, float ra, float rb)
{
    p.x = fabs(p.x);
    float k = (sc.y*p.x > sc.x*p.y) ? dot(p.xy, sc) : length(p.xy);
    return sqrt(dot(p,p) + ra*ra - 2.0*ra*k) - rb;
}

float sd_link(float3 p, float le, float r1, float r2 )
{
    float3 q = (float3)(p.x, fmax(fabs(p.y) - le, 0.0f), p.z);
    return length((float2)(length(q.xy) - r1, q.z)) - r2;
}

float sd_cylinder(float3 p, float3 c)
{
    return length(p.xz - c.xy) - c.z;
}

float sd_cone(float3 p, float2 c, float h)
{
    float2 q = h * (float2)(c.x / c.y, -1.0f);
        
    float2 w = (float2)(length(p.xz), p.y);

    float2 a = w - q * clamp(dot(w,q) / dot(q,q), 0.0f, 1.0f);
    float2 b = w - q * (float2)(clamp(w.x/q.x, 0.0f, 1.0f), 1.0f);

    float k = sign(q.y);
    float d = fmin(dot(a, a), dot(b, b));
    float s = fmax(k*(w.x*q.y - w.y*q.x), k*(w.y - q.y));

    return sqrt(d) * sign(s);
}

float sd_inf_cone(float3 p, float2 c)
{
    float2 q = (float2)(length(p.xz), -p.y);
    float d = length(q - c*max(dot(q, c), 0.0f));
    return d * ((q.x*c.y - q.y*c.x < 0.0) ? -1.0 : 1.0);
}

float sd_plane(float3 p, float3 n, float h)
{
    return dot(p, n) + h;
}

float sd_hex_prism(float3 p, float2 h)
{
    const float3 k = (float3)(-0.8660254f, 0.5f, 0.57735f);
    p = fabs(p);
    p.xy -= 2.0f * fmin(dot(k.xy, p.xy), 0.0f) * k.xy;
    float2 d = (float2)(
        length(p.xy - (float2)(clamp(p.x, -k.z*h.x, k.z*h.x), h.x)) * sign(p.y - h.x),
        p.z - h.y 
    );
    return fmin(fmax(d.x, d.y), 0.0f) + length(max(d, 0.0f));
}

float sd_tri_prism(float3 p, float2 h)
{
    float3 q = fabs(p);
    return fmax(q.z - h.y, fmax(q.x*0.866025f + p.y*0.5f, -p.y) - h.x*0.5f);
}

float sd_capsule(float3 p, float3 a, float3 b, float r)
{
    float3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0f, 1.0f);
    return length(pa - ba*h) - r;
}

float sd_vertical_capsule(float3 p, float h, float r)
{
    p.y -= clamp(p.y, 0.0f, h);
    return length(p) - r;
}

float sd_capped_cylinder(float3 p, float h, float r)
{
    float2 d = fabs((float2)(length(p.xz), p.y)) - (float2)(h, r);
    return fmin(fmax(d.x, d.y), 0.0f) + length(fmax(d, 0.0f));
}

float sd_capped_cylinder_ab(float3 p, float3 a, float3 b, float r)
{
    float3  ba = b - a;
    float3  pa = p - a;

    float baba = dot(ba, ba);
    float paba = dot(pa, ba);

    float x = length(pa*baba - ba*paba) - r*baba;
    float y = fabs(paba - baba*0.5) - baba*0.5;
    float x2 = x * x;
    float y2 = y * y * baba;

    float d = (fmax(x, y) < 0.0f) ? -fmin(x2, y2) : (((x > 0.0f) ? x2 : 0.0f) + ((y > 0.0f) ? y2 : 0.0f));

    return sign(d)*sqrt(fabs(d))/baba;
}

float sd_rounded_cylinder(float3 p, float ra, float rb, float h)
{
    float2 d = (float2) (length(p.xz) - 2.0f*ra + rb, fabs(p.y) - h);
    return fmin(fmax(d.x, d.y), 0.0f) + length(max(d, 0.0f)) - rb;
}

float sd_capped_cone(float3 p, float h, float r1, float r2)
{
    float2 q = (float2)(length(p.xz), p.y);

    float2 k1 = (float2)(r2, h);
    float2 k2 = (float2)(r2-r1, 2.0*h);

    float2 ca = (float2)(q.x - fmin(q.x, (q.y < 0.0f) ? r1 : r2), fabs(q.y) - h);
    float2 cb = q - k1 + k2*clamp(dot(k1 - q, k2) / dot(k2, k2), 0.0f, 1.0f );

    float s = (cb.x<0.0 && ca.y<0.0) ? -1.0 : 1.0;

    return s * sqrt(min(dot(ca, ca), dot(cb, cb)));
}

float sd_capped_cone_ab(float3 p, float3 a, float3 b, float ra, float rb)
{
    float rba  = rb - ra;
    float baba = dot(b-a, b-a);
    float papa = dot(p-a, p-a);
    float paba = dot(p-a, b-a) / baba; 

    float x = sqrt(papa - paba*paba*baba);

    float cax = fmax(0.0f, x - ((paba < 0.5f) ? ra : rb));
    float cay = fabs(paba - 0.5f) - 0.5f;

    float k = rba*rba + baba;
    float f = clamp((rba*(x - ra) + paba*baba) / k, 0.0f, 1.0f);

    float cbx = x-ra - f*rba;
    float cby = paba - f;

    float s = (cbx < 0.0f && cay < 0.0f) ? -1.0f : 1.0f;

    return s*sqrt( fmin(cax*cax + cay*cay*baba, 
                       cbx*cbx + cby*cby*baba) );
}

float sd_solid_angle(float3 p, float2 c, float ra)
{
    float2 q = (float2)(length(p.xz), p.y);
    float l = length(q) - ra;
    float m = length(q - c*clamp(dot(q,c), 0.0f, ra));
    return fmax(l, m*sign(c.y*q.x - c.x*q.y));
}

float sd_round_cone(float3 p, float r1, float r2, float h)
{
    float2 q = (float2)(length(p.xz), p.y);

    float b = (r1 - r2) / h;
    float a = sqrt(1.0f- b*b);
    float k = dot(q, (float2)(-b, a));

    if (k < 0.0f) return length(q) - r1;
    if (k > a*h) return length(q - (float2)(0.0f, h)) - r2;
        
    return dot(q, (float2)(a,b)) - r1;
}

float sd_ellipsoid(float3 p, float3 r)
{
    float k0 = length(p / r);
    float k1 = length(p / (r*r));
    return k0 * (k0 - 1.0f) / k1;
}

float sd_rhombus(float3 p, float la, float lb, float h, float ra)
{
    p = fabs(p);
    float2 b = (float2)(la, lb);
    float f = clamp( (ndot(b, b - 2.0f*p.xz)) / dot(b, b), -1.0f, 1.0f);
    float2 q = (float2)(length(p.xz - 0.5f*b*(float2)(1.0f - f,1.0f + f))*sign(p.x*b.y + p.z*b.x - b.x*b.y) - ra, p.y - h);
    return fmin(fmax(q.x, q.y), 0.0f) + length(fmax(q, 0.0f));
}

float sd_octahedron(float3 p, float s)
{
    p = fabs(p);
    float m = p.x + p.y + p.z - s;
    float3 q;
    if( 3.0f*p.x < m ) 
        q = p.xyz;
    else if( 3.0f*p.y < m ) 
        q = p.yzx;
    else if( 3.0f*p.z < m ) 
        q = p.zxy;
    else 
        return m * 0.57735027f;

    float k = clamp(0.5f*(q.z - q.y + s), 0.0f, s); 
    return length((float3)(q.x, q.y - s + k, q.z - k)); 
}
