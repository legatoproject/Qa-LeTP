/**
 * @file atomOpenStream.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void OpenStreamReturnsNotFound(const char *filePath)
{
    le_result_t result;
    le_atomFile_OpenStream(filePath, LE_FLOCK_READ, &result);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_OpenStream returns LE_NOT_FOUND when opens a not existed file");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_OpenStream returns LE_FAULT when opens a not existed file");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_OpenStream returns %d when opens a not existed file", result);
    }
}

void OpenStreamReturnsFault(const char *filePath)
{
    le_result_t result;
    le_atomFile_OpenStream(filePath, LE_FLOCK_READ, &result);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_OpenStream returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_OpenStream returns LE_NOT_FOUND if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_OpenStream returns %d if there was an error (accesses to a non-existed dir)", result);
    }
}

void OpenStreamReturnsFp(const char *filePath)
{
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);

    if (fp != NULL)
    {
        LE_INFO("[PASSED] le_atomFile_OpenStream returns the file pointer to the file if successfully");
        le_atomFile_CloseStream(fp);
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_OpenStream doesn't return the file pointer to the file if successfully");
    }
}

void OpenStreamAtomicRead(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_READ, NULL);

    while(true)
    {
        fread(readBuffer, 1, 1, fp);
        LE_INFO("***reading data from the file***");
        sleep(5);
    }
}

void OpenStreamAtomicWrt(const char *filePath)
{
    FILE *fp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);

    while(true)
    {
        fprintf(fp, "String Foo");
        LE_INFO("***writing data into the file***");
        sleep(5);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void OpenStreamAtomicBlocking(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        le_atomFile_CloseStream(childFp);
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

        FILE *parentFp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
        LE_INFO("***second process is holding a file lock***");
        le_atomFile_CloseStream(parentFp);
    }
    else
    {
        perror("kill()");
        exit(EXIT_FAILURE);
    }
}

void OpenStreamAtomicMultiAccess(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
        // send a signal to the parent to indicate that it can place
        // another file lock to the same file
        kill(parentPID, SIGCONT);
        LE_INFO("***first process is holding a file lock***");
        sleep(60);
        fprintf(childFp, "string foo");
        le_atomFile_CloseStream(childFp);
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

        FILE *parentFp = le_atomFile_OpenStream(filePath, LE_FLOCK_WRITE, NULL);
        LE_INFO("***second process is holding a file lock***");

        while (true)
        {
            fprintf(parentFp, "string 123");
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
        LE_INFO("***USAGE: app runProc atomOpenStream atomOpenStreamProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_OpenStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "notFound") == 0)
    {
        OpenStreamReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        OpenStreamReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "fp") == 0)
    {
        OpenStreamReturnsFp(testFilePath);
    }
    else if (strcmp(testDescription, "atomicWrt") == 0)
    {
        OpenStreamAtomicWrt(testFilePath);
    }
    else if (strcmp(testDescription, "atomicRead") == 0)
    {
        OpenStreamAtomicRead(testFilePath);
    }
    else if (strcmp(testDescription, "atomicBlocking") == 0)
    {
        OpenStreamAtomicBlocking(testFilePath);
    }
    else if (strcmp(testDescription, "atomicMultiAccess") == 0)
    {
        OpenStreamAtomicMultiAccess(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_OpenStream API===========================");

    exit(EXIT_SUCCESS);
}