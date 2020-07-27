/**
 * @file override.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
#include "legato.h"
#include "interfaces.h"
#include "overrideLibC.h"

COMPONENT_INIT
{
    defaultFunction();
    hiddenFunction();
}
