#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void CreateStreamReturnsDuplicate(const char *filePath)
{
    le_result_t result;

    le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, &result);

    if (result == LE_DUPLICATE)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_CreateStream returns LE_DUPLICATE when file is already existed");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_CreateStream returns LE_FAULT when file is already existed");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_CreateStream returns %d when file is already existed", result);
    }
}

void CreateStreamReturnsFault(const char *filePath)
{
    le_result_t result;

    le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_FAIL_IF_EXIST, S_IRWXU, &result);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] resultPtr of le_atomFile_CreateStream returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_DUPLICATE)
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_CreateStream returns LE_DUPLICATE if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] resultPtr of le_atomFile_CreateStream returns %d if there was an error (accesses to a non-existed dir)", result);
    }
}

void CreateStreamReturnsFp(const char *filePath)
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
        FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, filePemissions[i], NULL);

        if (fp != NULL)
        {
            // commit all changes so that the test file can be created completely
            le_atomFile_CloseStream(fp);
            stat(filePath, &fileStat);

            bool isCorrectPermission = (fileStat.st_mode & filePemissions[i]) ? true : false;

            if (isCorrectPermission)
            {
                LE_INFO("[PASSED] le_atomFile_CreateStream can create and open file with specified file permission: %d if the file does not exist", filePemissions[i]);
            }
            else
            {
                LE_INFO("[FAILED] le_atomFile_CreateStream creates a file with unexpected file permission. Expected: %d; Actual: %d", filePemissions[i], fileStat.st_mode);
            }

            // removed the generated file
            unlink(filePath);
        }
        else
        {
            LE_INFO("[FAILED] le_atomFile_CreateStream returns a null file pointer when creates and opens a file with specified file permission: %d if the file does not exist", filePemissions[i]);
        }
    }
}

void CreateStreamAtomicWrt(const char *filePath)
{
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);

    while (true)
    {
        fprintf(fp, "String Foo");
        LE_INFO("writing data into the file");
        sleep(5);
    }
}

void CreateStreamAtomicRead(const char *filePath)
{
    char readBuffer[20] = {0};
    FILE *fp = le_atomFile_CreateStream(filePath, LE_FLOCK_READ, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);

    while (true)
    {
        fread(readBuffer, 1, 1, fp);
        LE_INFO("reading data from the file");
        sleep(5);
    }
}

void AtomicBlockingSigHandler(int sigNum)
{
    accessOK = true;
}

void CreateStreamAtomicBlocking(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
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

        FILE *parentFp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
        LE_INFO("***second process is holding a file lock***");
        le_atomFile_CloseStream(parentFp);
    }
    else
    {
        perror("kill()");
        exit(EXIT_FAILURE);
    }
}

void CreateStreamMultiAccess(const char *filePath)
{
    pid_t parentPID = getpid();
    pid_t pid = fork();

    // child
    if (pid == 0)
    {
        FILE *childFp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
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

        FILE *parentFp = le_atomFile_CreateStream(filePath, LE_FLOCK_WRITE, LE_FLOCK_OPEN_IF_EXIST, S_IRWXU, NULL);
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
        LE_INFO("***USAGE: app runProc atomCreate atomCreateProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_CreateStream API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "duplicate") == 0)
    {
        CreateStreamReturnsDuplicate(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        CreateStreamReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "fp") == 0)
    {
        CreateStreamReturnsFp(testFilePath);
    }
    else if (strcmp(testDescription, "atomicWrt") == 0)
    {
        CreateStreamAtomicWrt(testFilePath);
    }
    else if (strcmp(testDescription, "atomicRead") == 0)
    {
        CreateStreamAtomicRead(testFilePath);
    }
    else if (strcmp(testDescription, "atomicBlocking") == 0)
    {
        CreateStreamAtomicBlocking(testFilePath);
    }
    else if (strcmp(testDescription, "atomicMultiAccess") == 0)
    {
        CreateStreamMultiAccess(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_CreateStream API===========================");

    exit(EXIT_SUCCESS);
}