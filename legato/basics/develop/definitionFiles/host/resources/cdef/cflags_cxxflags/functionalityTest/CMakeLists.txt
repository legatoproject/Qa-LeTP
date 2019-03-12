#*******************************************************************************
# Copyright (C) Sierra Wireless Inc. Use of this work is subject to license.
#
# Contributors:
#     Sierra Wireless - initial API and implementation
#*******************************************************************************

# Creates application from cflags_cxxflags.adef
mkapp(cflags_cxxflags.adef
    DEPENDS
        legato
        c
        cplusplus/*
        *
)
