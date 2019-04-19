#include "legato.h"
#include <assert.h>
#include <dirent.h>
#include <arpa/inet.h>


// Returns the current directory
void ctrl_GetCurrentDirectory(char* cwd, size_t num_elements)
{
    if (getcwd(cwd, num_elements) != NULL)
    {
        LE_INFO(">> The current dir is: [%s].\n", cwd);
    }
    else
    {
        LE_INFO(">> %s\n", strerror(errno));
    }
}

// Changes the current directory and prints the current directory
void ctrl_ChangeDirectory(char* path, long loop)
{
    char cwd[1024];
    for(long i=1;i<=loop;i++)
    {
        if (chdir(path) != 0)
        {
            LE_INFO(">> %s\n", strerror(errno));
        }
        
        if (getcwd(cwd, sizeof(cwd)) != NULL)
        {
            LE_INFO(">> The current dir is: [%s]. Loop: [%li]\n", cwd, i);
        }

    }
}

// Create new directory and check that chroot should not work
void ctrl_CreateDirectory(char* destStr, char* srcStr)
{
    if (le_utf8_Append(destStr, srcStr, 100, NULL) == LE_OK)
    {
        LE_INFO("Creating directory [%s] in the sandbox", destStr);

        if (mkdir(destStr, S_IRUSR | S_IWUSR | S_IXUSR | S_IXOTH) == 0)
        {
            // chroot should not work
            LE_INFO("attempting to chroot [%s].", destStr);
            assert(chroot(destStr) != 0);
        }
        else
        {
            LE_INFO("Failed to create directory %s. %s", destStr, strerror(errno));
        }
    }
}

void ctrl_GetProcesses()
{
    pid_t pid, ppid;

    pid = getpid();
    ppid = getppid();

    LE_INFO("Current PID: [%d]", pid);
    LE_INFO("Parent PID: [%d]", ppid);
}

void ctrl_KillProcesses(int pid)
{
    if (kill(pid, SIGKILL) == 0)
    {
        LE_INFO("Able to kill process: [%d]", pid);
    }
    else
    {
        LE_INFO(">> trying to kill pid [%d], error [%s]", pid, strerror(errno));
    }
}


COMPONENT_INIT
{
    LE_INFO("... BEGIN TEST ...");
}
