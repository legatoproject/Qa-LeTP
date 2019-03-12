#include "legato.h"

COMPONENT_INIT
{
    #ifdef CPPTESTFLAG
    LE_INFO("cppflag: CPPTESTFLAG response");
    #endif
}
