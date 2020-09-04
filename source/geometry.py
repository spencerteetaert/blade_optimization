def expand_for_fat(pt, mouse_down, fat_thickness):
    v = [pt[0] - mouse_down[0], pt[1] - mouse_down[1]]
    v_norm = [v[0] / (v[0]**2 + v[1]**2)**0.5, v[1] / (v[0]**2 + v[1]**2)**0.5]
    expansion = [fat_thickness * v_norm[0], fat_thickness * v_norm[1]]
    ret = (mouse_down[0] + expansion[0], mouse_down[1] + expansion[1])
    return ret