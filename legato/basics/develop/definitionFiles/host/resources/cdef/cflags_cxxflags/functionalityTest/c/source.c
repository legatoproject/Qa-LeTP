/**
 * @file source.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"

COMPONENT_INIT
{
    #ifdef CTESTFLAG
    LE_INFO("cflag: CTESTFLAG response");
    #endif
}
