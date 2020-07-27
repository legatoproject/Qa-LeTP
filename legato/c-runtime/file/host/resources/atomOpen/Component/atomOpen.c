/**
 * @file atomOpen.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void OpenReturnsNotFound(const char *filePath)
{
    le_result_t result = le_atomFile_Open(filePath, LE_FLOCK_READ);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] le_atomFile_Open returns LE_NOT_FOUND when opens a non-existed file");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_Open returns LE_FAULT when tries to open a non-existed file");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Open returns %d when tries to open a non-existed file", result);
    }
}

void OpenReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_Open(filePath, LE_FLOCK_READ);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_Open returns LE_FAULT when there was an error (accesses to non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_Open returns LE_NOT_FOUND when there was an error (accesses to non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Open returns %d when there was an error (accesses to non-existed dir)", result);
    }
}

void OpenReturnsFd(const char *filePath)
{
    int fd = le_atomFile_Open(filePath, LE_FLOCK_READ);

    if (fcntl(fd, F_GETFD) != -1)
    {
        LE_INFO("[PASSED] le_atomFile_Open returns a file descriptor when successfully opens the file");
    }
    else if (fd == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_Open returns LE_FAULT when tries to open an existed file");
    }
    else if (fd == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_Open returns LE_NOT_FOUND when tries to open an existed file");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Open returns %d when tries to open an existed file", fd);
    }
}

void OpenAtomicWrt(const char *filePath)
{
    const char *contentStr = "string foo";
    int fd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);

    while (true)
    {
        write(fd, contentStr, sizeof(contentStr));
        LE_INFO("***writing data into the file***");
        sleep(5);
    }
}

void OpenAtomicRead(const char *filePath)
{
    char readBuffer[50] = {0};
    int fd = le_atomFile_Open(filePath, LE_FLOCK_READ);

    while (true)
    {
        read(fd, readBuffer, 1);
        LE_INFO("***reading data from the file***");
        sleep(5);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void OpenAtomicBlocking(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        le_atomFile_Close(childFd);
        LE_INFO("***first process's file lock is released***");
        exit(EXIT_SUCCESS);
    }
    // parent
    else if (pid > 0)
    {
        signal(SIGCONT, AtomicBlockingSigHandler);

        while (!accessOK)
        {
            // wait for child to tell me to access the file
            sleep(1);
        }

        int parentFd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
        LE_INFO("***second process is holding a file lock***");
        le_atomFile_Close(parentFd);
    }
    else
    {
        perror("kill()");
        exit(EXIT_FAILURE);
    }
}

void OpenAtomicMultiAccess(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        write(childFd, "string foo", sizeof("string foo"));
        le_atomFile_Close(childFd);
        LE_INFO("***first process's file lock is released***");
        exit(EXIT_SUCCESS);
    }
    // parent
    else if (pid > 0)
    {
        signal(SIGCONT, AtomicBlockingSigHandler);

        while (!accessOK)
        {
            // wait for child to tell me to access the file
            sleep(1);
        }

        int parentFd = le_atomFile_Open(filePath, LE_FLOCK_WRITE);
        LE_INFO("***second process is holding a file lock***");

        while (true)
        {
            write(parentFd, "string 123", sizeof("string 123"));
            LE_INFO("***second process writes string 123 to the file***");
            sleep(5);

        }
    }
    else
    {
        perror("kill()");
        exit(EXIT_FAILURE);
    }
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomOpen atomOpenProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_Open API TEST======================");
    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "notFound") == 0)
    {
        OpenReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        OpenReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "fd") == 0)
    {
        OpenReturnsFd(testFilePath);
    }
    else if (strcmp(testDescription, "atomicWrt") == 0)
    {
        OpenAtomicWrt(testFilePath);
    }
    else if (strcmp(testDescription, "atomicRead") == 0)
    {
        OpenAtomicRead(testFilePath);
    }
    else if (strcmp(testDescription, "atomicBlocking") == 0)
    {
        OpenAtomicBlocking(testFilePath);
    }
    else if (strcmp(testDescription, "atomicMultiAccess") == 0)
    {
        OpenAtomicMultiAccess(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_Open API TEST===========================");

    exit(EXIT_SUCCESS);
}