/*
 * This app tests the limit on the number of signals that may be queued for the real user ID of the calling process.
 *
 * test case "SB_11"
 *
 *
 */


#include "legato.h"

static int getSigPendingResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_SIGPENDING, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for max signal queued for a process. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}




COMPONENT_INIT
{
    LE_INFO("###### NumSigQueuedTest app BEGIN #####");

    // Get the Max Signal Pending Resource Limit setting
    int SigPendingResLim = getSigPendingResLimSetting();
    LE_INFO("SigPending limit is: %d", SigPendingResLim);

    if (SigPendingResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped");
        LE_INFO("Signal queue limit test PASSED.");
        exit(EXIT_SUCCESS);
    }


    int NumSigQueued = SigPendingResLim;



#define RTSIG       SIGRTMIN  // define the realtime signal to use.

    // Fork off another process and send realtime signals to it.
    pid_t pid = fork();

    LE_ASSERT(pid >= 0);

    if (pid == 0)
    {
        // Block the signal.
        sigset_t sigSet;
        LE_ASSERT(sigemptyset(&sigSet) == 0);
        LE_ASSERT(sigaddset(&sigSet, RTSIG) == 0);
        LE_ASSERT(pthread_sigmask(SIG_BLOCK, &sigSet, NULL) == 0);

        // Pause the child.  It does nothing but sits and waits for signals.
        pause();
    }

    // Send the child realtime signals until we hit the limit.
    const union sigval value = {.sival_int = 0};

    int i;
    for (i = 0; i < NumSigQueued; i++)
    {
        LE_FATAL_IF(sigqueue(pid, RTSIG, value) == -1, "Could not queue more signals.  i == %d. %s", i, strerror(errno));
    }

    // Send one more signal that should fail.
    bool limitCorrect = false;
    if (sigqueue(pid, RTSIG, value) == -1)
    {
        if (errno == EAGAIN)
        {
            limitCorrect = true;
            LE_INFO("Could not send realtime signal because the signal queue is full which is correct.");
        }
        else
        {
            LE_ERROR("Could not send realtime signal for an unexpected reason. %s", strerror(errno));
        }
    }
    else
    {
        LE_ERROR("Sent realtime signl and exceeded the limit which is incorrect.");
    }

    // Kill the child.
    LE_ASSERT(kill(pid, SIGKILL) == 0);

    // Wait till the child is done.
    LE_ASSERT(wait(NULL) != -1);

    if (!limitCorrect)
    {
        exit(EXIT_FAILURE);
    }

    LE_INFO("Signal queue limit test PASSED.");


    exit(EXIT_SUCCESS);
}
