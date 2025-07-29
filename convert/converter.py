import laspy
import numpy as np

def convert_txt_to_laz(input_txt_path, output_laz_path):
    xs, ys, zs = [], [], []

    with open(input_txt_path, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            partes = linea.strip().split()
            if len(partes) == 3:
                x = float(partes[0])
                y = float(partes[1])
                profundidad = float(partes[2]) * 2 * -1
                xs.append(x)
                ys.append(y)
                zs.append(profundidad)

    xs = np.array(xs)
    ys = np.array(ys)
    zs = np.array(zs)

    header = laspy.LasHeader(point_format=3, version="1.2")
    header.offsets = [xs.min(), ys.min(), zs.min()]
    header.scales = [0.01, 0.01, 0.01]

    las = laspy.LasData(header)
    las.x = xs
    las.y = ys
    las.z = zs

    las.write(output_laz_path)
