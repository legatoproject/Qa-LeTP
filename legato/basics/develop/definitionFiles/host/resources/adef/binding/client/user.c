#include "legato.h"
#include "interfaces.h"

COMPONENT_INIT
{
    if (le_arg_NumArgs() == 1)
    {
        const char* user = le_arg_GetArg(0);
        service_Print(user);
    }
    else
    {
        service_Print("User not specified");
    }
}
