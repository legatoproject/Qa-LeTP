#include "legato.h"
#include <assert.h>

#define ROOT_DIR                  "/"
#define SANDBOX_HOME_DIR          "/"
#define LEGATO_DIR                "/legato"
#define LEGATO_CONFIG_TREE_DIR    "/legato/systems/current/config"
#define SB_CHROOT_DIR             "/SbChrootDir"


// Returns the current directory
void GetCurrentDirectory(char* cwd, size_t num_elements)
{
    if (getcwd(cwd, num_elements) != NULL)
    {
        LE_INFO(">> %s\n", cwd);
    }
    else
    {
        LE_INFO(">> %s\n", strerror(errno));
    }
}

// Changes the current directory and prints the current directory
void ChangeDirectory(char* path)
{
    if (chdir(path) != 0)
    {
        LE_INFO(">> %s\n", strerror(errno));
    }
}

/* L_SandBox_0001
 * rq10,20
 * Simple test to verify that our sandbox isolates our deployed application
 * from the rest of system (e.g legato folder) and other application */
void SB_10_20_30()
{
    LE_INFO("-------- SB_10_20_30 -------------- ");

    char cwd[1024];

    // should be /
    GetCurrentDirectory(cwd, sizeof(cwd));
    assert(strcmp(cwd, SANDBOX_HOME_DIR) == 0);

    // TODO: since home dir is no longer "/home/appAPPNAME", this section is kinda moot.
    // try to move to top level of sandbox -> "/"
    ChangeDirectory("..");
    ChangeDirectory("..");
    GetCurrentDirectory(cwd, sizeof(cwd));
    assert(strcmp(cwd, ROOT_DIR) == 0);

    // try to move beyond
    ChangeDirectory("..");
    GetCurrentDirectory(cwd, sizeof(cwd));
    assert(strcmp(cwd, ROOT_DIR) == 0); // if it does go beyond this path then error with sandbox

    // try to go to legato directory
    ChangeDirectory(LEGATO_DIR);
    GetCurrentDirectory(cwd, sizeof(cwd));
    assert(strcmp(cwd, ROOT_DIR) == 0); // should not be able to move there

    // try to go to legato config tree
    ChangeDirectory(LEGATO_CONFIG_TREE_DIR);
    GetCurrentDirectory(cwd, sizeof(cwd));
    assert(strcmp(cwd, ROOT_DIR) == 0); // should not be able to move there
    LE_INFO("Finishing SB_10_20_30");
}

/* L_SandBox_0004
 *req110 - send signals */
void SB_110()
{
    LE_INFO("-------- SB_110 -------------- ");

    pid_t pid, ppid;

    pid = getpid();
    ppid = getppid();

    LE_INFO("Current PID: %d", pid);
    LE_INFO("Parent PID: %d", ppid);

    /* Try to kill parent process owned by root*/
    LE_INFO("Attempting to kill parent process: %d", ppid);
    assert(kill(ppid, SIGKILL) != 0);

    /* Since no visibility of the processes, we will loop through arbitrary pid */
    int apid = 1;

    LE_INFO("Attempting to kill pid up to 100000, exccept for %d", pid);
    for (; apid < 100000; apid++)
    {
        // Try killing
        if (apid != pid)
        {
            // Make sure that it cannot kill processes other than itself
            assert(kill(apid, SIGKILL) != 0);

            // print all the actual running processes that we tried to kill
            if (errno == EPERM)
            {
                LE_INFO(">> trying to kill pid [%d], error [%s]", apid, strerror(errno));
            }
        }
    }
}

/* L_SandBox_0005
 * Breakout method: Using a temporary directory http://linux-vserver.org/Secure_chroot_Barrier
 * # mkdir foo
 * # chroot foo
 * # cd .. */
void SB_BreakOut1()
{
    LE_INFO("-------- SB_BreakOut1 -------------- ");

    char cwd[1024];
    // Start at home directory again
    ChangeDirectory(SANDBOX_HOME_DIR);
    GetCurrentDirectory(cwd, sizeof(cwd));
    char sandboxPath[100] = SANDBOX_HOME_DIR;
    if (le_utf8_Append(sandboxPath, SB_CHROOT_DIR, 100, NULL) == LE_OK)
    {
        LE_INFO("Creating directory %s in the sandbox", sandboxPath);

        if (mkdir(sandboxPath, S_IRUSR | S_IWUSR | S_IXUSR | S_IXOTH) == 0)
        {
            // chroot should not work
            LE_INFO("attempting to chroot %s", sandboxPath);
            assert(chroot(sandboxPath) != 0);
        }
        else
        {
            LE_INFO("Failed to create directory %s. %s", sandboxPath, strerror(errno));
        }
    }
}

/* L_SandBox_0006
 * Using chdir("..") many times */
void SB_BreakOut2()
{
    LE_INFO("-------- SB_BreakOut2 -------------- ");

    char cwd[1024];

    // Start at home directory again
    ChangeDirectory(SANDBOX_HOME_DIR);
    GetCurrentDirectory(cwd, sizeof(cwd));

    // Call chdir .. 10000 times
    int i = 0;
    for (; i < 10000; i++)
    {
        ChangeDirectory("..");
    }

    GetCurrentDirectory(cwd, sizeof(cwd));
    // No matter how many times we chdir, the farthest it can go is "/"
    assert(strcmp(cwd, ROOT_DIR) == 0);
}

COMPONENT_INIT
{
    int testCase = 0;

    if (le_arg_NumArgs() >= 1)
    {
        const char* arg1 = le_arg_GetArg(0);
        testCase = atoi(arg1);
    }

    switch (testCase)
    {
        case 1:
            SB_10_20_30();  // L_SandBox_0001
            break;
        case 2:
            SB_110();       // L_SandBox_0004
            break;
        case 3:
            SB_BreakOut1(); // L_SandBox_0005
            break;
        case 4:
            SB_BreakOut2(); // L_SandBox_0006
            break;
        default:
            break;
    }
    exit(EXIT_SUCCESS);
}
