/**
 * @file helloWorld.c
 *
 * Copyright (C) Sierra Wireless Inc.
 *
 */
/**
  This app/process is used for le_updateCtrl_Defer() and le_updateCtrl_Allow() test cases
  by installing this app as an update to the system. It is configured to be runned manually
  on the target device
**/

#include "legato.h"

COMPONENT_INIT
{
    LE_INFO("Hello World.\n");
}
