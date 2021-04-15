![Legato](https://legato.io/resources/img/legato_logo.png)

Qa-letp contains <A HREF="https://github.com/legatoproject/legato-af">
Legato</A> system testing scripts.

# Steps to installing LeTP and running the full system test campaign

1. Clone <A HREF="https://github.com/legatoproject/LeTP">LeTP</A> repo if you haven't already done so. <br>
    ```
    git clone https://github.com/legatoproject/LeTP.git
    ```
2. Go into the testing_target/ directory from LeTP root
    ```
    cd LeTP/testing_target
    ```
3. Clone the Qa-LeTP repo
    ```
    git clone https://github.com/legatoproject/Qa-LeTP.git
    ```
4. Setup LeTP as you normally would
    ```
    cd ../
    source configLeTP.sh testing_target
    ```
    The following command should return the path of letp.
    ```
    which letp
    ```
    Make sure the environment variable $LEGATO_ROOT is set before moving on.
    This is required for running some tests.
    If you're unsure how to set it, please refer to "Getting Started" section in LeTP documentation.
5. Navigate to the test directory
    ```
    cd testing_target/Qa-LeTP/runtest
    ```
6. Run the full system test campaign.
    ```
    letp run full_campaign.json --config 'module/ssh(used)=1' --config 'module/slink1(used)=1' --config 'module/slink1/name=<DEVICE_CLI_PORT>' --config 'module/slink2(used)=1' --config 'module/slink2/name=<DEVICE_AT_PORT>'
    ```

# Documentations for tests

To generate the documentation for tests provided:

1. Navigate to the documentation directory in Qa-LeTP.
    ```
    cd LeTP/testing_target/Qa-LeTP/doc
    ```
2. Generate HTML documentation
    ```
    make html
    ```
Generated documentations can be found in doc/_sphinx/html/index.html

# File structure for Qa-LeTP

Below is the file tree for Qa-LeTP:

```
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
    |   |               |   ├── resources
    |   |               |   ├── test_KMod_basic.py
    |   |               |   └── test_KMod.py
    |   |               └── runtest
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
```
