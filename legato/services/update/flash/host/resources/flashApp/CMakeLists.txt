#*******************************************************************************
# Copyright (C) Sierra Wireless Inc.
#*******************************************************************************

# This test application can only run on dual system modules.
# Therefore, it can be currently run only on ar758x and ar759x targets.
if((LEGATO_TARGET MATCHES "ar758x") OR (LEGATO_TARGET MATCHES "ar759x"))
    mkapp(      flashApp.adef
                -i ${LEGATO_ROOT}/interfaces/flash
    )
endif()

