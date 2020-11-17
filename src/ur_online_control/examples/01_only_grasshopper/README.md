# Start server

If starting the server from grasshopper does not work:

Open command promt and go to your folder

	cd C:\Users\rustr\workspace\projects\ur_online_control\examples\01_only_grasshopper

Activate your python 2.7 conda environment
	
	activate py27

Start the server.

	python main_add2floats.py


Connect to server from Grasshopper.

Change sliders and press "send".

You should see the result immediately at the receive component.

If you want to stop, change "continue_fabrication" to False and send again.
