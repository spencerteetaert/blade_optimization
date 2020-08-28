import csv

def load_data(data_path):
    print("Loading data from", data_path)
    file_obj = open(data_path, 'r')
    data = file_obj.readlines()
    file_obj.close()

    image_data = []
    xs = []
    ys = []
    indices = []
    alignment_points = []

    # Reads 
    for line in data:
        line_data = line.split(',')
        print(line_data)
        if line_data[0] != '':
            print("PASSED")
            image_data += [line_data[0]]
            index = 2
            indices += [len(xs)]
            while True:
                xs += [float(line_data[index])]
                index += 1
                if (line_data[index] == ''):
                    index += 1
                    break
            while True:
                ys += [float(line_data[index])]
                index += 1
                if (line_data[index] == ''):
                    index += 1
                    break
            alignment_points += [[float(line_data[index]), float(line_data[index+1])]]
            
    return image_data, xs, ys, indices, alignment_points

def write_data(write_path, image_names, xs, ys, indices, alignment_points):
    print("Writing data to", write_path)
    temp = []

    with open(write_path, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        for i in range(0, len(image_names)):
            to_write = [image_names[i][0:-4]]
            to_write += ['']
            try:
                to_write += xs[indices[i]:indices[i+1]]
                to_write += [''] 
                to_write += ys[indices[i]:indices[i+1]]
                to_write += [''] 
                to_write += [alignment_points[i][0]]
                to_write += [alignment_points[i][1]]
            except:
                to_write += xs[indices[i]:len(xs)]
                to_write += [''] 
                to_write += ys[indices[i]:len(ys)]
                to_write += [''] 
                to_write += [alignment_points[i][0]]
                to_write += [alignment_points[i][1]]

            writer.writerow(to_write)