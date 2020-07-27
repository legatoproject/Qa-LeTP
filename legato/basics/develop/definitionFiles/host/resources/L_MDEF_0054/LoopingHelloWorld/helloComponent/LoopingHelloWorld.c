/**
 * @file LoopingHelloWorld.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"

COMPONENT_INIT
{
    int i = 0;
    for (i=0; i<100; i++)
    {
        LE_INFO("Hello, world.");
        sleep(5);
    }
}
