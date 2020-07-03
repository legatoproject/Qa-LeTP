/**
 * @file atomCancel.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

void CancelOpenWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
    write(fd, "String Foo", sizeof("String Foo"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelCreateWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    write(fd, "String Foo", sizeof("String Foo"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelTryOpenWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);
    write(fd, "String Foo", sizeof("String Foo"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelTryCreateWrtFlockReturnsOK(const char *filePath)
{
    int fd = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    write(fd, "String Foo", sizeof("String Foo"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelOpenReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_Open(filePath, LE_FLOCK_READ);
    read(fd, readBuffer, sizeof("Hello World"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelCreateReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_Create(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    read(fd, readBuffer, sizeof("Hello World"));
    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelTryOpenReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_TryOpen(filePath, LE_FLOCK_READ);
    read(fd, readBuffer, sizeof("Hello World"));

    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

void CancelTryCreateReadFlockReturnsOK(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_TryCreate(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
    read(fd, readBuffer, sizeof("Hello World"));

    le_atomFile_Cancel(fd);

    LE_INFO("le_atomFile_Cancel is called");
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomCancel atomCancelProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_Cancel API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "openWrtFlockOK") == 0)
    {
        CancelOpenWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenWrtFlockOK") == 0)
    {
        CancelTryOpenWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createWrtFlockOK") == 0)
    {
        CancelCreateWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateWrtFlockOK") == 0)
    {
        CancelTryCreateWrtFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "openReadFlockOK") == 0)
    {
        CancelOpenReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryOpenReadFlockOK") == 0)
    {
        CancelTryOpenReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "createReadFlockOK") == 0)
    {
        CancelCreateReadFlockReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "tryCreateReadFlockOK") == 0)
    {
        CancelTryCreateReadFlockReturnsOK(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_Cancel API===========================");

    exit(EXIT_SUCCESS);
}