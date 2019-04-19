#include "legato.h"
#include "interfaces.h"


COMPONENT_INIT
{
    char option[10];
    char destStr[50];
    char srcStr[50];
    int nbArg = le_arg_NumArgs();
    long cycles;

    if (nbArg >= 1)
    {
        strcpy(option, le_arg_GetArg(0));
        if (nbArg >= 2)
        {
            strcpy(destStr, le_arg_GetArg(1));
            if (nbArg >= 3)
            {
                strcpy(srcStr, le_arg_GetArg(2));
            }
        }        
    }
    else
    {
        LE_INFO("TODO: \"app runProc testSandBoxBasic --exe=test_ctrl -- <options>\"");
    }

    if (strcmp(option, "getdir") == 0)
    {
        char cwd[1024];
        ctrl_GetCurrentDirectory(cwd, sizeof(cwd));
    }
    else if (strcmp(option, "changedir") == 0)
    {
        LE_INFO("Change the directory to [%s].", destStr);
        cycles = strtol(le_arg_GetArg(2), NULL, 0);
        ctrl_ChangeDirectory(destStr,cycles);
    }
    else if (strcmp(option, "createdir") == 0)
    {
        LE_INFO("destination directory is: %s%s", destStr, srcStr);
        ctrl_CreateDirectory(destStr, srcStr);
    }
    else if (strcmp(option,"getpid") == 0)
    {
        ctrl_GetProcesses();
    }
    else if (strcmp(option, "killpid") == 0)
    {
        int pid = strtol(le_arg_GetArg(1), NULL, 0);
        ctrl_KillProcesses(pid);
    }
    else
    {
        LE_ERROR("Invalid parameters");
    }

    exit(EXIT_SUCCESS);
}
