/**
 * @file CoreDumpFileSizeTest.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/*
 * This app tests the limit of maximum core dump file size
 *
 * test case "SB_17"
 *
 *
 */

#include "legato.h"

static int getCoreSizeResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_CORE, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for max size of core dump. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}

COMPONENT_INIT
{
    LE_INFO("###### CoreDumpFileSizeTest app BEGIN #####");

    // Get the Max Core Dump Size Resource Limit setting
    int CoreSizeResLim = getCoreSizeResLimSetting();
    LE_INFO("CoreSize limit is: %d", CoreSizeResLim);

    if (CoreSizeResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped\n");
        LE_INFO("Core dump file limit test PASSED.\n");
        exit(EXIT_SUCCESS);
    }


    struct stat filestat;


    // Fork a process that seg faults and should successfully create a core dump.
    pid_t pid = fork();
    LE_ASSERT(pid >= 0);

    if (pid == 0)
    {
        // Create a core dump file by seg faulting.
        int i = *(int*)0;
        LE_DEBUG("i is: %d", i);

        LE_FATAL("Should not get here.");
    }

    // Wait till the child is done.
    int status;
    LE_ASSERT(wait(&status) != -1);

    LE_ASSERT(WIFSIGNALED(status));

    // if core size limit is set to be at least 4096 (ie. the size of one page), then a core dump should be created
    if (CoreSizeResLim >= 4096)
    {

        // returns true if the child produced a core dump
        LE_ASSERT(WCOREDUMP(status));


        // find out the file name of the core dump
        // NOTE THAT this is assuming the core dump file name has a leading "core"
        // the file name pattern is in /proc/sys/kernel/core_pattern
        char* coreFileName;
        DIR* dirp;
        dirp = opendir(".");
        if (dirp == NULL)
        {
            LE_INFO("opendir error: %s", strerror(errno));
            exit(EXIT_FAILURE);
        }

        struct dirent* dp;
        while ((dp = readdir(dirp)) != NULL)
        {
            if (strncmp(dp->d_name, "core", 4) == 0)
            {
                LE_INFO("file name is: %s", dp->d_name);
                coreFileName = strdup(dp->d_name);
            }
        }
        closedir(dirp);

        if (stat(coreFileName, &filestat) == -1)
        {
            LE_INFO("stat error: %s", strerror(errno));
            free(coreFileName);
            exit(EXIT_FAILURE);
        }
        LE_INFO("Core dump file status: size %lld bytes", (long long) filestat.st_size);


        // the core dump file size seems to round up somewhere in the middle between a complete page.
        // For example, a limit setting of 8191, 8192, and 8193 all rounds to an actual size of 8192
        // The point of this logic is to check that the core file size isn't too big and is set (somewhat) according
        // to the limit
        LE_FATAL_IF((filestat.st_size > ((CoreSizeResLim / 4096) + 1) * 4096), "Core dump file size might be too big");

        LE_ASSERT(remove(coreFileName) == 0);

        free(coreFileName);
    }
    //if core size limit is set to be less than 4096, then no core dump should be created
    else {
        LE_FATAL_IF(WCOREDUMP(status), "Core dump file created but should not have been.");
    }

    LE_INFO("Core dump file limit test PASSED.");
    exit(EXIT_SUCCESS);
}
