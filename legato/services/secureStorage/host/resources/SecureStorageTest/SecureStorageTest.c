#include "legato.h"
#include "interfaces.h"


void readTest
(
    long cycles
)
{
    LE_INFO("----- Read Test Begin -----");

    char outBuffer[1024];
    size_t outBufferSize = sizeof(outBuffer);
    le_result_t result;

    // write item once so it can be read.
    result = le_secStore_Write("file1", (uint8_t*)"string123", 10);
    LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));


    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Read("file1", (uint8_t*)outBuffer, &outBufferSize);

        LE_FATAL_IF(result != LE_OK, "read failed: [%s]", LE_RESULT_TXT(result));

        LE_FATAL_IF(strcmp(outBuffer, "string123") != 0,
                    "Read item should be '%s', but is '%s'.", "string123", outBuffer);

        counter++;
    }

    // clean up
    result = le_secStore_Delete("file1");
    LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));
}


void writeTest
(
    long cycles
)
{
    LE_INFO("----- Write Test Begin -----");

    le_result_t result;

    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Write("file1", (uint8_t*)"string123", 10);
        LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));

        counter++;
    }

    // clean up
    result = le_secStore_Delete("file1");
    LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));
}


void deleteTest
(
    long cycles
)
{
    LE_INFO("----- Delete Test Begin -----");

    le_result_t result;

    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Delete("file1");
        LE_FATAL_IF(result != LE_NOT_FOUND, "delete failed: [%s]", LE_RESULT_TXT(result));

        counter++;
    }
}


// write test - with a large file
void writeLargeFileTest
(
    long cycles
)
{
    LE_INFO("----- Write Large File Test Begin -----");

    le_result_t result;

    // This file size is limited by the the app limit in adef and the payload size defined in
    // le_secStore.api. They are both 8192 bytes.
    const int fileSize = 8192;

    #define patternSize 10
    char pattern[patternSize] = "1234567890";
    int tailStrSize = fileSize % patternSize;

    void* largeStr = malloc(fileSize);
    void* largeStrCurPtr = largeStr;

    int copySize;
    while ( (largeStrCurPtr - largeStr) < fileSize)
    {
        copySize = ((fileSize - (largeStrCurPtr - largeStr)) <= tailStrSize) ? tailStrSize : sizeof(pattern);

        memcpy(largeStrCurPtr, pattern, copySize);
        largeStrCurPtr += copySize;
    }

    LE_INFO("large str of size [%d] is [%s]", fileSize, (char*)largeStr);



    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Write("file1", (uint8_t*)largeStr, fileSize);
        LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));

        counter++;
    }

    // clean up
    result = le_secStore_Delete("file1");
    LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));
}


void longItemNameTest
(
    void
)
{
    LE_INFO("----- Long Item Name Test Begin -----");

    /* implementation dependent. see le_secStore.api MAX_NAME_SIZE */
    #define LONGNAMELIMIT 255
    le_result_t result;
    char outBuffer[1024];
    size_t outBufferSize = sizeof(outBuffer);
    char longName[LONGNAMELIMIT + 1];

    // fill the longName array with characters
    int i;
    for ( i = 0; i < LONGNAMELIMIT; i++)
    {
        longName[i] = 'c';
    }

    // terminate the name with null char.
    longName[i] = '\0';
    LE_INFO("sanity check - longName length is: %u", strlen(longName));

    LE_INFO("----- Round [1] -----"); // need this to satisfy the test script
    LE_INFO("test with long name: %s", longName);

    result = le_secStore_Write(longName, (uint8_t*)"string123", 10);
    LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));

    result = le_secStore_Read(longName, (uint8_t*)outBuffer, &outBufferSize);
    LE_FATAL_IF(result != LE_OK, "read failed: [%s]", LE_RESULT_TXT(result));
    LE_FATAL_IF(strcmp(outBuffer, "string123") != 0,
                "Read item should be '%s', but is '%s'.", "string123", outBuffer);

    result = le_secStore_Delete(longName);
    LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));

    LE_INFO("If it gets this far, that means write, read, and delete all succeeded.");
}


void writeReadTest
(
    long cycles
)
{
    LE_INFO("----- Write Read Test Begin -----");

    char outBuffer[1024];
    size_t outBufferSize = sizeof(outBuffer);
    le_result_t result;


    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Write("file1", (uint8_t*)"string123", 10);

        LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));



        result = le_secStore_Read("file1", (uint8_t*)outBuffer, &outBufferSize);

        LE_FATAL_IF(result != LE_OK, "read failed: [%s]", LE_RESULT_TXT(result));

        LE_FATAL_IF(strcmp(outBuffer, "string123") != 0,
                    "Read item should be '%s', but is '%s'.", "string123", outBuffer);

        counter++;
    }

    // clean up
    result = le_secStore_Delete("file1");
    LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));
}


void writeDeleteReadTest
(
    long cycles
)
{
    LE_INFO("----- Write Delete Read Test Begin -----");

    char outBuffer[1024];
    size_t outBufferSize = sizeof(outBuffer);
    le_result_t result;

    long max = cycles;
    long counter = 1;
    while (counter <= max)
    {
        LE_INFO("----- Round [%ld] -----", counter);

        result = le_secStore_Write("file1", (uint8_t*)"string123", 10);
        LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));


        result = le_secStore_Delete("file1");
        LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));

        result = le_secStore_Read("file1", (uint8_t*)outBuffer, &outBufferSize);
        LE_FATAL_IF(result != LE_NOT_FOUND, "After deletion, file can still be read: [%s]", LE_RESULT_TXT(result));

        counter++;
    }
}


COMPONENT_INIT
{
    LE_INFO("=================================  Secure Storage Test Begin  ========================================================");

    if (le_arg_NumArgs() != 2)
    {
        LE_ERROR("Usage: SecureStorageTest [test type] [cycles]");
        exit(EXIT_FAILURE);
    }

    char argTestType[50];
    strcpy(argTestType, le_arg_GetArg(0));
    long argCycles = strtol(le_arg_GetArg(1), NULL, 0);


    if (strcmp(argTestType, "read") == 0)
    {
        LE_INFO("read test selected");
        readTest(argCycles);
    }
    else if (strcmp(argTestType, "write") == 0)
    {
        LE_INFO("write test selected");
        writeTest(argCycles);
    }
    else if (strcmp(argTestType, "delete") == 0)
    {
        LE_INFO("delete test selected");
        deleteTest(argCycles);
    }
    else if (strcmp(argTestType, "writelarge") == 0)
    {
        LE_INFO("write large file test selected");
        writeLargeFileTest(argCycles);
    }
    else if (strcmp(argTestType, "longitemname") == 0)
    {
        LE_INFO("long item name test selected");
        longItemNameTest();
    }
    else if (strcmp(argTestType, "writeread") == 0)
    {
        LE_INFO("write read test selected");
        writeReadTest(argCycles);
    }
    else if (strcmp(argTestType, "writedeleteread") == 0)
    {
        LE_INFO("write delete read test selected");
        writeDeleteReadTest(argCycles);
    }
    else
    {
        LE_INFO("invalid option selected");
        exit(EXIT_FAILURE);
    }

    LE_INFO("=================================  Secure Storage Test Passed  ========================================================");
    exit(EXIT_SUCCESS);
}
