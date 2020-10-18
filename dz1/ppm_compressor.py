import sys
import numpy as np


quant_table_k1 = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
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
            
            file_content = file.read()
            read_rows = [
                file_content[i : i + (self.width * self.bytes_per_comp * 3)]
                for i in range(0, len(file_content), self.width * self.bytes_per_comp * 3)
            ]
            read_pixels = [
                [
                    [int(e) for e in row[i : i + self.bytes_per_comp * 3]]
                    for i in range(0, len(row), self.bytes_per_comp * 3)
                ]
                for row in read_rows
            ]

        for row in read_pixels:
            r = []
            g = []
            b = []
            for comp in row:
                r.append(comp[0])
                g.append(comp[1])
                b.append(comp[2])
            self.R.append(r)
            self.G.append(g)
            self.B.append(b)
                    
        self.R = np.array(self.R, dtype=data_type)
        self.G = np.array(self.G, dtype=data_type)
        self.B = np.array(self.B, dtype=data_type)

    def get_rgb_comp_for_block(self, block_number, block_dimension=8):
        if block_number < 0:
            block_number = 0
        elif block_number >= (self.width // block_dimension)  * (self.height // block_dimension):
            block_number = (self.width // block_number) * (self.height // block_dimension) - 1
        r_block = []
        g_block = []
        b_block = []
        
        blocks_per_row = self.width // block_dimension
        # index of first row of the block
        first_row = int(np.floor(block_number // blocks_per_row) * block_dimension)
        
        # index of first column of the block
        first_column = block_number / blocks_per_row - block_number // blocks_per_row
        first_column *= blocks_per_row * block_dimension
        first_column = int(first_column)
        
        for row in range(first_row, first_row + block_dimension):
            curr_r_row = []
            curr_g_row = []
            curr_b_row = []
            for i in range(first_column, first_column + block_dimension):
                curr_r_row.append(self.R[row][i])
                curr_g_row.append(self.G[row][i])
                curr_b_row.append(self.B[row][i])
            r_block.append(curr_r_row)
            g_block.append(curr_g_row)
            b_block.append(curr_b_row)

        return np.array(r_block), np.array(g_block), np.array(b_block)
    

def transform_to_ycbcr(R : np.array, G : np.array, B : np.array):
    
    y = [
        [0.299 * R[i][j] + 0.587 * G[i][j] + 0.114 * B[i][j] for j in range(R.shape[1])] 
            for i in range(R.shape[0])
        ]
    cb = [
        [-0.1687 * R[i][j] - 0.3313 * G[i][j] + 0.5 * B[i][j] + 128 for j in range(R.shape[1])]
            for i in range(R.shape[1])
        ]
    cr = [
        [0.5 * R[i][j] - 0.4187 * G[i][j] - 0.0813 * B[i][j]  + 128 for j in range(R.shape[0])]
            for i in range(R.shape[0])
        ]
    
    return np.array(y), np.array(cb), np.array(cr)


def dct_2d_transformatioin(y: np.array, cb: np.array, cr: np.array, block_dimension=8):
    y_dct = []
    cb_dct = []
    cr_dct = []
    for u in range(block_dimension):
        # u_coeff = pow(0.5, 0.5) if u == 0 else 1
        pi_u = (u * np.pi) / 16
        curr_y = np.zeros((y.shape[1]))
        curr_cb = np.zeros((cb.shape[1]))
        curr_cr = np.zeros((cr.shape[1]))
        for v in range(block_dimension):
            coeff = 0.5 if (u == 0 or v == 0) else 1
            # coeff = pow(0.5, 0.5) * u_coeff if v == 0 else u_coeff
            pi_v = (v * np.pi) / 16
            coeff *= (2 / block_dimension)
            for i in range(block_dimension):
                for j in range(block_dimension):
                    curr_y[v] += y[i][j] * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
                    curr_cb[v] += cb[i][j] * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
                    curr_cr[v] += cr[i][j] * np.cos((2 * i + 1) * pi_u) * np.cos((2 * j + 1) * pi_v)
        y_dct.append(coeff * curr_y)
        cb_dct.append(coeff * curr_cb)
        cr_dct.append(coeff * curr_cr)

    return np.array(y_dct), np.array(cb_dct), np.array(cr_dct)

def quantize(matrix, quant_table, inverse=False):
    if inverse is True:
        return np.multiply(matrix, quant_table).astype('int64')
    
    return np.divide(matrix, quant_table).astype('int64')


def write_matrix_to_file(m, out_file):
    for row in m:
            for e in row:
                out_file.write(str(e) + "\t")
            out_file.write("\n")

def compress_ppm(ppm_image, block_number, out_path):

    r, g, b = ppm_image.get_rgb_comp_for_block(block_number)
    
    y, cb, cr = transform_to_ycbcr(r, g, b)
    
    # translate components to [-128, 127] interval
    y -= 128
    cb -= 128
    cr -= 128

    y, cb, cr = dct_2d_transformatioin(y, cb, cr)

    y = quantize(y, quant_table_k1)
    cb = quantize(cb, quant_table_k2)
    cr = quantize(cr, quant_table_k2)

    # write the result on screen
    write_matrix_to_file(y, sys.stdout)
    print("\n")
    write_matrix_to_file(cb, sys.stdout)
    print("\n")
    write_matrix_to_file(cr, sys.stdout)
    print("\n")

    # write the result into the file with given path
    with open(out_path, "w") as out_file:
        write_matrix_to_file(y, out_file)
        out_file.write("\n")
        write_matrix_to_file(cb, out_file)
        out_file.write("\n")
        write_matrix_to_file(cr, out_file)


def main():
    fi_path = sys.argv[1]   # path to the input image
    block_number = int(sys.argv[2]) # index of a desired block
    out_path = sys.argv[3]  # path to the output file
    ppm_image = PpmImage(fi_path)
    compress_ppm(ppm_image, block_number, out_path)


if __name__ == "__main__":
    main()
