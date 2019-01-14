#include <stdio.h>
#include <string.h>

int BUFFER_SIZE = 100;

char s[] = "";
char buffer[20];
int  filePtr = 0;
int  fileSize = 0;
int  numMatch = 0;

FILE* readFile(char* fileName) {
    FILE* file = fopen(fileName, "rb");
    //fread(buffer, 100, 1, test);
    // printf("%s\n", buffer);
    return file;
}

int writeFile(char* fileName, int fileSize, int numMatches) {
    FILE* file = fopen(fileName, "wb");
    char sizeStr[256];
    char numMatchStr[256];
    sprintf(sizeStr, "Size of file is %i\n", fileSize);
    sprintf(numMatchStr, "Number of matches = %i\n", numMatches);

    fwrite(sizeStr, strlen(sizeStr), 1, file);
    fwrite(numMatchStr, strlen(numMatchStr), 1, file);
}

int incCount(char* input, char* match) {
    if (strncmp(match, input, strlen(match)) == 0) {
        numMatch++;
    }

    return numMatch;
}

// might have to convert bytes to a long
int getFileSize(FILE* file) {
    fseek(file, 0, SEEK_END);
    int bytes = ftell(file);
    rewind(file);
    return bytes;
}

int readIntoBuffer(FILE* file) {
    fread(buffer, BUFFER_SIZE, 1, file);
    filePtr = BUFFER_SIZE;
    return 0;
}

int shiftBuffer(FILE* file) {
    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = buffer[i+1];
    }
    filePtr++;

    // look into fseek
    // need to shift buffer one at a time
    fseek(file, 1, filePtr);
    fread(buffer, 1, 20, file);

    printf("%s\n", buffer);
    return 0;
}

int main(int argc, char **argv) {
    FILE* file = readFile(argv[1]);
    //writeFile("example2Output", 3, 4);
    //printf("%i\n", getCount("testestest this is a test", "test"));
    //printf("%i\n", getCount("this should stack stackstack", "stack"));
    readIntoBuffer(file);
    int fileSize = getFileSize(file);
    //printf("%s\n", buffer);
    for (int i = 0; i < fileSize/20; i++) {
        shiftBuffer(file);
        incCount(buffer, argv[2]);
        //printf("%s", buffer);
        //printf("getcount is %i\n", getCount(buffer, argv[2]));
    }
    //printf("%s\n", buffer);
    writeFile(argv[3], fileSize, numMatch);
    return 0;
}
