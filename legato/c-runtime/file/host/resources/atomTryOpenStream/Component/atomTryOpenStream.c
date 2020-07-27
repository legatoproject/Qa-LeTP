/**
 * @file atomTryOpenStream.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void TryOpenStreamReturnsWouldBlock(const char *filePath)
{
    le_result_t result;
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_READ, NULL);
    le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, &result);

    if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_TryOpenStream returns LE_WOULD_BLOCK if there is already an incompatible lock on the file.");
        le_atomFile_CloseStream(fp);
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_NOT_FOUND if there is already an incompatible lock on the file.");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_FAULT if there is already an incompatible lock on the file.");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns '%d' if there is already an incompatible lock on the file.", result);
    }
}

void TryOpenStreamReturnsNotFound(const char *filePath)
{
    le_result_t result;
    le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, &result);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_TryOpenStream returns LE_NOT_FOUND if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_WOULD_BLOCK if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns '%d' if there was an error (accesses to a non-existed dir)", result);
    }
}

void TryOpenStreamReturnsFp(const char *filePath)
{
    FILE *fp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, NULL);

    if (fp != NULL)
    {
        LE_INFO("[PASSED] le_atomFile_TryOpenStream returns a file pointer if successful");
        le_atomFile_CloseStream(fp);
    }
    else
    {
        LE_INFO("[PASSED] le_atomFile_TryOpenStream doesn't return a file pointer if successful");
    }
}

void TryOpenStreamReturnsFault(const char *filePath)
{
    le_result_t result;
    le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, &result);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_TryOpenStream returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_NOT_FOUND if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns LE_WOULD_BLOCK if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryOpenStream returns '%d' if there was an error (accesses to a non-existed dir)", result);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void TryOpenStreamAcquiresFlock(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_TryOpenStream(filePath, LE_FLOCK_WRITE, NULL);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        le_atomFile_CloseStream(childFp);
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

        FILE *parentFp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
        LE_INFO("***second process is holding a file lock***");
        le_atomFile_CloseStream(parentFp);
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
        LE_INFO("***USAGE: app runProc atomTryOpenStream atomTryOpenStreamProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_TryOpenStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "wouldBlock") == 0)
    {
        TryOpenStreamReturnsWouldBlock(testFilePath);
    }
    else if (strcmp(testDescription, "notFound") == 0)
    {
        TryOpenStreamReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fp") == 0)
    {
        TryOpenStreamReturnsFp(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        TryOpenStreamReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "acquireFlock") == 0)
    {
        TryOpenStreamAcquiresFlock(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_TryOpenStream API===========================");

    exit(EXIT_SUCCESS);
}