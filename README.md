# optee_rpi4_temp_covert_channel
A experiment using the cpu temperature of a Raspberry Pi 4 as a covert channel on optee


To use connect your rpi4 via ethernet, check the IP and adjust accordingly on files `port` and `analysis_tool/shell_scripts/run_on_rpi`. 
You will also need to build the host and ta applications. Adjust the path of your optee directories and cross-compiler at `rpi4/Makefile`. Then run `make` inside the rpi4 directory.

Once this is done you can run `./port` to copy all the necesary files to the rpi4. You can edit `port` to put the files on a specific directory on your rpi. 

Finally simply execute `analysis_tool/analysis_tool.py` and follow the instructions. (To send the dino image the code block on `host.c` must be uncommented).
