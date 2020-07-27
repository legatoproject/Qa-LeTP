/**
 * @file atomCreate.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void CreateReturnsDuplicate(const char *filePath)
{
    le_result_t result = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (result == LE_DUPLICATE)
    {
        LE_INFO("[PASSED] le_atomFile_Create returns LE_DUPLICATE if the file already existed");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_Create returns LE_FAULT if the file already existed");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Create returns %d if the file already existed", result);
    }
}

void CreateReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_Create returns LE_FAULT when there was an error (accesses to non-existed dir)");
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] le_atomFile_Create returns LE_DUPLICATE when there was an error (accesses to non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_Create returns %d when there was an error (accesses to non-existed dir)", result);
    }
}

void CreateReturnsFd(const char *filePath)
{
    const int numOfFilePermissions = 18;
    int i;

    // full list obtained from https://www.gnu.org/software/libc/manual/html_node/Permission-Bits.html
    const mode_t filePemissions[] = {
        S_IRUSR,        //0400  Read permission bit for the owner of the file
        S_IREAD,        //0400  Read permission bit for the owner of the file
        S_IWUSR,        //0200  Write permission bit for the owner of the file
        S_IWRITE,       //0200  Write permission bit for the owner of the file
        S_IXUSR,        //0100  Execute (for ordinary files) or search (for directories) permission bit for the owner of the file
        S_IEXEC,        //0100  Execute (for ordinary files) or search (for directories) permission bit for the owner of the file
        S_IRWXU,        //This is equivalent to ‘(S_IRUSR | S_IWUSR | S_IXUSR)’
        S_IRGRP,        //040   Read permission bit for the group owner of the file
        S_IWGRP,        //020   Write permission bit for the group owner of the file
        S_IXGRP,        //010   Execute or search permission bit for the group owner of the file
        S_IRWXG,        //This is equivalent to ‘(S_IRGRP | S_IWGRP | S_IXGRP)’
        S_IROTH,        //04    Read permission bit for other users
        S_IWOTH,        //02    Write permission bit for other users
        S_IXOTH,        //01    Execute or search permission bit for other users
        S_IRWXO,        //This is equivalent to ‘(S_IROTH | S_IWOTH | S_IXOTH)’
        S_ISUID,        //04000 This is the set-user-ID on execute bit
        S_ISGID,        //02000 This is the set-group-ID on execute bit
        S_ISVTX,        //01000 This is the sticky bit
    };

    // remove any system default 'masked' file permission for the process
    umask(0);

    for (i = 0; i < numOfFilePermissions; i++)
    {
        struct stat fileStat;
        int fd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, filePemissions[i]);

        if (fcntl(fd, F_GETFD) != -1)
        {
            // commit all changes so that the test file can be created completely
            le_atomFile_Close(fd);
            stat(filePath, &fileStat);

            bool isCorrectPermission = (fileStat.st_mode & filePemissions[i]) ? true : false;

            if (isCorrectPermission)
            {
                LE_INFO("[PASSED] le_atomFile_Create can create and open file with specified file permission: %d if the file does not exist", filePemissions[i]);
            }
            else
            {
                LE_INFO("[FAILED] le_atomFile_Create creates a file with unexpected file permission. Expected: %d; Actual: %d", filePemissions[i], fileStat.st_mode);
            }

            // removed the generated file
            unlink(filePath);
        }
        else if (fd == LE_FAULT)
        {
            LE_INFO("[FAILED] le_atomFile_Create returns LE_FAULT when creates and opens a file with specified file permission if the file does not exist");
        }
        else if (fd == LE_DUPLICATE)
        {
            LE_INFO("[FAILED] le_atomFile_Create returns LE_DUPLICATE when creates and opens a file with specified file permission if the file does not exist");
        }
        else
        {
            LE_INFO("[FAILED] le_atomFile_Create returns %d when creates and opens a file with specified file permission if the file does not exist", fd);
        }
    }
}

void CreateAtomicWrt(const char *filePath)
{
    int fd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);

    while (true)
    {
        write(fd, "String Foo", sizeof("String Foo"));
        LE_INFO("writing data into the file");
        sleep(5);
    }
}

void CreateAtomicRead(const char *filePath)
{
    char readBuffer[20] = {0};
    int fd = le_atomFile_Create(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);

    while(true)
    {
        read(fd, readBuffer, 1);
        LE_INFO("reading data from the file");
        sleep(5);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void CreateAtomicBlocking(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
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

        int parentFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
        LE_INFO("***second process is holding a file lock***");
        le_atomFile_Close(parentFd);
    }
    else
    {
        perror("kill()");
        exit(EXIT_FAILURE);
    }
}

void CreateAtomicMultiAccess(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        int childFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
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

        int parentFd = le_atomFile_Create(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU);
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
        LE_INFO("***USAGE: app runProc atomCreate atomCreateProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_Create API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "duplicate") == 0)
    {
        CreateReturnsDuplicate(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        CreateReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "fd") == 0)
    {
        CreateReturnsFd(testFilePath);
    }
    else if (strcmp(testDescription, "atomicWrt") == 0)
    {
        CreateAtomicWrt(testFilePath);
    }
    else if (strcmp(testDescription, "atomicRead") == 0)
    {
        CreateAtomicRead(testFilePath);
    }
    else if (strcmp(testDescription, "atomicBlocking") == 0)
    {
        CreateAtomicBlocking(testFilePath);
    }
    else if (strcmp(testDescription, "atomicMultiAccess") == 0)
    {
        CreateAtomicMultiAccess(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_Create API===========================");

    exit(EXIT_SUCCESS);
}