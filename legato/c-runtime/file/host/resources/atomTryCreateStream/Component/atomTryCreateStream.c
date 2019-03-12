#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void TryCreateStreamReturnsDuplicate(const char *filePath)
{
    le_result_t result;
    le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, &result);

    if (result == LE_DUPLICATE)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_TryCreateStream returns LE_DUPLICATE if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns LE_WOULD_BLOCK if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns LE_FAULT if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns '%d' if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode", result);
    }
}

void TryCreateStreamReturnsWouldBlock(const char *filePath)
{
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, NULL);

    le_result_t result;
    le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, &result);

    if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_TryCreateStream returns LE_WOULD_BLOCK if there is already an incompatible lock on the file.");
        le_atomFile_CloseStream(fp);
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns LE_DUPLICATE if there is already an incompatible lock on the file.");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns LE_FAULT if there is already an incompatible lock on the file.");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_TryCreateStream returns '%d' if there is already an incompatible lock on the file.", result);
    }
}

void TryCreateStreamReturnsFp(const char *filePath)
{
    FILE *fp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, NULL);

    if (fp != NULL)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreateStream returns a file pointer if successful");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreateStream doesn't return a file pointer");
    }
}

void TryCreateStreamReturnsFault(const char *filePath)
{
    le_result_t result;
    le_atomFile_TryCreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, &result);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreateStream returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreateStream returns LE_WOULD_BLOCK if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreateStream returns LE_DUPLICATE if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreateStream returns '%d' if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode", result);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void TryCreateStreamAcquiresFlock(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_TryCreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, NULL);
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

        FILE *parentFp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, NULL);
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
        LE_INFO("***USAGE: app runProc atomTryCreateStream atomTryCreateStreamProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_TryCreateStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "duplicate") == 0)
    {
        TryCreateStreamReturnsDuplicate(testFilePath);
    }
    else if (strcmp(testDescription, "wouldBlock") == 0)
    {
        TryCreateStreamReturnsWouldBlock(testFilePath);
    }
    else if (strcmp(testDescription, "fp") == 0)
    {
        TryCreateStreamReturnsFp(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        TryCreateStreamReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "acquireFlock") == 0)
    {
        TryCreateStreamAcquiresFlock(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_TryCreateStream API===========================");

    exit(EXIT_SUCCESS);
}