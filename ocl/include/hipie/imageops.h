#ifndef __ie_imageops_h
#define __ie_imageops_h

float bias(float v, float bias)
{
    return (v / ((((1.0f / bias) - 2.0f) * (1.0f - v)) + 1.0f));
}

float gain(float v, float gain)
{
    return v < 0.5f
        ? (bias(v * 2.0f, gain) / 2.0f)
        : (bias(v * 2.0f - 1.0f, 1.0f - gain) / 2.0f + 0.5f);
}

#endif