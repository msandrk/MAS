import sys
import numpy as np


quant_table_k1 = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 86, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
])

quant_table_k2 = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99]
])

class PpmImage:
    def __init__(self, path : str):
        
    # def parse_ppm_file(self, path):
        with open(path, "rb") as file:
            
            ppm_format = file.readline()
            while ppm_format.startswith("#".encode("ansi")):
                ppm_format = file.readline()
            
            if ppm_format.startswith("P6".encode("ansi")) is not True:
                print("Only raw, P6, ppm format is suported")
                sys.exit(-1)
            
            line = file.readline()
            while line.startswith("#".encode("ansi")):
                line = file.readline()
            self.width, self.height = [int(x) for x in line.split()]
            
            line = file.readline()
            while line.startswith("#".encode("ansi")):
                line = file.readline()
            self.bytes_per_comp = 1 if int(line) < 256 else 2
            data_type = np.uint8 if self.bytes_per_comp == 1 else np.uint16

            self.R = []
            self.G = []
            self.B = []
                
            for row in range(self.height):
                # line = file.readline(self.width * self.bytes_per_comp * 3)
                line = file.readline()
                if line.startswith("#".encode("ansi")):
                    continue
                
                r = []
                g = []
                b = []
                i = 0
                while i < self.width * self.bytes_per_comp * 3:
                    r.append(int.from_bytes(line[i : i + self.bytes_per_comp], byteorder=sys.byteorder, signed=False))
                    
                    i += self.bytes_per_comp
                    
                    g.append(int.from_bytes(line[i : i + self.bytes_per_comp], byteorder=sys.byteorder, signed=False))
                    i += self.bytes_per_comp
                    
                    b.append(int.from_bytes(line[i : i + self.bytes_per_comp], byteorder=sys.byteorder, signed=False))
                    i += self.bytes_per_comp
                
                self.R.append(np.array(r, dtype=data_type))
                self.G.append(np.array(g, dtype=data_type))
                self.B.append(np.array(b, dtype=data_type))
        
        self.R = np.array(self.R)
        self.G = np.array(self.G)
        self.B = np.array(self.B)

def get_rgb_comp_for_block(ppm_image, block_number, block_dimension=8):
    if block_number < 0:
        block_number = 0
    elif block_number >= (ppm_image.width // block_dimension)  * (ppm_image.height // block_dimension):
        block_number = (ppm_image.width // block_number) * (ppm_image.height // block_dimension) - 1
    r_block = []
    g_block = []
    b_block = []
    
    # index of first row of the block
    first_row = block_number // (ppm_image.width // block_dimension)
    
    for row in range(first_row, first_row + block_dimension):
        curr_r_row = []
        curr_g_row = []
        curr_b_row = []
        for i in range(block_number * block_dimension, block_dimension * (block_number + 1)):
            curr_r_row.append(ppm_image.R[row][i])
            curr_g_row.append(ppm_image.G[row][i])
            curr_b_row.append(ppm_image.B[row][i])
        r_block.append(curr_r_row)
        g_block.append(curr_g_row)
        b_block.append(curr_b_row)

    return np.array(r_block), np.array(g_block), np.array(b_block)


def transform_to_ycbcr(R : np.array, G : np.array, B : np.array):
    y = 0.299 * R + 0.587 * G + 0.114 * B
    cb = -0.1687 * R - 0.3313 * G + 0.5 * B + 128
    cr = 0.5 * R - 0.4187 * G - 0.0813 * B + 128
    return (y, cb, cr)

def dct__2d_transformatioin(y: np.array, cb: np.array, cr: np.array, block_dimension=8):
    y_dct = []
    cb_dct= []
    cr_dct = []
    for u in range(block_dimension):
        curr_row_y = []
        curr_row_cb = []
        curr_row_cr = []
        pi_u = np.pi * u / (2 * block_dimension)
        for v in range(block_dimension):
            coeff = 0.5 if u == 0 or v == 0 else 1
            coeff /= 4
            pi_v = np.pi * v / (2 * block_dimension)
            curr_values = np.zeros((3, 1))
            for i in range (y.shape[0]):
                for j in range(y.shape[1]):
                    curr_values[0] += y[i][j] * coeff * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
                    curr_values[1] += cb[i][j] * coeff * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
                    curr_values[2] += cr[i][j] * coeff * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
            curr_row_y.append(curr_values[0])
            curr_row_cb.append(curr_values[1])
            curr_row_cr.append(curr_values[2])
    y_dct.append(curr_row_y)
    cr_dct.append(curr_row_cb)
    cb_dct.append(curr_row_cr)
    return y_dct, cb_dct, cr_dct

def quantize(matrix, quant_table, inverse=False):
    return matrix

def write_matrix_to_file(m, out_file):
    for row in m:
            for e in row:
                out_file.write(e + "\t")


def compress_ppm(input_path, block_number, out_path):
    ppm_image = PpmImage(input_path)
    r, g, b = get_rgb_comp_for_block(ppm_image, block_number)
    y, cb, cr = transform_to_ycbcr(r, g, b)
    
    # translate components to [-128, 127] interval
    y -= 128
    cb -= 128
    cr -= 128

    y, cb, cr = dct__2d_transformatioin(y, cb, cr)

    y = quantize(y, quant_table_k1)
    cb = quantize(cb, quant_table_k2)
    cr = quantize(cr, quant_table_k2)
    
    with open(out_path, "w") as out_file:
        write_matrix_to_file(y, out_file)
        out_file.write("\n")
        write_matrix_to_file(cb, out_file)
        out_file.write("\n")
        write_matrix_to_file(cr, out_file)


def main():
    fi_path = sys.argv[1]
    block_number = int(sys.argv[2])
    out_path = sys.argv[3]
    compress_ppm(fi_path, block_number, out_path)


if __name__ == "__main__":
    main()
