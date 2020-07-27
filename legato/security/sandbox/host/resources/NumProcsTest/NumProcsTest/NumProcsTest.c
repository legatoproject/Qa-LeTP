/**
 * @file NumProcsTest.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/*
 * This app tests max number of processes that a calling process can create
 *
 * test case "SB_16"
 *
 *
 */


#include "legato.h"

static int getNumProcsResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_NPROC, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for max num procs for a process. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}




COMPONENT_INIT
{
    LE_INFO("###### NumProcsTest app BEGIN #####");

    // Get the Num Procs Resource Limit setting
    int NumProcsResLim = getNumProcsResLimSetting();
    LE_INFO("NumProcs limit is: %d\n", NumProcsResLim);

    if (NumProcsResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped");
        LE_INFO("Number of processes limit test PASSED.");
        exit(EXIT_SUCCESS);
    }


    int NumProcs = NumProcsResLim;


    // Start forking processes until we hit the limit.  Remember to include the current process.
    pid_t pid[NumProcs - 1];
    int i;
    for (i = 0; i < NumProcs - 1; i++)
    {
        pid[i] = fork();

        LE_FATAL_IF(pid[i] < 0, "Could not fork.  i == %d. %m", i);

        if (pid[i] == 0)
        {
            // This is the child process just pause here.
            pause();
            exit(EXIT_SUCCESS);
        }
    }

    // Try one more fork.
    bool limitCorrect = false;
    pid_t extraPid = fork();

    if ((extraPid == -1) && (errno == EAGAIN))
    {
        LE_INFO("Could not create more than %d processes.  The limit was set correctly.",
                (int)NumProcs);
        limitCorrect = true;
    }
    else if (extraPid == 0)
    {
        // This is the child process just pause here.
        pause();
        exit(EXIT_SUCCESS);
    }
    else
    {
        LE_ERROR("Created more than %d processes.  The limit was not set correctly.",
        (int)NumProcs);
    }

    // Kill all child processes
    for (i = 0; i < NumProcs - 1; i++)
    {
        LE_ASSERT(kill(pid[i], SIGKILL) == 0);
    }

    if (!limitCorrect)
    {
        // Kill the extra process.
        LE_ASSERT(kill(extraPid, SIGKILL) == 0);
    }

    // Wait for all children to terminate.
    while ((wait(NULL) != -1) || (errno != ECHILD)) {}

    LE_FATAL_IF(!limitCorrect, "Number of process limit is incorrect.");

    LE_INFO("Number of processes limit test PASSED.");



    exit(EXIT_SUCCESS);
}
