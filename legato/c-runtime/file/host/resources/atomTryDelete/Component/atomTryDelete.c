#include "legato.h"
#include "interfaces.h"

bool accessOK = false;

void TryDeleteReturnsOK(const char *filePath)
{
    le_result_t result = le_atomFile_TryDelete(filePath);

    if (result == LE_OK)
    {
        LE_INFO("[PASSED] le_atomFile_TryDelete returns LE_OK if successful");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_NOT_FOUND if successful");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_FAULT if successful");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_WOULD_BLOCK if successful");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns '%d' if successful", result);
    }
}

void TryDeleteReturnsNotFound(const char *filePath)
{
    le_result_t result = le_atomFile_TryDelete(filePath);

    if (result == LE_NOT_FOUND)
    {
        LE_INFO("[PASSED] le_atomFile_TryDelete returns LE_NOT_FOUND if file doesn't exists");
    }
    else if (result == LE_OK)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_OK if file doesn't exists");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_FAULT if file doesn't exists");
    }
    else if (result == LE_WOULD_BLOCK)
    {
         LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_WOULD_BLOCK if file doesn't exists");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns '%d' if file doesn't exists", result);
    }
}

void TryDeleteReturnsFault(const char *filePath)
{
    le_result_t result = le_atomFile_TryDelete(filePath);

    if (result == LE_FAULT)
    {
        LE_INFO("[PASSED] le_atomFile_TryDelete returns LE_FAULT if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_NOT_FOUND if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_OK)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_OK if there was an error (accesses to a non-existed dir)");
    }
    else if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_WOULD_BLOCK if there was an error (accesses to a non-existed dir)");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns '%d' if there was an error (accesses to a non-existed dir)", result);
    }
}

void TryDeleteReturnsWouldBlock(const char *filePath)
{
    le_atomFile_Open(filePath, LE_FLOCK_WRITE);
    le_result_t result = le_atomFile_TryDelete(filePath);

    if (result == LE_WOULD_BLOCK)
    {
        LE_INFO("[PASSED] le_atomFile_TryDelete returns LE_WOULD_BLOCK if file is already locked");
    }
    else if (result == LE_NOT_FOUND)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_NOT_FOUND if file is already locked");
    }
    else if (result == LE_OK)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_OK if file is already locked");
    }
    else if (result == LE_FAULT)
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns LE_FAULT if file is already locked");
    }
    else
    {
        LE_INFO("[FAILED] le_atomFile_TryDelete returns '%d' if file is already locked", result);
    }
}

COMPONENT_INIT
{
    if (le_arg_NumArgs() != 2)
    {
        LE_INFO("***USAGE: app runProc atomTryDelete atomTryDeleteProc -- <file path> -- <test description>***");
        exit(EXIT_SUCCESS);
    }

    LE_INFO("====================BEGIN le_atomFile_TryDelete API======================");

    const char *testFilePath = le_arg_GetArg(0);
    const char *testDescription = le_arg_GetArg(1);

    if (strcmp(testDescription, "notFound") == 0)
    {
        TryDeleteReturnsNotFound(testFilePath);
    }
    else if (strcmp(testDescription, "fault") == 0)
    {
        TryDeleteReturnsFault(testFilePath);
    }
    else if (strcmp(testDescription, "ok") == 0)
    {
        TryDeleteReturnsOK(testFilePath);
    }
    else if (strcmp(testDescription, "wouldBlock") == 0)
    {
        TryDeleteReturnsWouldBlock(testFilePath);
    }
    else
    {
        LE_INFO("***Unknown test description***");
    }

    LE_INFO("====================END le_atomFile_TryDelete API===========================");

    exit(EXIT_SUCCESS);
}