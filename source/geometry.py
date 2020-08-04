def expand_for_fat(pt, mouse_down, fat_thickness):
    v = [pt[0] - mouse_down[0], pt[1] - mouse_down[1]]
    v_norm = [v[0] / (v[0]**2 + v[1]**2)**0.5, v[1] / (v[0]**2 + v[1]**2)**0.5]
    expansion = [fat_thickness * v_norm[0], fat_thickness * v_norm[1]]
    ret = [mouse_down[0] + expansion[0], mouse_down[1] + expansion[1]]
    return ret

# Function to find the circle on  
# which the given three points lie  
def find_circle_center(pts):
    x1, y1 = pts[0]
    x2, y2 = pts[1]
    x3, y3 = pts[2] 
    
    x12 = x1 - x2;  
    x13 = x1 - x3;  
  
    y12 = y1 - y2;  
    y13 = y1 - y3;  
  
    y31 = y3 - y1;  
    y21 = y2 - y1;  
  
    x31 = x3 - x1;  
    x21 = x2 - x1;  
  
    # x1^2 - x3^2  
    sx13 = pow(x1, 2) - pow(x3, 2);  
  
    # y1^2 - y3^2  
    sy13 = pow(y1, 2) - pow(y3, 2);  
  
    sx21 = pow(x2, 2) - pow(x1, 2);  
    sy21 = pow(y2, 2) - pow(y1, 2);  
  
    f = (((sx13) * (x12) + (sy13) * 
          (x12) + (sx21) * (x13) + 
          (sy21) * (x13)) // (2 * 
          ((y31) * (x12) - (y21) * (x13)))); 
              
    g = (((sx13) * (y12) + (sy13) * (y12) + 
          (sx21) * (y13) + (sy21) * (y13)) // 
          (2 * ((x31) * (y12) - (x21) * (y13))));  
  
    c = (-pow(x1, 2) - pow(y1, 2) - 
         2 * g * x1 - 2 * f * y1);  
  
    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0  
    # where centre is (h = -g, k = -f) and  
    # radius r as r^2 = h^2 + k^2 - c  
    h = -g;  
    k = -f;  
    sqr_of_r = h * h + k * k - c;  
  
    # # r is the radius  
    r = sqr_of_r**0.5  
  
    print("Center = (", h, ", ", k, ")");  
    return [h, k], r