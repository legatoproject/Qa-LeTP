/**
 * @file testUpdateCtrl.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/**
  The Legato system will be in probation period when this app is installed to the target.
  This app/process will take two parameters such as "updateCtrlApi name" and "test case number"
  to test differnt api's functionality. Verfication is done from the updateCtrlApi testing
  scripts
**/

#include "legato.h"
#include "interfaces.h" // update,updateCtrl APIs
#include <unistd.h> // getpid()
#include <sys/types.h> // kill()
#include <signal.h> // SIGKILL

// begin of macros
#define True 1
#define False 0
#define identical 0

// begin of global scope
pid_t CALLING_PID;

// begin of function prototypes
void TestMarkGood(const char*);
void TestMarkGoodWithInput(int);
void TestLockProbation(const char*);
void TestUnlockProbation(const char*);
void TestFailProbation(const char*);
void TestDefer(const char*);
void TestAllow(const char*);


//============================================================
COMPONENT_INIT
{
    // [0] = API name; [1] = testcase #
    if (le_arg_NumArgs() == 2)
    {
        const char *functionName = le_arg_GetArg(0);
        const char *testCaseNum = le_arg_GetArg(1);
        CALLING_PID = getpid();

        LE_INFO("---------------Begin-------------\n");
        LE_INFO("functionName: %s", functionName);
        LE_INFO("testCaseNum: %s", testCaseNum);
        LE_INFO("testUpdateCtrl process pid: %d", CALLING_PID);

        if (functionName && testCaseNum)
        {
            if (strcmp(functionName, "defer") == identical)
            {
                TestDefer(testCaseNum);
            }
            else if (strcmp(functionName, "allow") == identical)
            {
                TestAllow(testCaseNum);
            }
            else if (strcmp(functionName, "markGood") == identical)
            {
                TestMarkGood(testCaseNum);
            }
            else if (strcmp(functionName, "lockProbation") == identical)
            {
                TestLockProbation(testCaseNum);
            }
            else if (strcmp(functionName, "unLockProbation") == identical)
            {
                TestUnlockProbation(testCaseNum);
            }
            else if (strcmp(functionName, "failProbation") == identical)
            {
                TestFailProbation(testCaseNum);
            }
            else
            {
                exit(EXIT_SUCCESS);
            }
        } //end of if (functionName)
    } //end of if num of args = 2

    LE_INFO("----------------End--------------\n");
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_MarkGood()
  post - to test TestMarkGoodWithInput function according to the testCaseNum parameter
**/

void TestMarkGood(const char *testCaseNum)
{
    /*
        MarkGood(True)
        case 1: LE_OK
        case 4: LE_DUPLICATE
    */
    if (strncmp(testCaseNum, "1", 1) == identical || strncmp(testCaseNum, "5", 1) == identical)
    {
        TestMarkGoodWithInput(True);
    }
    /*
        MarkGood(True)
        case 3: LE_BUSY
    */
    else if (strncmp(testCaseNum, "3", 1) == identical)
    {
        le_updateCtrl_LockProbation();
        TestMarkGoodWithInput(True);
    }
    /*
        MarkGood(False)
        case 2: LE_BUSY
    */
    else if (strncmp(testCaseNum, "4", 1) == identical)
    {
        le_updateCtrl_LockProbation();
        TestMarkGoodWithInput(False);
    }
    /*
        MarkGood(False)
        case 2: LE_OK
        case 3: LE_DUPLICATE
    */
    else if (strncmp(testCaseNum, "2", 1) == identical || strncmp(testCaseNum, "6", 1) == identical)
    {
        TestMarkGoodWithInput(False);
    }
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_LockProbation()
  post - to test le_updateCtrl_LockProbation() function according to the testCaseNum parameter
**/

void TestLockProbation(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "1", 1) == identical || strncmp(testCaseNum, "2", 1) == identical
      || strncmp(testCaseNum, "4", 1) == identical)
    {
        le_updateCtrl_LockProbation();
    }
    else if (strncmp(testCaseNum, "3", 1) == identical)
    {
        if (CALLING_PID)
        {
            le_updateCtrl_LockProbation();
            kill(CALLING_PID, SIGKILL);
        }
    }
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_UnlockProbation()
  post - to test le_updateCtrl_UnlockProbation() function according to the testCaseNum parameter
**/

void TestUnlockProbation(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "1", 1) == identical)
    {
        le_updateCtrl_UnlockProbation();
    }
    else if (strncmp(testCaseNum, "2", 1) == identical)
    {
        le_updateCtrl_LockProbation();
        le_updateCtrl_LockProbation();
        le_updateCtrl_UnlockProbation();

        while (sleep(30))
        {
            LE_INFO("waiting...");
        }

        le_updateCtrl_UnlockProbation();
    }
    else if (strncmp(testCaseNum, "3", 1) == identical)
    {
        le_updateCtrl_LockProbation();
        le_updateCtrl_LockProbation();

        while (sleep(30))
        {
            LE_INFO("waiting...");
        }

        le_updateCtrl_UnlockProbation();
        le_updateCtrl_UnlockProbation();
    }
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_FailProbation()
  post - to test le_updateCtrl_FailProbation() function according to the testCaseNum parameter
**/

void TestFailProbation(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "1", 1) == identical || strncmp(testCaseNum, "2", 1) == identical)
    {
        le_updateCtrl_FailProbation();
    }
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_Defer()
  post - to test le_updateCtrl_Defer() function according to the testCaseNum parameter
**/

void TestDefer(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "1", 1) == identical || strncmp(testCaseNum, "2", 1) == identical
      || strncmp(testCaseNum, "3", 1) == identical || strncmp(testCaseNum, "6", 1) == identical)
    {
        le_updateCtrl_Defer();
    }
    else if (strncmp(testCaseNum, "4", 1) == identical)
    {
        if (CALLING_PID)
        {
            le_updateCtrl_Defer();
            kill(CALLING_PID, SIGKILL);
        }
    }
    else if (strncmp(testCaseNum, "5", 1) == identical)
    {
        le_updateCtrl_Defer();
        le_updateCtrl_FailProbation();
    }
}

/**
  pre -
  param - testCaseNum: the number of different test cases of le_updateCtrl_Allow()
  post - to test le_updateCtrl_Allow() function according to the testCaseNum parameter
**/

void TestAllow(const char *testCaseNum)
{
    if (strncmp(testCaseNum, "1", 1) == identical)
    {
        le_updateCtrl_Defer();
        le_updateCtrl_Defer();
        le_updateCtrl_Allow();

        // wait for 20s
        while (sleep(20))
        {
            LE_INFO("Waiting...");
        }

        le_updateCtrl_Allow();
    }
    else if (strncmp(testCaseNum, "2", 1) == identical)
    {
        // the first process
        LE_INFO("I am the testUpdateCtrl process with pid %d", CALLING_PID);
        le_updateCtrl_Defer();
        le_updateCtrl_Defer();

        // wait for 20s
        while (sleep(20))
        {
            LE_INFO("Waiting...");
        }

        le_updateCtrl_Allow();
        le_updateCtrl_Allow();
    }
    else if (strncmp(testCaseNum, "3", 1) == identical)
    {
        le_updateCtrl_Defer();
        le_updateCtrl_FailProbation();
        le_updateCtrl_Allow();
    }
}

/**
  pre -
  param - input: True/False parameter of le_updateCtrl_MarkGood()
  post - to test le_updateCtrl_MarkGood() function according to the input parameter
**/

void TestMarkGoodWithInput(int input)
{
    le_result_t markGoodResult = le_updateCtrl_MarkGood(input);

    if (markGoodResult == LE_OK)
    {
        LE_INFO("return LE_OK: The system was marked Good\n");
    }
    else if (markGoodResult == LE_DUPLICATE)
    {
        LE_INFO("return LE_DUPLICATE: Probation has expired - the system has already been marked Good\n");
    }
    else if (markGoodResult == LE_BUSY)
    {
        LE_INFO("return LE_BUSY: Someone holds a probation lock\n");
    }
    else
    {
        LE_INFO("return unexpected value\n");
    }
}