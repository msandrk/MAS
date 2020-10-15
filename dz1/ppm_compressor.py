import sys
import numpy as np

def parse_ppm_file(path):
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
        width, height = [int(x) for x in line.split()]
        
        line = file.readline()
        while line.startswith("#".encode("ansi")):
            line = file.readline()
        bytes_per_comp = 1 if int(line) < 256 else 2
        data_type = np.uint8 if bytes_per_comp == 1 else np.uint16

        R = []
        G = []
        B = []
            
        for row in range(height):
            line = file.readline(width * bytes_per_comp * 3)
            if line.startswith("#".encode("ansi")):
                continue
            
            r = []
            g = []
            b = []
            i = 0
            while i < width * bytes_per_comp:
                r.append(int.from_bytes(line[i : i + bytes_per_comp], byteorder=sys.byteorder, signed=False))
                
                i += bytes_per_comp
                
                g.append(int.from_bytes(line[i : i + bytes_per_comp], byteorder=sys.byteorder, signed=False))
                i += bytes_per_comp
                
                b.append(int.from_bytes(line[i : i + bytes_per_comp], byteorder=sys.byteorder, signed=False))
                i += bytes_per_comp
            
            R.append(np.array(r, dtype=data_type))
            G.append(np.array(g, dtype=data_type))
            B.append(np.array(b, dtype=data_type))
    
    return (R, G, B)

if __name__ == "__main__":
    fi_path = sys.argv[1]
    parse_ppm_file(fi_path)
