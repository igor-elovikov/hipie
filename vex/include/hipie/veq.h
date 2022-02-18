#ifndef __ie_vex_veq_h
#define __ie_vex_veq_h

#define QUERY_POINTS 0
#define QUERY_PRIMS 1
#define QUERY_VERTS 2

#include "hipie/array.h"
#include "hipie/geo.h"

struct veq
{
    int query_type = QUERY_POINTS;
    int elems[];
    int geo_idx = 0;

    function veq geo(int input_index)
    {
        geo_idx = input_index;
        return this;
    }

    function veq prims(string pattern)
    {
        veq q;
        q.query_type = QUERY_PRIMS;
        q.geo_idx = geo_idx;
        q.elems = expandprimgroup(geo_idx, pattern);
        return q;
    }

    function veq points(string pattern)
    {
        veq q;
        q.query_type = QUERY_POINTS;
        q.geo_idx = geo_idx;
        q.elems = expandpointgroup(geo_idx, pattern);
        return q;
    }

    function veq vertices(string pattern)
    {
        veq q;
        q.query_type = QUERY_VERTS;
        q.geo_idx = geo_idx;
        q.elems = expandvertexgroup(geo_idx, pattern);
        return q;
    }

    function veq topoints()
    {
        if (query_type == QUERY_POINTS)
        {
            return this;
        }

        if (query_type == QUERY_PRIMS)
        {
            veq q;
            q.query_type = QUERY_POINTS;
            q.geo_idx = geo_idx;

            int total_points = 0;
            foreach (int prim; elems) total_points += primvertexcount(geo_idx, prim);

            int result[];
            resize(result, total_points);

            total_points = 0;

            foreach (int prim; elems)
            {
                int prim_pts[] = primpoints(geo_idx, prim);
                foreach (int pt; prim_pts)
                {
                    result[total_points] = pt;
                    total_points++;
                }
            }

            removeduplicates_sorted(result);
            q.elems = result;

            return q;
        }

        if (query_type == QUERY_VERTS)
        {
            veq q;
            q.query_type = QUERY_POINTS;
            q.geo_idx = geo_idx;

            int query_size = len(elems);
            int result[];
            resize(result, query_size);

            for (int index = 0; index < query_size; index++)
            {
                result[index] = vertexpoint(geo_idx, elems[index]);
            }

            removeduplicates_sorted(result);
            q.elems = result;

            return q;

        }

        return this;
    }

    function veq toprims()
    {
        if (query_type == QUERY_PRIMS)
        {
            return this;
        }

        if (query_type == QUERY_POINTS)
        {
            veq q;
            q.query_type = QUERY_PRIMS;
            q.geo_idx = geo_idx;

            int result[];
            foreach (int pt; elems)
            {
                push(result, pointprims(geo_idx, pt));
            }

            removeduplicates_sorted(result);
            q.elems = result;

            return q;
        }

        if (query_type == QUERY_VERTS)
        {
            veq q;
            q.query_type = QUERY_PRIMS;
            q.geo_idx = geo_idx;

            int query_size = len(elems);
            int result[];
            resize(result, query_size);

            for (int index = 0; index < query_size; index++)
            {
                result[index] = vertexprim(geo_idx, elems[index]);
            }

            removeduplicates_sorted(result);
            q.elems = result;

            return q;
        }

        return this;
    }

    function veq setgroup(string group_name)
    {
        if (query_type == QUERY_POINTS)
        {
            foreach (int e; elems)
            {
                setpointgroup(geo_idx, group_name, e, 1);
            }
        }

        if (query_type == QUERY_PRIMS)
        {
            foreach (int e; elems)
            {
                setprimgroup(geo_idx, group_name, e, 1);
            }
        }

        if (query_type == QUERY_VERTS)
        {
            foreach (int e; elems)
            {
                setvertexgroup(geo_idx, group_name, e, -1, 1);
            }
        }

        return this;
    }

    function veq removegroup(string group_name)
    {
        if (query_type == QUERY_POINTS)
        {
            foreach (int e; elems)
            {
                setpointgroup(geo_idx, group_name, e, 0);
            }
        }

        if (query_type == QUERY_PRIMS)
        {
            foreach (int e; elems)
            {
                setprimgroup(geo_idx, group_name, e, 0);
            }
        }

        if (query_type == QUERY_VERTS)
        {
            foreach (int e; elems)
            {
                setvertexgroup(geo_idx, group_name, e, -1, 0);
            }
        }

        return this;
    }

    function veq togglegroup(string group_name)
    {
        if (query_type == QUERY_POINTS)
        {
            foreach (int e; elems)
            {
                setpointgroup(geo_idx, group_name, e, 0, "toggle");
            }
        }

        if (query_type == QUERY_PRIMS)
        {
            foreach (int e; elems)
            {
                setprimgroup(geo_idx, group_name, e, 0, "toggle");
            }
        }

        if (query_type == QUERY_VERTS)
        {
            foreach (int e; elems)
            {
                setvertexgroup(geo_idx, group_name, e, -1, 0, "toggle");
            }
        }

        return this;
    }

    function veq filter(string pattern)
    {
        int query_size = len(elems);
        string pattern_tokens[];
        resize(pattern_tokens, query_size);

        for (int index = 0; index < query_size; index++)
        {
            pattern_tokens[index] = itoa(elems[index]);
        }

        string main_pattern = join(pattern_tokens, " ");

        string filter_tokens[] = split(pattern);
        int num_tokens = len(filter_tokens);

        for (int index = 0; index < num_tokens; index++)
        {
            filter_tokens[index] = "^!" + filter_tokens[index];
        }

        string result_pattern = main_pattern + " " + join(filter_tokens, " ");

        veq q;
        q.geo_idx = geo_idx;
        q.query_type = query_type;

        if (query_type == QUERY_POINTS)
        {
            q.elems = expandpointgroup(geo_idx, result_pattern);
        }

        if (query_type == QUERY_PRIMS)
        {
            q.elems = expandprimgroup(geo_idx, result_pattern);
        }

        if (query_type == QUERY_VERTS)
        {
            q.elems = expandvertexgroup(geo_idx, result_pattern);
        }

        return q;
    }

    function int[] elements()
    {
        return elems;
    }

#define DEF_SELECT(type) \
    function type[] select(string attrib_name) \
    { \
        if (query_type == QUERY_POINTS) \
        { \
            return points_attribs(geo_idx, elems, attrib_name); \
        } \
        \
        if (query_type == QUERY_PRIMS) \
        { \
            return prims_attribs(geo_idx, elems, attrib_name); \
        } \
        \
        if (query_type == QUERY_VERTS) \
        { \
            return vertices_attribs(geo_idx, elems, attrib_name); \
        } \
        return {}; \
    } \
    \

DEF_SELECT(float)
DEF_SELECT(int)
DEF_SELECT(vector)
DEF_SELECT(vector2)
DEF_SELECT(vector4)
DEF_SELECT(string)
DEF_SELECT(dict)

#undef DEF_SELECT

    function veq log()
    {
        printf("\nelements: %g", elems);
        return this;
    }

};


#endif

