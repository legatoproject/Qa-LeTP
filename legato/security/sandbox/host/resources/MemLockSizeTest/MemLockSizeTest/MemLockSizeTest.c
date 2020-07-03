/**
 * @file MemLockSizeTest.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/*
 * This app tests the limit of maximum number of bytes of memory that may be locked into RAM
 *
 * test case "SB_12"
 *
 *
 */


#include "legato.h"
#include <sys/mman.h>

static int getMemLockSizeResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_MEMLOCK, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for max size of mem lock. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}




COMPONENT_INIT
{
    LE_INFO("###### MemLockSizeTest app BEGIN #####");

    // Get the Max MemLockSize Resource Limit setting
    int MemLockSizeResLim = getMemLockSizeResLimSetting();
    LE_INFO("MemLockSize limit is: %d", MemLockSizeResLim);

    if (MemLockSizeResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped");
        LE_INFO("Memory lock size limit test PASSED.");
        exit(EXIT_SUCCESS);
    }


    int rc, i, j, err;
    long pageSize = sysconf(_SC_PAGESIZE);
    long numPages = ((MemLockSizeResLim / pageSize) + 1);
    long arraySize = numPages * pageSize;
    char array[arraySize];

    // lock 1 byte (and hence the page that it resides) into memory
    // all of these locks are expected to succeed - the number of locks are right at the configured limit
    for (i = 0, j = 0; i < (numPages - 1); i++, j = j + pageSize)
    {
        rc = mlock(&array[j], 1);
        LE_ASSERT(rc == 0);
    }

    // perform one more lock that's expected to fail
    rc = mlock(&array[j], 1);
    err = errno;
    LE_FATAL_IF(rc == 0, "should not have been able to lock memory.");
    LE_INFO("The error for the last mlock that's expected to fail is: %s", strerror(err));

    LE_INFO("Memory lock size limit test PASSED.");


    exit(EXIT_SUCCESS);
}
