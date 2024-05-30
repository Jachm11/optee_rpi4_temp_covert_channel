# Paths
OPTEEOS_DIR = /home/jachm/Documents/OPTEE-RPI4/optee_os
OPTEECLIENT_DIR = /home/jachm/Documents/OPTEE-RPI4/buildroot/output/build/optee-client-4.0.0
CC = /home/jachm/Documents/OPTEE-RPI4/toolchains/aarch64/bin/aarch64-none-linux-gnu-

# Set output directory
BUILD_DIR = build/rpi4

# Set target names
HOST_TARGET = $(BUILD_DIR)/host
LOGGER_TARGET = $(BUILD_DIR)/logger
TA_TARGET   = $(BUILD_DIR)/ta

# Compiler flags
CXXFLAGS = -I$(OPTEECLIENT_DIR)/libteec/include
LDFLAGS  = -L$(OPTEECLIENT_DIR)/libteec -lteec -lm

# TA log level
CFG_TEE_TA_LOG_LEVEL ?= 4

# The UUID for the Trusted Application
BINARY=8aaaf200-2450-11e4-abe2-0002a5d5c51e


# Targets
.PHONY: all port clean

all: $(HOST_TARGET) $(TA_TARGET) $(LOGGER_TARGET)

$(HOST_TARGET): host/host.c | $(BUILD_DIR)
	$(CC)gcc $^ $(CXXFLAGS) $(LDFLAGS) -o $@

$(LOGGER_TARGET): host/temp_logger.c | $(BUILD_DIR)
	$(CC)gcc $^ $(CXXFLAGS) $(LDFLAGS) -o $@

$(TA_TARGET): export CROSS_COMPILE64=$(CC)
$(TA_TARGET): export TA_DEV_KIT_DIR=$(OPTEEOS_DIR)/out/arm-plat-rpi4/export-ta_arm64
$(TA_TARGET): export O=../build/rpi4/ta
$(TA_TARGET): ta/temp_ch_ta.c | $(BUILD_DIR)
	$(MAKE) -C ta/

$(BUILD_DIR):
	mkdir -p $@

clean:
	rm -rf build