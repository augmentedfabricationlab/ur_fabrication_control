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

Execute the commands below in Anaconda Prompt (in case of issues, run as Administrator):

    conda create -n urfab python=3.7 compas=0.15 compas_fab=0.11 --yes
    conda activate urfab

Additional depenencies:

    conda install -c conda-forge pythreejs

### 2. Setting up the Rhino/Grasshopper Environment

Run the following commands on Anaconda prompt:
    
    python -m compas_rhino.install
    python -m compas_fab.rhino.install

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
    import compas_fab
    compas .__version__
    compas_fab .__version__
    







