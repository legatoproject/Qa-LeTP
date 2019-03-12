#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void DeleteReturnsOK(const char *filePath)
{
    le_result_t result = le_atomFile_Delete(filePath);

    if (result == LE_OK)
    {
        LE_INFO("[PASSED] le_atomFile_Delete returns LE_OK if successful");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_NOT_FOUND if successful");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_FAULT if successful");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns '%d' if successful", result);
    }
}

void DeleteReturnsNotFound(const char *filePath)
{
    le_result_t result = le_atomFile_Delete(filePath);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] le_atomFile_Delete returns LE_NOT_FOUND if file doesn't exists");
    }
    else if (result == LE_OK)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_OK if file doesn't exists");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_FAULT if file doesn't exists");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns '%d' if file doesn't exists", result);
    }
}

void DeleteReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_Delete(filePath);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_Delete returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_NOT_FOUND if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_OK)
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns LE_OK if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Delete returns '%d' if there was an error (accesses to a non-existed dir)", result);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void DeleteAtomicBlocking(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);
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

        le_atomFile_Delete(filePath);
        LE_INFO("***second process removes the file***");
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
        LE_INFO("***USAGE: app runProc atomDelete atomDeleteProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_Delete API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "notFound") == 0)
    {
        DeleteReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        DeleteReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "ok") == 0)
    {
        DeleteReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "atomicBlocking") == 0)
    {
        DeleteAtomicBlocking(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }


    LE_INFO("====================END le_atomFile_Delete API===========================");

    exit(EXIT_SUCCESS);
}