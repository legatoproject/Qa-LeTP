/**
 * @file atomTryOpen.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void TryOpenReturnsWouldBlock(const char *filePath)
{
    int fd = le_atomFile_Open(filePath, LE_FLOCK_READ);

    le_result_t result = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);

    if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[PASSED] le_atomFile_TryOpen returns LE_WOULD_BLOCK if there is already an incompatible lock on the file.");
        le_atomFile_Close(fd);
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_NOT_FOUND if there is already an incompatible lock on the file.");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_FAULT if there is already an incompatible lock on the file.");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns '%d' if there is already an incompatible lock on the file.", result);
    }
}

void TryOpenReturnsNotFound(const char *filePath)
{
    le_result_t result = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] le_atomFile_TryOpen returns LE_NOT_FOUND if the file does not exist.");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_WOULD_BLOCK if the file does not exist.");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_FAULT if the file does not exist.");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns '%d' if the file does not exist.", result);
    }
}

void TryOpenReturnsFd(const char *filePath)
{
    int fd = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);

    if (fcntl(fd, F_GETFD) != -1)
    {
        LE_INFO("[PASSED] le_atomFile_TryOpen returns a file descriptor if successful");
        le_atomFile_Close(fd);
    }
    else if (fd == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_NOT_FOUND when tries to open an existed file");
    }
    else if (fd == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_WOULD_BLOCK when tries to open an existed file");
    }
    else if (fd == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_FAULT when tries to open an existed file");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns '%d' when tries to open an existed file", fd);
    }
}

void TryOpenReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_TryOpen(filePath, LE_FLOCK_WRITE);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_TryOpen returns LE_FAULT when there was an error (accesses to non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_WOULD_BLOCK when there was an error (accesses to non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns LE_NOT_FOUND when there was an error (accesses to non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryOpen returns '%d' when there was an error (accesses to non-existed dir)", result);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void TryOpenAcquiresFlock(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_TryOpen(filePath, LE_FLOCK_READ);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        le_atomFile_Close(childFd);
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
        perror("*** ERROR *** fork()");
    }
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomTryOpen atomTryOpenProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_TryOpen API======================");
    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "wouldBlock") == 0)
    {
        TryOpenReturnsWouldBlock(testFilePath);
    }
    else if (strcmp(testDescription, "notFound") == 0)
    {
        TryOpenReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fd") == 0)
    {
        TryOpenReturnsFd(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        TryOpenReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "acquireFlock") == 0)
    {
        TryOpenAcquiresFlock(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_TryOpen API===========================");

    exit(EXIT_SUCCESS);
}