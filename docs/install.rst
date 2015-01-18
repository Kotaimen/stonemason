Installation
============


Development Environment
-----------------------


ubuntu-14.04-LTS
~~~~~~~~~~~~~~~~

Install binary package dependency:

.. code-block:: console

    sudo apt-get install python python-dev python-pip
    sudo apt-get install python3 python3-dev python3-pip
    sudo apt-get install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev
    sudo apt-get install memcached libmemcached-dev
    
    
Install python dependency:
    
.. code-block:: console

    sudo pip install -rrequirements-dev.txt
    sudo pip install -rrequirements.txt
    sudo pip3 install -rrequirements-dev.txt
    sudo pip3 install -rrequirements.txt


Homebrew
~~~~~~~~


Install binary package dependency:

.. code-block:: console

    brew install python python3
    brew install libjpeg libz libtiff freetype libwebp lcms2
    brew install memcached libmemcached


Install python dependency:

.. code-block:: console

    pip install -rrequirements-dev.txt
    pip install -rrequirements.txt
    pip3 install -rrequirements-dev.txt
    pip3 install -rrequirements.txt


Test
----

Clone the code:

.. code-block:: console

    git clone https://github.com/Kotaimen/stonemason.git

Run nosetests:

.. code-block:: console

    cd stonemason
    python setup.py build_ext --inplace
    nosetests

Run tox:

.. code-block:: console

    tox

