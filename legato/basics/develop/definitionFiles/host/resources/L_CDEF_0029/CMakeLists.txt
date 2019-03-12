#*******************************************************************************
# Copyright (C) Sierra Wireless Inc.
#*******************************************************************************

# Creates application from helloWorld.adef
mkapp(      simApp.adef
            -i ${LEGATO_ROOT}/interfaces/modemServices
            -i helloComponent
)
