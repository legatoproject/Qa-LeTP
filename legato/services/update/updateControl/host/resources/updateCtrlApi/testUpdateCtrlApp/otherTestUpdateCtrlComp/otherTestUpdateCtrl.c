/**
 * @file otherTestUpdateCtrl.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/**
    The Legato system will be in probation period when this app is installed to the target.
    This app/process will take two parameters such as "updateCtrlApi name" and "test case number"
    to test le_updateCtrl_UnlockProbation() and le_updateCtrl_Allow() for the test case that
    requires two processes (testUpdateCtrl and otherTestUpdateCtrl processes).
    Verfication is done from the updateCtrlApi testing scripts
**/

#include "legato.h"
#include "interfaces.h"
#include <unistd.h> // getpid()

// begin of macros
#define Identical 0

// begin of function prototypes
void TestUnlockProbation(const char*);
void TestAllow(const char*);

COMPONENT_INIT
{
    // [0] = API name; [1] = testcase #
    if (le_arg_NumArgs() == 2)
    {
        const char *functionName = le_arg_GetArg(0);
        const char *testCaseNum = le_arg_GetArg(1);

        LE_INFO("otherTestUpdateCtrl process pid: %d", getpid());

        if (functionName && testCaseNum)
        {
            if (strcmp(functionName, "unLockProbation") == Identical)
            {
                TestUnlockProbation(testCaseNum);
            }
            else if (strcmp(functionName, "allow") == Identical)
            {
                TestAllow(testCaseNum);
            }
            else
            {
                exit(EXIT_SUCCESS);
            }
        }
    }
}

/**
  pre -
  param - testCaseNum: the test case number that requires to test le_updateCtrl_UnlockProbation()
                       in multiple processes
  post - to test le_updateCtrl_UnlockProbation() function according to the testCaseNum parameter
**/

void TestUnlockProbation(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "3", 1) == Identical)
    {
        le_updateCtrl_UnlockProbation();
        le_updateCtrl_UnlockProbation();
    }
}

/**
  pre -
  param - testCaseNum: the test case number that requires to test le_updateCtrl_Allow()
                       in multiple processes
  post - to test le_updateCtrl_Allow() function according to the testCaseNum parameter
**/

void TestAllow(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "2", 1) == Identical)
    {
        le_updateCtrl_Allow();
        le_updateCtrl_Allow();
    }
}