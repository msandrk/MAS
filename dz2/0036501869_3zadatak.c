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

    if(file == NULL) {
        printf("\nNeuspjesno citanje datoteke...");
        exit(1);
    }

    int counts[NUM_OF_GROUPS] = { 0 };
    int width = 0, height = 0;
    int numOfPixels;
    uint16_t currPixel = 0, maxVal = 0;
    uint8_t readBytes = 0, shiftBy;
    char tmp[6];

    fgets(tmp, 6, file); // read "P5" annotation
    fgets(tmp, 6, file); // read image width
    width = atoi(tmp);
    fgets(tmp, 6, file); // read image height;
    height = atoi(tmp);

    fgets(tmp, 6, file); // read maxval;
    maxVal = atoi(tmp);

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
        printf("\nPotrebno je predati datoteku u pgm formatu kao argument...\n");
        exit(1);
    }

    float freqs[NUM_OF_GROUPS];
    
    calculateFrequency(argv[1], freqs);
    printResults(freqs);
    
    return 0;
}
