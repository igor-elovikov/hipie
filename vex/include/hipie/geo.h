#ifndef __ie_vex_geo_h
#define __ie_vex_geo_h

#define DEF_POINTS_ATTRIBS(type) \
function type[] points_attribs(int geo; int points[]; string attrib_name) \
{ \
    type attribs[]; \
    int count = len(points); \
    resize(attribs, count); \
    for (int i = 0; i < count; i++) \
    { \
        attribs[i] = point(geo, attrib_name, points[i]); \
    } \
    return attribs; \
} \
//

#define DEF_PRIMS_ATTRIBS(type) \
function type[] prims_attribs(int geo; int prims[]; string attrib_name) \
{ \
    type attribs[]; \
    int count = len(prims); \
    resize(attribs, count); \
    for (int i = 0; i < count; i++) \
    { \
        attribs[i] = prim(geo, attrib_name, prims[i]); \
    } \
    return attribs; \
} \
//

#define DEF_VERTICES_ATTRIBS(type) \
function type[] vertices_attribs(int geo; int vertices[]; string attrib_name) \
{ \
    type attribs[]; \
    int count = len(vertices); \
    resize(attribs, count); \
    for (int i = 0; i < count; i++) \
    { \
        attribs[i] = vertex(geo, attrib_name, vertices[i]); \
    } \
    return attribs; \
} \
//


DEF_POINTS_ATTRIBS(float)
DEF_POINTS_ATTRIBS(vector)
DEF_POINTS_ATTRIBS(vector2)
DEF_POINTS_ATTRIBS(vector4)
DEF_POINTS_ATTRIBS(string)
DEF_POINTS_ATTRIBS(dict)

DEF_PRIMS_ATTRIBS(float)
DEF_PRIMS_ATTRIBS(vector)
DEF_PRIMS_ATTRIBS(vector2)
DEF_PRIMS_ATTRIBS(vector4)
DEF_PRIMS_ATTRIBS(string)
DEF_PRIMS_ATTRIBS(dict)

DEF_VERTICES_ATTRIBS(float)
DEF_VERTICES_ATTRIBS(vector)
DEF_VERTICES_ATTRIBS(vector2)
DEF_VERTICES_ATTRIBS(vector4)
DEF_VERTICES_ATTRIBS(string)
DEF_VERTICES_ATTRIBS(dict)

#undef DEF_POINTS_ATTRIBS
#undef DEF_PRIMS_ATTRIBS
#undef DEF_VERTICES_ATTRIBS

#endif