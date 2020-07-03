/**
 * @file FdTest.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/*
 * This app tests file descriptor limit by creating many different file types.
 *
 * test case "SB_04"
 *
 *
 */

#include "legato.h"
#include <dirent.h>


static int getFdResLimSetting()
{
    struct rlimit lim;

    if (getrlimit(RLIMIT_NOFILE, &lim) == -1)
    {
        LE_INFO("Error getting current resource limit for file descriptor. error: %s", strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
    {
        return lim.rlim_cur;
    }
}


static int isFdValid(int fd)
{
    return (fcntl(fd, F_GETFD) != -1);
}


COMPONENT_INIT
{
    LE_INFO("###### FdTest app BEGIN #####");

    // Get the FD Resource Limit setting
    int FdResLim = getFdResLimSetting();
    LE_INFO("Fd limit is: %d", FdResLim);

    if (FdResLim == -1)
    {
        LE_INFO("Resource limit is set to unlimited. Test skipped");
        exit(EXIT_SUCCESS);
    }

    int i = 0;
    while (isFdValid(i) == 1)
    {
        i++;
    }

    // i is the first fd that's invalid, which happens to be the number of fds already used
    int num_std_fd = i;
    LE_INFO("%d fd are already opened by this app.", num_std_fd);


    int fpArraySize = FdResLim - 1 - num_std_fd;

    // Create "fd resource limit - 1" number of file streams
    // open files with fopen
    FILE* fp[fpArraySize];
    for (i = 0; i < fpArraySize; i++)
    {
        fp[i] = fopen("file.txt", "w");
        if (fp[i] == NULL)
        {
            LE_INFO("error: %s", strerror(errno));
        }
    }


    // Create one more file/dir/pipe/socket, and verify that it's possible to do so
    // Then create one more file/dir/pipe/socket, and verify that it's not possible to do so

    //files
    FILE* fp_atlimit = fopen("file.txt", "w");
    FILE* fp_limitplusone = fopen("file.txt", "w");

    if (FdResLim <= num_std_fd)
    {
        if ((fp_atlimit == NULL) && (fp_limitplusone == NULL))
        {
            LE_INFO("No more available fd, and hence no more files can be opened.");
        }
        else
        {
            LE_FATAL("Error: Files can be opened, but there should be no more available fd.");
        }
    }
    else {
        if ((fp_atlimit != NULL) && (fp_limitplusone == NULL))
        {
            LE_INFO("Files can be opened right at the fd limit, but no more.");
        }
        else {
            if (fp_atlimit == NULL)
            {
                LE_INFO("fp_atlimit is NULL");
            }
            else {
                LE_INFO("fp_atlimit is not NULL");
            }

            if (fp_limitplusone == NULL)
            {
                LE_INFO("fp_limitplusone is NULL");
            }
            else {
                LE_INFO("fp_limitplusone is not NULL");
            }

            LE_FATAL("Error: More or less files than 1 are opened, but there should be only 1 available fd.");
        }
    }

    // clean up
    if ((fp_atlimit != NULL) && (fclose(fp_atlimit) != 0))
    {
        LE_INFO("fp_atlimit is not closed successfully. Error:%s", strerror(errno));
    }
    if ((fp_limitplusone != NULL) && (fclose(fp_limitplusone) != 0))
    {
        LE_INFO("fp_limitplusone is not closed successfully. Error:%s", strerror(errno));
    }


    // directories
    if (le_dir_Make("dummydir", 0777) == LE_OK)
    {

        DIR* dir_atlimit = opendir("dummydir");
        DIR* dir_limitplusone = opendir("dummydir");

        if (FdResLim <= num_std_fd)
        {
            if ((dir_atlimit == NULL) && (dir_limitplusone == NULL))
            {
                LE_INFO("No more available fd, and hence no more directories can be opened.");
            }
            else
            {
                LE_FATAL("Error: Directories can be opened, but there should be no more available fd.");
            }
        }
        else
        {
            if ((dir_atlimit != NULL) && (dir_limitplusone == NULL))
            {
                LE_INFO("Directories can be opened right at the fd limit, but no more.");
            }
            else
            {
                LE_FATAL("Error: More or less directories than 1 are opened, but there should be only 1 available fd.");
            }
        }

        // clean up
        if ((dir_atlimit != NULL) && (closedir(dir_atlimit) != 0))
        {
            LE_INFO("dir_atlimit is not closed successfully. Error:%s", strerror(errno));
        }
        if ((dir_limitplusone != NULL) && (closedir(dir_limitplusone) != 0))
        {
            LE_INFO("dir_limitplusone is not closed successfully. Error:%s", strerror(errno));
        }

    }
    else {
        LE_INFO("Error: cannot create directory. Test skipped.");
    }


    // pipes
    if (mkfifo("named_pipe", 0777) == 0)
    {

        int fd_pipe_atlimit = open("named_pipe", O_RDONLY | O_NONBLOCK);
        int fd_pipe_limitplusone = open("named_pipe", O_RDONLY | O_NONBLOCK);

        if (FdResLim <= num_std_fd)
        {
            if ((fd_pipe_atlimit == -1) && (fd_pipe_limitplusone == -1))
            {
                LE_INFO("No more available fd, and hence no more pipes can be opened.");
            }
            else
            {
                LE_FATAL("Error: pipes can be opened, but there should be no more available fd.");
            }
        }
        else
        {
            if ((fd_pipe_atlimit != -1) && (fd_pipe_limitplusone == -1))
            {
                LE_INFO("Pipes can be opened right at the fd limit, but no more.");
            }
            else
            {
                LE_FATAL("Error: More or less pipes than 1 are opened, but there should be only 1 available fd.");
            }
        }

        // clean up
        if ((fd_pipe_atlimit != -1) && (close(fd_pipe_atlimit) != 0))
        {
            LE_INFO("fd_pipe_atlimit is not closed successfully. Error:%s", strerror(errno));
        }
        if ((fd_pipe_limitplusone != -1) && (close(fd_pipe_limitplusone) != 0))
        {
            LE_INFO("fd_pipe_limitplusone is not closed successfully. Error:%s", strerror(errno));
        }

    }
    else {
        LE_INFO("Error: cannot create named pipe. Test skipped.");
    }


    // socket
    int fd_socket_atlimit = socket(PF_LOCAL, SOCK_STREAM, 0);
    int fd_socket_limitplusone = socket(PF_LOCAL, SOCK_STREAM, 0);

    if (FdResLim <= num_std_fd)
    {
        if ((fd_socket_atlimit == -1) && (fd_socket_limitplusone == -1))
        {
            LE_INFO("No more available fd, and hence no more sockets can be opened.");
        }
        else
        {
            LE_FATAL("Error: Sockets can be opened, but there should be no more available fd.");
        }
    }
    else {
        if ((fd_socket_atlimit != -1) && (fd_socket_limitplusone == -1))
        {
            LE_INFO("Sockets can be opened right at the fd limit, but no more.");
        }
        else {
            LE_FATAL("Error: More or less Sockets than 1 are opened, but there should be only 1 available fd.");
        }
    }

    // clean up
    if ((fd_socket_atlimit != -1) && (close(fd_socket_atlimit) != 0))
    {
        LE_INFO("fd_socket_atlimit is not closed successfully. Error: %s", strerror(errno));
    }
    if ((fd_socket_limitplusone != -1) && (close(fd_socket_limitplusone) != 0))
    {
        LE_INFO("fd_socket_limitplusone is not closed successfully. Error: %s", strerror(errno));
    }


    // final clean up
    for (i = 0; i < fpArraySize; i++)
    {
        if (fp[i] == NULL)
        {
            LE_FATAL("fp is NULL but it's not expected to be. Something could be potentially wrong.");
        }
        else
        {
            if (fclose(fp[i]) != 0)
            {
                LE_FATAL("fp is not closed successfully.");
            }
        }
    }



    LE_INFO("File descriptor limit test PASSED.");


    fflush(stdout);
    exit(EXIT_SUCCESS);
}
