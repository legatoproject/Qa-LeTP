#include "legato.h"
#include "interfaces.h"

void foo_f()
{
    LE_INFO("foo_f is called");
}

void bar_f()
{
    LE_INFO("bar_f is called");
}

COMPONENT_INIT
{
    LE_INFO("Server started");
}
