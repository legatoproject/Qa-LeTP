/**
 * @file ldflags.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"
#include "testLib.h"

COMPONENT_INIT
{
    LE_INFO("Library returned: %i", libPrinter());
}
