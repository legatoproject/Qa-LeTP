#include "legato.h"
#include "interfaces.h"

void CancelStreamOpenStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
    fprintf(fp, "String Foo");
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamCreateStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fprintf(fp, "String Foo");
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamTryOpenStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, NULL);
    fprintf(fp, "String Foo");
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamTryCreateStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fprintf(fp, "String Foo");
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamOpenStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_READ, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamCreateStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);
    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamTryOpenStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_READ, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);

    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

void CancelStreamTryCreateStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);

    le_atomFile_CancelStream(fp);

    LE_INFO("le_atomFile_CancelStream is called");
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomCancel atomCancelProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_CancelStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "openStreamWrtFlockOK") == 0)
    {
        CancelStreamOpenStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenStreamWrtFlockOK") == 0)
    {
        CancelStreamTryOpenStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createStreamWrtFlockOK") == 0)
    {
        CancelStreamCreateStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateStreamWrtFlockOK") == 0)
    {
        CancelStreamTryCreateStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "openStreamReadFlockOK") == 0)
    {
        CancelStreamOpenStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenStreamReadFlockOK") == 0)
    {
        CancelStreamTryOpenStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createStreamReadFlockOK") == 0)
    {
        CancelStreamCreateStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateStreamReadFlockOK") == 0)
    {
        CancelStreamTryCreateStreamReadFlockReturnsOK(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_CancelStream API===========================");

    exit(EXIT_SUCCESS);
}