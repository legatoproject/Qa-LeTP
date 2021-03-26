.. _introduction:

############
Introduction
############

Qa-letp contains `Legato <https://github.com/legatoproject/legato-af>`_
system testing scripts.

Steps to installing LeTP and running the full system test campaign
------------------------------------------------------------------

1. Clone the LeTP repo if you haven't already done so::

    git clone https://github.com/legatoproject/LeTP.git

2. Go into the testing_target/ directory from LeTP root::

    cd LeTP/testing_target

3. Clone the Qa-LeTP repo::

    git clone https://github.com/legatoproject/Qa-LeTP.git

4. Setup LeTP as you normally would::

    cd ../
    source configLeTP.sh testing_target

   The following command should return the path of letp.::

           which letp

   Make sure the environment variable $LEGATO_ROOT is set before moving on.
   This is required for running some tests.
   If you're unsure how to set it, please refer to "Getting Started" section in LeTP documentation.

5. Navigate to the test directory::

    cd testing_target/Qa-LeTP/runtest

6. Run the full system test campaign::

    letp run full_campaign.json --config 'module/ssh(used)=1' --config 'module/slink1(used)=1' --config 'module/slink1/name=<DEVICE_CLI_PORT>' --config 'module/slink2(used)=1' --config 'module/slink2/name=<DEVICE_AT_PORT>'

Documentations for tests
------------------------

To generate the documentation for tests provided:

1. Navigate to the documentation directory in Qa-LeTP.::

    cd LeTP/testing_target/Qa-LeTP/doc

2. Generate HTML documentation::

    make html

Generated documentations can be found in doc/_sphinx/html/index.html
