#include "legato.h"
#include "interfaces.h"

void service_Print
(
    const char* msg
)
{
    LE_INFO("Message received: %s", msg);
}

COMPONENT_INIT
{
    LE_INFO("Service started");
}
