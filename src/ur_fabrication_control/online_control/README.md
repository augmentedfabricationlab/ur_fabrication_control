# ur_online_control


Requires compas 0.3.2 + compas_fab 0.2.1.


Installation notes (01.07.2019):

create a new environment in Anaconda
1. open anaconda prompt in administrator mode
2. conda create -n myenv python=2.7.16 (replace myenv by name of your choice, e.g. ur_online_control)

install compas_fab 0.2.1

3. conda activate myenv (e.g. conda activate ur_online_control)
4. conda install -c conda-forge compas_fab=0.2.1

install compas_fab for rhino

5. python -m compas_fab.rhino.uninstall 6.0
6. python -m compas_fab.rhino.install 6.0

clone current version of ur_online_control repository
set path in rhino to parent folder or ur_online_control repository
(e.g. if your folder is here: .../Desktop/stuff/ur_online_control, set a path in the rhino edit python script editor to: .../Desktop/stuff)

Ironpython: https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.9
