#ifndef __ie_vex_array_h
#define __ie_vex_array_h

function int removeduplicates_sorted(int input[])
{
    int input_size = len(input);
    if (input_size <= 1) return input_size;

    input = sort(input);
    int tracking_value = input[0];
    int result_size = 1;

    for (int index = 1; index < input_size; index++)
    {
        int value = input[index];
        if (value != tracking_value)
        {
            input[result_size] = value;
            tracking_value = value;
            result_size++;
        }
    }

    if (result_size != input_size) resize(input, result_size);

    return result_size;
}

function int removeduplicates_stable(int input[])
{
    int input_size = len(input);
    if (input_size <= 1) return input_size;

    int sorted_input[] = argsort(input);
    int tracking_value = input[sorted_input[0]];

    int result_size = 1;

    for (int index = 1; index < input_size; index++)
    {
        int value = input[sorted_input[index]];
        if (value != tracking_value)
        {
            sorted_input[result_size] = sorted_input[index];
            tracking_value = value;
            result_size++;
        }
    }


    if (result_size != input_size) resize(sorted_input, result_size);
    input = reorder(input, sort(sorted_input));

    return result_size;
}

#define DEF_REMOVE_VALUE_ALL(type) \
function int removevalue_all(type input[]; type value) \
{ \
    int result = 0; \
    foreach(int index; type v; input) \
    { \
        if (v != value) \
        { \
            input[result] = v; \
            result++; \
        } \
    } \
    if (result != len(input)) resize(input, result); \
    return result; \
} \
//

DEF_REMOVE_VALUE_ALL(int)
DEF_REMOVE_VALUE_ALL(float)
DEF_REMOVE_VALUE_ALL(vector)
DEF_REMOVE_VALUE_ALL(vector2)
DEF_REMOVE_VALUE_ALL(vector4)
DEF_REMOVE_VALUE_ALL(string)

#undef DEF_REMOVE_VALUE_ALL

#endif