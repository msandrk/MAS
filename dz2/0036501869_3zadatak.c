/*
    This program calculates realtive frequency of each of 16 groups
    in a ".pmg" file. Groups are designated by most significant 4 bits
    of each pixel color.
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NUM_OF_GROUPS   16

/*
    Reads pixels from binary .pgm P5 file and calculates relative
    frequencies.
*/
void calculateFrequency(char const *filename, float *freqs){
    FILE *file = fopen(filename, "rb");
    int counts[NUM_OF_GROUPS] = { 0 };
    int width = 0, height = 0;
    int numOfPixels;
    uint16_t currPixel = 0, maxVal = 0;
    uint8_t readBytes, shiftBy;
    char buff[6];       // max number of chars that can be read in a column, if there
                        // are no comments in the .pgm file, is 6 (if maxVal is "65535" + "\n")

    if(file == NULL) {
        printf("\nNo such file or directory! Exiting...\n\n");
        exit(1);
    }

    fgets(buff, 3, file); // read "P5" annotation
    fgets(buff, 6, file); // read image width
    width = atoi(buff);
    fgets(buff, 6, file); // read image height;
    height = atoi(buff);

    fgets(buff, 6, file); // read maxval;
    maxVal = atoi(buff);

    readBytes = maxVal > 255 ? 2 : 1; // each pixel is represented by how many bytes
    shiftBy = readBytes == 1 ? 4 : 12;
    
    // count how many times each group appears
    while((fread(&currPixel, readBytes, 1, file)) == readBytes) {
        counts[currPixel >> shiftBy]++;
        currPixel = 0;
    }

    // calculate relative frequency of each group
    numOfPixels = height * width;
    for(int i = 0; i < NUM_OF_GROUPS; i++){
        freqs[i] = (float) counts[i] / numOfPixels;
    }

    fclose(file);
}

/*
    Prints relative frequencies of groups
*/
void printResults(float *freqs){
    int i;
    for(i = 0; i < NUM_OF_GROUPS; i++){
        printf("%d %f\n", i, freqs[i]);
    }
}

int main(int argc, char const *argv[])
{
    if(argc != 2){
        printf("\nProgram requires 1 argument which represents the path to a '.pgm' file!\n\n");
        exit(1);
    }

    float freqs[NUM_OF_GROUPS];
    
    calculateFrequency(argv[1], freqs);
    printResults(freqs);
    
    return 0;
}
