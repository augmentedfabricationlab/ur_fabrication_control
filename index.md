# Getting started

### Dependencies

* Windows 10
* Rhino 6 / Grasshopper
* [Anaconda Python](https://www.anaconda.com/distribution/?gclid=CjwKCAjwo9rtBRAdEiwA_WXcFoyH8v3m-gVC55J6YzR0HpgB8R-PwM-FClIIR1bIPYZXsBtbPRfJ8xoC6HsQAvD_BwE)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Github Desktop](https://desktop.github.com/)

### 1. Setting up the Anaconda environment with COMPAS and COMPAS_fab

Add conda-forge to the list of channels where conda looks for packages.

	conda config --add channels conda-forge

Execute the commands below in Anaconda Prompt (run as Administrator):

    conda create -n afab19 python=3.6 COMPAS=0.8.1 --yes
    
Alternatively: If you run into problems with the PIL library, run instead:

	create -n afab19 python=3.6 COMPAS=0.8.1 matplotlib=3.0 --yes

Then continue with activating the environment:

    conda activate afab19
    
And install COMPAS_fab with:

    conda install -c conda-forge compas_fab
    
For more info about COMPAS follow this [link](https://compas-dev.github.io/).

For more info about COMPAS_fab follow this [link](https://gramaziokohler.github.io/compas_fab/latest/).

### 2. Setting up jupyter and extensions

Install jupyter for the afab19 environment:

    conda install -c anaconda jupyter 

To run the jupyter notebook, you simply have to type:

    jupyter notebook

in your command line.

#### Configure jupyter workspace

To configure the workspace, type

    jupyter notebook --generate-config

This writes a default configuration file into:

`%HOMEPATH%\.jupyter\jupyter_notebook_config.py` (on windows)

or

`~/.jupyter/jupyter_notebook_config.py` (on mac)

If you want jupyter to open in a different directory, then change the following line:

    c.NotebookApp.notebook_dir = 'YOUR_PREFERRED_PATH'

### Download nbextensions

To install nbextensions, execute the commands below in Anaconda Prompt (run as Administrator) in the afab19 environment:

    conda install -c conda-forge jupyter_contrib_nbextensions
    conda install -c conda-forge rise

After installing, restart the Jupyter notebook, and you can observe a new tab Nbextensions added to the menu, last entry under "Edit".
Install the following extensions:

1. Split Cells Notebook - Enable split cells in Jupyter notebooks

2. [RISE](https://rise.readthedocs.io/en/stable/installation.html#) - allows you to instantly turn your Jupyter Notebooks into a slideshow

### 3. Additional Python Dependencies

Three JS

    conda install -c conda-forge pythreejs
    
Optionally: Updating to another version of COMPAS, e.g.:

     conda install compas=0.10.0
	
    

### 4. Setting up the Rhino/Grasshopper Environment

see also this [link](https://compas-dev.github.io/main/gettingstarted/cad/rhino.html)

Installing COMPAS for Rhino is very simple. Just type the following on Anaconda prompt:
    
    python -m compas_rhino.install
    python -m compas_rhino.install -p compas_fab





