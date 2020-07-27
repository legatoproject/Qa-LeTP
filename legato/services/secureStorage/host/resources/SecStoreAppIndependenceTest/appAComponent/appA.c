/**
 * @file appA.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/* Legato Framework */
#include "legato.h"

/* IPC APIs */
#include "interfaces.h"

COMPONENT_INIT
{
    LE_INFO("secure storage independence test, appA");

    if (le_arg_NumArgs() == 1)
    {
        const char *option = le_arg_GetArg(0);

        if (strcmp(option, "read") == 0)
        {
            char outBuffer[20];
            size_t outBufferSize =  sizeof(outBuffer);
            le_result_t result = le_secStore_Read("file1", (uint8_t*)outBuffer, &outBufferSize);
            LE_FATAL_IF(result != LE_OK, "read failed: [%s]", LE_RESULT_TXT(result));

            // after appB has finished writing a different secure storage content with appA's
            // secure storage item name, if appA reads the same content as it wrote, mark this
            // TC passed; failed otherwise.
            if (strcmp("string123", outBuffer) == 0)
            {
                LE_INFO("appA successfully read its own written content");
            }

            // clean up
            result = le_secStore_Delete("file1");
            LE_FATAL_IF(result != LE_OK, "delete failed: [%s]", LE_RESULT_TXT(result));
        }
        else if (strcmp(option, "write") == 0)
        {
            // writes different secure storage content with appB's secure storage item name
            le_result_t result = le_secStore_Write("file1", (uint8_t*)"string123", 10);
            LE_FATAL_IF(result != LE_OK, "write failed: [%s]", LE_RESULT_TXT(result));
        }
        else
        {
            LE_INFO("ERROR*** invalid argument");
            exit(EXIT_FAILURE);
        }
    }
    else
    {
        LE_ERROR("ERROR*** invalid number of arguments");
        exit(EXIT_FAILURE);
    }

    exit(EXIT_SUCCESS);
}