import csv

def load_data(data_path):
    print("Loading data from", data_path)
    file_obj = open(data_path, 'r')
    data = file_obj.readlines()
    file_obj.close()

    header = ['Trial','Pig ID', 'Date', 'Treatment', 'Gender', 'Genetic', 'Live Weight', \
        'Hot Carcass Weight', 'Carcass Yield', 'Cold Carcass Weight', 'Loin Length', \
        'Lon Primal Weight', 'loinhamendbonespecwgt','FD','LD','LEA','AR']
    image_data = []
    xs = []
    ys = []
    indices = []

    # Reads 
    for line in data:
        line_data = line.split(',')
        if len(line_data) > 18:
            image_data += [line_data[0:17]]
            index = 18
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
                if (index >= len(line_data)):
                    break
    
    return header, image_data, xs, ys, indices

def write_data(write_path, data_path, image_names, xs, ys, indices):
    print("Writing data to", write_path)
    temp = []

    # Opens all available image data
    with open(data_path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if row[0] != '':
                temp += [row]

    # Sorts through image data to extract in order of labelling 
    image_data = []
    for name in image_names:
        name_info = name.split("_")
        trial_number = name_info[2].strip()[1:-4]
        pig_id = name_info[1].strip()

        for row in temp:
            if (row[0] == trial_number and row[1] == pig_id):
                image_data += [row]
    
    # Write data to csv file 
    with open(write_path, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        for i in range(0, len(image_data)):
            to_write = image_data[i]
            to_write += ['']
            try:
                to_write += xs[indices[i]:indices[i+1]]
                to_write += [''] 
                to_write += ys[indices[i]:indices[i+1]]
            except:
                to_write += xs[indices[i]:len(xs)]
                to_write += [''] 
                to_write += ys[indices[i]:len(ys)]
            writer.writerow(to_write)