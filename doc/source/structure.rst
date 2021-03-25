##########################
File structure for Qa-LeTP
##########################

This is the file structure of Qa-LeTP for easy navigation.
Tests are divided into categories based on their functionality and purpose.
Further details on each test can be found in the documentations of each test.

Below is the file tree for Qa-LeTP::

    ├── config
    │
    ├── doc     // Documentation resources
    │   ├── Makefile    // Makefile for documentation generation
    |   ├── source      // Source files for documentation generation
    │   ├── _sphinx     // Generated after "make html". Contains the documentation.
    │
    ├── legato
    │   ├── basics
    │   │   ├── develop
    │   │   │   ├── definitionFiles     // Set of tests for the Legato component and application definition files.
    │   │   │       ├── host
    |   |   |       |   ├── resources
    |   |   |       |   ├── test_adef_link.py
    |   |   |       |   ├── test_adef_version.py
    |   |   |       |   ├── test_cdef_bundles.py
    |   |   |       |   ├── ...
    │   │   │       └── runtest
    │   │   ├── sampleApps      // Set of test for the Legato sample apps.
    │   │   │   ├── host
    │   │   │   │   ├── conftest.py     // Fixtures for sampleApps.
    │   │   │   │   ├── resources
    │   │   │   │   ├── test_sampleApps_dataHub.py      // Set of functions to test the Legato DataHub sample app.
    │   │   │   │   ├── test_sampleApps_helloIpc.py     // Set of functions to test the HelloIpc sample app.
    │   │   │   │   ├── test_sampleApps_helloWorld.py   // Set of functions to test the helloWorld sample app.
    │   │   │   │   └── ...
    │   │   │   └── runtest
    │   │   └── tools
    │   │       └── targetTools
    │   │           └── kmod        // Set of tests for the Legato kmod tools
    |   |               ├── host
    |   |               ├── resources
    |   |               ├── test_KMod_basic.py
    |   |               └── test_KMod.py
    │   ├── c-runtime       // Set of tests for file operations in C files.
    │   │   └── file
    │   │       ├── host
    │   │       │   ├── conftest.py             // Fixture to test atomic files.
    │   │       │   ├── resources
    │   │       │   ├── test_cancel.py          // Set of functions to test the le_atomFile_Cancel
    │   │       │   ├── test_cancelStream.py    // Set of functions to test the le_atomFile_CancelStream
    │   │       │   ├── test_close.py           // Set of functions to test the le_atomFile_Close
    │   │       │   ├── ...
    │   │       │   └── tools
    │   │       └── runtest
    │   ├── security
    │   │   └── sandbox
    │   │       ├── host
    │   │       │   ├── resources
    │   │       │   ├── test_basic.py           // Set of functions to test the sandboxbasic app.
    │   │       │   └── test_limitation.py      // Set of functions to test the sandbox app limitation.
    │   │       └── runtest
    │   └── services
    │       ├── secureStorage       // Secured storage test.
    │       │   ├── host
    │       │   │   ├── resources
    │       │   │   └── test_secureStorage.py       // Set of functions to test the secured storage.
    │       │   └── runtest
    │       └── update
    │           ├── flash       // The flash APIs test.
    │           │   ├── host
    |           |   |   ├── resources
    |           |   |   └── test_flash.py       // Set of functions to test flash APIs.
    │           │   └── runtest
    │           └── updateControl       // The update control API test.
    │               ├── host
    |               |   ├── conftest.py
    |               |   ├── __init__.py
    |               |   ├── resources
    |               |   ├── test_updateControl_Allow.py             // Set of functions to test the le_updateCtrl_Allow
    |               |   ├── test_updateControl_Defer.py             // Set of functions to test the le_updateCtrl_Defer
    |               |   ├── test_updateControl_FailProbation.py     // Set of functions to test the le_updateCtrl_FailProbation
    |               |   ├── ...
    |               |   └── tools
    │               └── runtest
    ├── LICENSE.md
    ├── README.md
    └── runtest
        ├── full_campaign.json
        └── sanity_campaign.json

