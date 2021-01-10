#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#define BLOCK_SIZE 16    // dimension of a block

// calculates maximum index of a block for width of 'w' and height of 'h'
#define MAX_BLOCK_NUMBER(w, h)  (((w) / BLOCK_SIZE * (h) / BLOCK_SIZE) - 1)

typedef struct _real_search_coord_ {
    int x1;
    int y1;
    int x2;
    int y2;
} real_search_coord;

typedef struct _vector_ {
    int x;
    int y;
} vector;

/*
    Loads block with index 'blockNumber' into 'referentBlock' matrix.
    Returns 'blockNumber' that was acctualy loaded (e.g. if 'blockNumber'
    is less than 0, block with index 0 will be loaded to 'referentBlock')
*/
int getReferentBlock(char const *fileName, int blockNumber, 
                    uint16_t referentBlock[BLOCK_SIZE][BLOCK_SIZE]){
    
    int picWidth, picHeight;
    char buff[6];
    uint8_t elementSize = 0;
    uint16_t maxVal;
    FILE *picture = fopen(fileName, "rb");

    if(picture == NULL){
        printf("\n\nUnable to open '%s'! Exiting...\n\n", fileName);
        exit(1);
    }

    fgets(buff, 6, picture);    // get "P5" annotation
    fgets(buff, 6, picture);    // get image width
    picWidth = atoi(buff);
    
    fgets(buff, 6, picture);    // get image height
    picHeight = atoi(buff);

    
    blockNumber = blockNumber < 0 ? 0 : blockNumber;
    blockNumber = blockNumber > MAX_BLOCK_NUMBER(picWidth, picHeight) ?
                    MAX_BLOCK_NUMBER(picWidth, picHeight) : blockNumber;


    fgets(buff, 6, picture);
    maxVal = atoi(buff);

    elementSize = maxVal <= 255 ? 1 : 2;

    size_t firstRow = blockNumber / (picWidth / BLOCK_SIZE) * BLOCK_SIZE;
    size_t firstColumn = blockNumber % (picWidth / BLOCK_SIZE) * BLOCK_SIZE;
    
    fseek(picture, firstRow * picWidth * elementSize, SEEK_CUR);
    fseek(picture, firstColumn * elementSize, SEEK_CUR);


    if(elementSize == 1) {
        for(int i = 0; i < BLOCK_SIZE; i++){
            for(int j = 0; j < BLOCK_SIZE; j++){
                fread(&referentBlock[i][j], 1, 1, picture);
            }
            fseek(picture, (picWidth - BLOCK_SIZE) * elementSize, SEEK_CUR);
        }
    } else {
        for(int i = 0; i < BLOCK_SIZE; i++){
            fread(&referentBlock[i], elementSize, BLOCK_SIZE, picture);
            fseek(picture, (picWidth - BLOCK_SIZE) * elementSize, SEEK_CUR);
        }
    }
    fclose(picture);
    return blockNumber;
}

/*
    Loads search area for full search into 'searchWindow'. Area is spanning
    from 'blockNumber' +/- BLOCK_SIZE elements which totals in 3 * BLOCK_SIZE rows
    and columns. Pointers 'rowStart', 'rowEnd', 'colStart' and 'colEnd' are used 
    to indicate span of useful data. For instance, if the 'blockNumber' is 0, areas
    -BLOCK_SIZE elements in both x and y directions are not present and in that case
    rowStart and column start are properly adjusted.
*/
real_search_coord getSearchArea(char const *fileName, int blockNumber, 
                    uint16_t searchWindow[3*BLOCK_SIZE][3*BLOCK_SIZE]){
    
    int picWidth, picHeight;
    char buff[6];
    uint8_t elementSize = 0;
    uint16_t maxVal;
    int firstRow, firstColumn, lastRow, lastColumn;
    real_search_coord coords = { 0, 0, 0, 0};
    FILE *picture = fopen(fileName, "rb");

    if(picture == NULL){
        printf("\n\nUnable to open '%s'! Exiting...\n\n", fileName);
        exit(1);
    }

    fgets(buff, 6, picture);    // get "P5" annotation
    fgets(buff, 6, picture);    // get image width
    picWidth = atoi(buff);
    
    fgets(buff, 6, picture);    // get image height
    picHeight = atoi(buff);

    fgets(buff, 6, picture);
    maxVal = atoi(buff);

    elementSize = maxVal <= 255 ? 1 : 2;

    // Start with one block above the referent block.
    firstRow = blockNumber / (picWidth / BLOCK_SIZE) * BLOCK_SIZE - BLOCK_SIZE;
    coords.y1 = firstRow < 0 ? BLOCK_SIZE : 0;  // set start of real data in searchArea
    
    // Start with one block to the left of the referent block.
    firstColumn = blockNumber % (picWidth / BLOCK_SIZE) * BLOCK_SIZE - BLOCK_SIZE;
    coords.x1 = firstColumn < 0 ? BLOCK_SIZE : 0; // set start of real data in searchArea
    
    // End with block below the referent block
    lastRow = firstRow + 3 * BLOCK_SIZE;
    coords.y2 = lastRow > picHeight ? 2 * BLOCK_SIZE : 3 * BLOCK_SIZE; // set end of real data

    // End with one block to the right of the referent block.
    lastColumn = firstColumn + 3 * BLOCK_SIZE;
    coords.x2 = lastColumn > picWidth ? 2 * BLOCK_SIZE : 3 * BLOCK_SIZE; // set end of real data
    
    firstRow = firstRow < 0 ? 0 : firstRow;
    firstColumn = firstColumn < 0 ? 0 : firstColumn;

    // position pointer to the begining of the block
    fseek(picture, firstRow * picWidth * elementSize, SEEK_CUR);
    fseek(picture, firstColumn * elementSize, SEEK_CUR);

    if (elementSize == 1) {
        for(int i = coords.y1; i < coords.y2; i++){
            for(int j = coords.x1; j < coords.x2; j++){
                fread(&searchWindow[i][j], elementSize, 1, picture);
            }
            fseek(picture, picWidth - (coords.x2 - coords.x1 + 1), SEEK_CUR);
        }
    } else {
        for(int i = coords.y1; i < coords.y2; i++){
            size_t bytesRead = fread(&searchWindow[i][coords.x1], elementSize,
                                    (coords.x2 - coords.x1) + 1, picture);
            fseek(picture, (picWidth * elementSize - bytesRead), SEEK_CUR);
        }
    }
    
    fclose(picture);
    return coords;
}

/*
    Calculates mean absolute difference (MAD) between two blocks.
*/

double mean_absolute_difference(uint16_t block1[BLOCK_SIZE][BLOCK_SIZE], 
                                uint16_t block2[BLOCK_SIZE][BLOCK_SIZE]){
    double result = 0;
    for(int i = 0; i < BLOCK_SIZE; i++){
        for(int j = 0; j < BLOCK_SIZE; j++){
            result += abs(block1[i][j] - block2[i][j]);
        }
    }
    return result / (BLOCK_SIZE * BLOCK_SIZE);
}

vector full_search(uint16_t referentBlock[BLOCK_SIZE][BLOCK_SIZE],
                uint16_t searchArea[3 * BLOCK_SIZE][3 * BLOCK_SIZE],
                real_search_coord const *coords){

    double currMAD, minMAD = -1.; // MAD must be >= 0
    vector moveVector = { 0, 0};
    
    for(int i = coords->y1; i < coords->y2 - BLOCK_SIZE; i++){
        for(int j = coords->x1; j < coords->x2 - BLOCK_SIZE; j++){
            // get block that is currently being compared
            uint16_t activeBlock[BLOCK_SIZE][BLOCK_SIZE];
            for(int k = 0; k < BLOCK_SIZE; k++){
                for(int l = 0; l < BLOCK_SIZE; l++){
                    activeBlock[k][l] = searchArea[i + k][j + l];
                }
            }
            currMAD = mean_absolute_difference(referentBlock, activeBlock);
            if (minMAD < 0 || currMAD < minMAD) {
                minMAD = currMAD;
                moveVector.x = j - BLOCK_SIZE;
                moveVector.y = i - BLOCK_SIZE;
            }
        }
    }

    return moveVector;
}

int main(int argc, char const *argv[])
{
    if (argc != 2) {
        printf("\nProgramme requires a block number as an argument!\n\n");
        exit(1);
    }

    int blockNumber = atoi(argv[1]);
    real_search_coord coords;
    vector moveVector;
    uint16_t referentBlock[BLOCK_SIZE][BLOCK_SIZE] = { 0 };
    uint16_t searchWindow[3 * BLOCK_SIZE][3 * BLOCK_SIZE] = { 0 };
    
    blockNumber = getReferentBlock("./lenna1.pgm", blockNumber, referentBlock);

    coords = getSearchArea("./lenna.pgm", blockNumber, searchWindow);
    
    moveVector = full_search(referentBlock, searchWindow, &coords);
    
    printf("%d,%d\n", moveVector.x, moveVector.y);

    return 0;
}
