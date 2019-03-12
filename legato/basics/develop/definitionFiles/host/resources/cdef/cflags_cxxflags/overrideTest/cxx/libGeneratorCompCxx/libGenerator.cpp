#include "legato.h"
#include "interfaces.h"

void defaultFunction (void)
{
    LE_INFO("Default function");
}

void __attribute__((visibility("hidden"))) hiddenFunction (void)
{
    LE_INFO("Hidden function");
}

COMPONENT_INIT
{
}
