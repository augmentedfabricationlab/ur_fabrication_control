# Getting started

### Dependencies

* Windows 10
* Rhino 6 / Grasshopper
* [Anaconda Python](https://www.anaconda.com/distribution/?gclid=CjwKCAjwo9rtBRAdEiwA_WXcFoyH8v3m-gVC55J6YzR0HpgB8R-PwM-FClIIR1bIPYZXsBtbPRfJ8xoC6HsQAvD_BwE)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Github Desktop](https://desktop.github.com/)

For more info about COMPAS follow this [link](https://compas-dev.github.io/).

For more info about COMPAS_fab follow this [link](https://gramaziokohler.github.io/compas_fab/latest/).

### 1. Setting up the Anaconda environment with COMPAS and COMPAS_fab

Add conda-forge to the list of channels where conda looks for packages.

	conda config --add channels conda-forge

Execute the commands below in Anaconda Prompt (run as Administrator):

    conda create -n urfab python=3.6 COMPAS=0.10 --yes

Then continue with activating the environment:

    conda activate urfab
    
And install COMPAS_fab with:

    conda install -c conda-forge compas_fab=0.8

Additional depenencies:

    conda install -c conda-forge pythreejs


### 2. Setting up the Rhino/Grasshopper Environment

see also this [link](https://compas-dev.github.io/main/gettingstarted/cad/rhino.html)

Run the following commands on Anaconda prompt:
    
    python -m compas_rhino.install
    python -m compas_rhino.install -p compas_fab

If you run into problems with the PIL library, run:

	conda install matplotlib=3.0

and try installing again.


### 2. Setting up jupyter and extensions

Install jupyter for the urfab environment:

    conda install -c anaconda jupyter 

To install nbextensions, execute the commands below in Anaconda Prompt (run as Administrator) in the afab19 environment:

    conda install -c conda-forge jupyter_contrib_nbextensions
    conda install -c conda-forge rise

To run the jupyter notebook, you simply have to type:

    jupyter notebook

in your command line.

Then enable the extension rise and split-cells via the new tab Nbextensions added to the menu (last entry under "Edit").


### 3. Testing your set-up:

open Anaconda prompt and type one after the other:
    
    python
    import compas
    compas .__version__
    compas_fab .__version__
    







