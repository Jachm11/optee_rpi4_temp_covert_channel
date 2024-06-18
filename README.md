# optee_rpi4_temp_covert_channel

An experiment using the CPU temperature of a Raspberry Pi 4 as a covert channel on OP-TEE.

To use, connect your RPi4 via Ethernet, check the IP, and adjust the necessary files `port` and `analysis_tool/shell_scripts/run_on_rpi` accordingly. You will also need to build the host and TA applications. Adjust the paths for your OP-TEE directories and cross-compiler in `rpi4/Makefile`(Refer to this [RPI4 optee port](https://github.com/Jachm11/optee-os_raspberry_pi_4_port) if unclear). Then, run `make` inside the rpi4 directory.

Once this is done, you can run `./port` to copy all the necessary files to the RPi4. You can edit port to specify the directory where the files should be placed on your RPi. 

Finally, execute `analysis_tool/analysis_tool.py` and follow the instructions. (To send the dino image, the code block in `host.c` must be uncommented).
