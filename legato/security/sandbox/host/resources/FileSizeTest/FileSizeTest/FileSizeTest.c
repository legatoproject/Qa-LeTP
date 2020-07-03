/**
 * @file FileSizeTest.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/*
 * This app tests max file size that a process can create
 *
 * test case "SB_08"
 *
 *
 */


#include "legato.h"

static int getFileSizeResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_FSIZE, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for max file size for a process. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}




COMPONENT_INIT
{
    LE_INFO("###### FileSizeTest app BEGIN #####");

    // Get the File Size Resource Limit setting
    int FileSizeResLim = getFileSizeResLimSetting();
    LE_INFO("FileSize limit is: %d", FileSizeResLim);

    if (FileSizeResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped");
        LE_INFO("File size limit test PASSED.");
        exit(EXIT_SUCCESS);
    }


    int FileSize = FileSizeResLim;

    // Fork off a process to create a file.
    pid_t pid = fork();
    LE_ASSERT(pid >= 0);

    if (pid == 0)
    {
        // Have the child create another file.
        // Create another file that should be large enough to overflow our apps file system.
        int fd = open("test3", O_CREAT | O_WRONLY, S_IRUSR | S_IWUSR);
        LE_ASSERT(fd != -1);

        int i;
        for (i = 0; i < FileSize; i++)
        {
            LE_ASSERT(write(fd, "b", 1) == 1);
        }

        // Write one more byte to this file.  This should cause a SIGXFSZ to be sent to us and kill us.
        if (write(fd, "b", 1) != 1)
        {
            LE_ASSERT(close(fd) != -1);
            LE_FATAL("Could not write to file for an unexpected reason.  %m");
        }
        else
        {
            LE_ASSERT(close(fd) != -1);
            LE_FATAL("Should not have been able to write anymore to the file.");
        }
    }


    // Wait till the child is done.
    int status;
    LE_ASSERT(wait(&status) != -1);

    LE_ASSERT(WIFSIGNALED(status));
    LE_ASSERT(WTERMSIG(status) == SIGXFSZ);

    // Delete the file.
    LE_ASSERT(remove("test3") == 0);

    LE_INFO("File size limit test PASSED.");


    exit(EXIT_SUCCESS);
}
