/**
 * @file atomCloseStream.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

void CloseStreamOpenStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
    fprintf(fp, "String Foo");
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamCreateStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fprintf(fp, "String Foo");
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamTryOpenStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, NULL);
    fprintf(fp, "String Foo");
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamTryCreateStreamWrtFlockReturnsOK(const char *filePath)
{
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fprintf(fp, "String Foo");
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamOpenStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_READ, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamCreateStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);
    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamTryOpenStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_READ, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);

    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

void CloseStreamTryCreateStreamReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
    fread(readBuffer, 1, sizeof("Hello World"), fp);

    le_result_t result = le_atomFile_CloseStream(fp);

    LE_INFO("le_atomFile_CloseStream is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_CloseStream returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_CloseStream returns %d", result);
    }
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomClose atomCloseProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_CloseStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "openStreamWrtFlockOK") == 0)
    {
        CloseStreamOpenStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenStreamWrtFlockOK") == 0)
    {
        CloseStreamTryOpenStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createStreamWrtFlockOK") == 0)
    {
        CloseStreamCreateStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateStreamWrtFlockOK") == 0)
    {
        CloseStreamTryCreateStreamWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "openStreamReadFlockOK") == 0)
    {
        CloseStreamOpenStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenStreamReadFlockOK") == 0)
    {
        CloseStreamTryOpenStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createStreamReadFlockOK") == 0)
    {
        CloseStreamCreateStreamReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateStreamReadFlockOK") == 0)
    {
        CloseStreamTryCreateStreamReadFlockReturnsOK(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_CloseStream API===========================");

    exit(EXIT_SUCCESS);
}