#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void TryCreateReturnsDuplicate(const char *filePath)
{
    le_result_t result = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (result == LE_DUPLICATE)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreate returns LE_DUPLICATE if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_WOULD_BLOCK if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_FAULT if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns '%d' if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode", result);
    }
}

void TryCreateReturnsWouldBlock(const char *filePath)
{
    int fd = le_atomFile_Create(filePath, LE_FLOCK_READ, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);
    le_result_t result = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreate returns LE_WOULD_BLOCK if there is already an incompatible lock on the file.");
        le_atomFile_Close(fd);
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_DUPLICATE if there is already an incompatible lock on the file.");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_FAULT if there is already an incompatible lock on the file.");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns '%d' if there is already an incompatible lock on the file.", result);
    }
}

void TryCreateReturnsFd(const char *filePath)
{
    int fd = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (fcntl(fd, F_GETFD) != -1)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreate returns a file descriptor if successful");
        le_atomFile_Close(fd);
    }
    else if (fd == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_DUPLICATE when tries to create and open an existed file");
    }
    else if (fd == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_FAULT if when tries to create and open an existed file");
    }
    else if (fd == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_WOULD_BLOCK if when tries to create and open an existed file");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns '%d' if when tries to create and open an existed file", fd);
    }
}

void TryCreateReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_TryCreate(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_TryCreate returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_WOULD_BLOCK if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns LE_DUPLICATE if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryCreate returns '%d' if the file already exists and LE_FLOCK_FAIL_IF_EXIST is specified in createMode", result);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void TryCreateAcquiresFlock(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_TryCreate(filePath, LE_FLOCK_READ, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);
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

        int parentFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);
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
        LE_INFO("***USAGE: app runProc atomTryCreate atomTryCreateProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_TryCreate API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "duplicate") == 0)
    {
        TryCreateReturnsDuplicate(testFilePath);
    }
    else if (strcmp(testDescription, "wouldBlock") == 0)
    {
        TryCreateReturnsWouldBlock(testFilePath);
    }
    else if (strcmp(testDescription, "fd") == 0)
    {
        TryCreateReturnsFd(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        TryCreateReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "acquireFlock") == 0)
    {
        TryCreateAcquiresFlock(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_TryCreate API===========================");

    exit(EXIT_SUCCESS);
}