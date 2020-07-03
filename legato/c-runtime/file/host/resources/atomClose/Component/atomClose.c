/**
 * @file atomClose.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

void CloseOpenWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
    write(fd, "String Foo", sizeof("String Foo"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseCreateWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    write(fd, "String Foo", sizeof("String Foo"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseTryOpenWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);
    write(fd, "String Foo", sizeof("String Foo"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseTryCreateWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    write(fd, "String Foo", sizeof("String Foo"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseOpenReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_Open(filePath, LE_FLOCK_READ);
    read(fd, readBuffer, sizeof("Hello World"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseCreateReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_Create(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    read(fd, readBuffer, sizeof("Hello World"));
    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseTryOpenReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_TryOpen(filePath, LE_FLOCK_READ);
    read(fd, readBuffer, sizeof("Hello World"));

    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

void CloseTryCreateReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_TryCreate(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    read(fd, readBuffer, sizeof("Hello World"));

    le_result_t result = le_atomFile_Close(fd);

    LE_INFO("le_atomFile_Close is called");

    if (result == LE_OK)
    {
        LE_INFO("le_atomFile_Close returns LE_OK");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("le_atomFile_Close returns LE_FAULT");
    }
    else
    {
        LE_INFO("le_atomFile_Close returns %d", result);
    }
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomClose atomCloseProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_Close API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "openWrtFlockOK") == 0)
    {
        CloseOpenWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenWrtFlockOK") == 0)
    {
        CloseTryOpenWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createWrtFlockOK") == 0)
    {
        CloseCreateWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateWrtFlockOK") == 0)
    {
        CloseTryCreateWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "openReadFlockOK") == 0)
    {
        CloseOpenReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenReadFlockOK") == 0)
    {
        CloseTryOpenReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createReadFlockOK") == 0)
    {
        CloseCreateReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateReadFlockOK") == 0)
    {
        CloseTryCreateReadFlockReturnsOK(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_Close API===========================");

    exit(EXIT_SUCCESS);
}