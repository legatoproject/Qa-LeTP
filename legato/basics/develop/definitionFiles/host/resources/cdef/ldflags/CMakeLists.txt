#*******************************************************************************
# Copyright (C) Sierra Wireless Inc. Use of this work is subject to license.
#
# Contributors:
#     Sierra Wireless - initial API and implementation
#*******************************************************************************

# Creates application from ldflags.adef
mkapp(ldflags.adef  -ItestLib
    DEPENDS
        legato
        ldflagsComponent/*
        *
)
