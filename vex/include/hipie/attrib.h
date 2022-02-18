#define ATTRIB_TYPE_UNKNOWN -1
#define ATTRIB_TYPE_int 0
#define ATTRIB_TYPE_float 1
#define ATTRIB_TYPE_vector2 1
#define ATTRIB_TYPE_vector 1
#define ATTRIB_TYPE_vector4 1
#define ATTRIB_TYPE_string 2
#define ATTRIB_TYPE_intarray 3
#define ATTRIB_TYPE_floatarray 4
#define ATTRIB_TYPE_stringarray 4
#define ATTRIB_TYPE_dict 6
#define ATTRIB_TYPE_dictarray 7

#define DEF_ATTRIB_TYPE_CHECK(CLASS, TYPE) \
function int is_##CLASS##attribtype_##TYPE(string attrib_name) \
{ \
    return ##CLASS##attribtype(0, attrib_name) == ATTRIB_TYPE_##TYPE; \
} \
//

#define DEF_FLOATATTRIB_TYPE_CHECK(CLASS, TYPE, SIZE) \
function int is_##CLASS##attribtype_##TYPE(string attrib_name) \
{ \
    return ##CLASS##attribtype(0, attrib_name) == ATTRIB_TYPE_##TYPE && ##CLASS##attribsize(0, attrib_name) == SIZE; \
} \
//

#define DEF_ATTRIB_TYPE_CHECKS(CLASS) \
DEF_ATTRIB_TYPE_CHECK(CLASS, int) \
DEF_ATTRIB_TYPE_CHECK(CLASS, string) \
DEF_FLOATATTRIB_TYPE_CHECK(CLASS, float, 1) \
DEF_FLOATATTRIB_TYPE_CHECK(CLASS, vector2, 2) \
DEF_FLOATATTRIB_TYPE_CHECK(CLASS, vector, 3) \
DEF_FLOATATTRIB_TYPE_CHECK(CLASS, vector4, 4) \
//

DEF_ATTRIB_TYPE_CHECKS(point)
DEF_ATTRIB_TYPE_CHECKS(prim)
DEF_ATTRIB_TYPE_CHECKS(vertex)
DEF_ATTRIB_TYPE_CHECKS(detail)

#undef DEF_ATTRIB_TYPE_CHECK
#undef DEF_FLOATATTRIB_TYPE_CHECK
#undef DEF_ATTRIB_TYPE_CHECKS