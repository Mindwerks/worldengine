def color_prop(color_a, color_b, value_a, value_b, v):
    ip = (v - value_a)/(value_b - value_a)
    p = 1.0 - ip
    ra, ga, ba = color_a
    rb, gb, bb = color_b
    return (ra * p + rb * ip), (ga * p + gb * ip), (ba * p + bb * ip)
