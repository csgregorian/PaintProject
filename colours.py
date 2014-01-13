def cmyk(color):
    cmyk_scale = 100
    
    r = color[0]
    g = color[1]
    b = color[2]
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / 255.
    m = 1 - g / 255.
    y = 1 - b / 255.

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0,cmyk_scale]
    return (c*cmyk_scale, m*cmyk_scale, y*cmyk_scale, k*cmyk_scale)

def unmap(color):
    r = color//16//16//16//16
    g = color//16//16%256
    b = color%256
    return (r, g, b)
