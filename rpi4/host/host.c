#include <err.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include <unistd.h>
/* OP-TEE TEE client API (built by optee_client) */
#include <tee_client_api.h>
/* For the UUID (found in the TA's h-file(s)) */
#include "../ta/temp_ch_ta.h"

#define VERBOSE 0
#define FREQUENCY 1500000
#define HAMMING_BLOCK_SIZE 16

//       ________________________
//_____/ Hamming encode and utils

/**
 * Checks if a given number is a power of 2.
 * 
 * @param x The integer to check.
 * @return 1 if x is a power of 2, 0 otherwise.
 * 
 */
int is_power_2(int x){
    // A number is a power of 2 if it has only one bit set in its binary representation.
    // So, if we AND the number with its bitwise complement (number - 1), we should get 0 for powers of 2.
    return (x && !(x & (x - 1)));
}

/**
 * Checks if a specific bit is set in a given number.
 * 
 * @param num The integer to check.
 * @param pos The position of the bit to check (0-indexed).
 * @return 1 if the bit at position pos is set, 0 otherwise.
 * 
 */
int is_bit_set(int num, int pos){
    // Left shift 1 to the position and bitwise AND with num
    // If the result is non-zero, the bit is set; otherwise, it's not set
    return (num & (1 << pos)) != 0;
}

/**
 * Hamming encodes a bit string.
 * 
 * @param bits The input bit string to encode.
 * @param block_size The size of each block including parity bits.
 * @return The Hamming encoded bit string, or NULL if memory allocation fails.
 */
char* hamming_encode(char* bits, int block_size) {
    int len = strlen(bits);
    int parity_bits = log2(block_size);
    int blocks = (int)ceil((double)len / (block_size - (parity_bits + 1)));
    int final_length = blocks * block_size;
    
#if VERBOSE
    int unused = final_length - (len + (parity_bits + 1) * blocks);
    printf("Length:        %d\n", len);
    printf("Parity bits:   %d\n", parity_bits);
    printf("Data bits:     %d\n", block_size - (parity_bits + 1));
    printf("Blocks:        %d\n", blocks);
    printf("Final length:  %d\n", final_length);
    printf("Unused space:  %d\n", unused);
    printf("Unused percent: %.6f\n", (float)unused / len);
    if ((float)unused / len > 0.5) {
        printf("WARNING! Inefficient encoding, try a different block size.\n");
    }
#endif

    // Allocate memory for the encoded data
    char* hamming_data = (char*)malloc(final_length * sizeof(char));
    if (hamming_data == NULL) {
        printf("Memory allocation failed!\n");
        return NULL;
    }

    int data_i = 0;
    for (int block = 0; block < blocks; block++) {
        int parities[parity_bits + 1];
        memset(parities, 0, sizeof(parities));
        // Copy data, count parities, ignore power of 2 (parity) positions
        for (int i = 3; i < block_size; i++) {
            if (is_power_2(i)) {
                // Skip parity positions
            } else if (data_i < len) {
                char data = bits[data_i++];
                hamming_data[block * block_size + i] = data;
                if (data == '1') {
                    parities[0]++;
                    for (int j = 0; j < parity_bits; j++) {
                        if (is_bit_set(i, j)) {
                            parities[j + 1]++;
                        }
                    }
                }
            } else {
                hamming_data[block * block_size + i] = '0';
            }
        }
        // Set parity bits
        for (int i = 0; i < parity_bits; i++) {
            int parity_index = (int)pow(2, i);
            hamming_data[block * block_size + parity_index] = (parities[i + 1] % 2 == 0) ? '0' : '1';
            if (hamming_data[block * block_size + parity_index] == '1') {
                parities[0]++;
            }
        }
        // Set extended parity
        hamming_data[block * block_size] = (parities[0] % 2 == 0) ? '0' : '1';
    }
    return hamming_data;
}

/**
 * Converts an ASCII string to a binary string representation.
 * 
 * @param s The input ASCII string.
 * @return The binary string representation of the input string. 
 *         The caller is responsible for freeing the allocated memory.
 *         Returns NULL if the input string is NULL.
 */

char* string_to_binary(char* s) {
    if(s == NULL) return 0; // no input string 
    size_t len = strlen(s);
    char *binary = malloc(len*8 + 1); // each char is one byte (8 bits) and + 1 at the end for null terminator
    binary[0] = '\0';
    for(size_t i = 0; i < len; ++i) {
        char ch = s[i];
        for(int j = 7; j >= 0; --j){
            if(ch & (1 << j)) {
                strcat(binary,"1");
            } else {
                strcat(binary,"0");
            }
        }
    }
    return binary;
}

/**
 * Sets the CPU frequency.
 *
 * @param freq_khz The desired CPU frequency in kilohertz.
 */
void set_cpu_frequency(unsigned int freq_khz) {
    FILE *setspeed_fp;

    // Open the freq file for writting (specific to Linux systems)
    setspeed_fp = fopen("/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed", "w");

    if (setspeed_fp == NULL) {
        perror("Error opening files");
        exit(1);
    }

    // Set the frequency
    fprintf(setspeed_fp, "%u", freq_khz);
    fclose(setspeed_fp);
}

int main(int argc, char *argv[]){

	//     __________________________
	//____/ Arguements setup

	// Check sleep and hamming params
	if(argc != 3) {
        printf("Usage: %s <integer> <0/1>\n", argv[0]);
        return 1;
    }
  	int sleep_milis = atoi(argv[1]);
	int bool_value = atoi(argv[2]); 
    int hamming;
    if (bool_value == 1) {
        hamming = 1;
    } else if (bool_value == 0) {
        hamming = 0;
    } else {
        printf("The second argument must be 0 or 1.\n");
        return 1;
    }

	// Set RPI4 freq to max
	set_cpu_frequency(FREQUENCY);
#if VERBOSE 
	printf("CPU freq set to %d\n",FREQUENCY);
#endif

	//     __________________________
	//____/ TEE initialization

	/* TEE variables */
	TEEC_Result res;
	TEEC_Context ctx;
	TEEC_Session sess;
	TEEC_Operation op;
	TEEC_UUID uuid = TEMP_CH_TA_UUID;
	uint32_t err_origin;

	// Initialize a context connecting us to the TEE
	res = TEEC_InitializeContext(NULL, &ctx);
	if (res != TEEC_SUCCESS){
		errx(1, "TEEC_InitializeContext failed with code 0x%x", res);
	}

	// Open a session in the TA
	res = TEEC_OpenSession(&ctx, &sess, &uuid, TEEC_LOGIN_PUBLIC, NULL, NULL, &err_origin);
	if (res != TEEC_SUCCESS){
		errx(1, "TEEC_Opensession failed with code 0x%x origin 0x%x", res, err_origin);
	}

	//     ___________________________________
	//____/ TA operation params initialization

	// Clear the TEEC_Operation struct
	memset(&op, 0, sizeof(op));

	/*
	 * Prepare the argument. Pass the sleep value (milis) in the first parameter
	 * and the second with a shared memory pointer to 64 bytes 
	 */
	op.paramTypes = TEEC_PARAM_TYPES(TEEC_VALUE_INPUT, 
									 TEEC_MEMREF_TEMP_INOUT,
									 TEEC_NONE,
									 TEEC_NONE);

	op.params[0].value.a = sleep_milis;

	// Create a shared memory block of 64 bytes
	TEEC_SharedMemory shared_mem;
	shared_mem.size = 4100;
	shared_mem.flags = TEEC_MEM_INPUT;
	
	res = TEEC_AllocateSharedMemory(&ctx,&shared_mem);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_AllocateSharedMemory failed with code 0x%x", res);

	if (shared_mem.buffer != NULL) {

		//char* msg = string_to_binary("hola");
        char* msg = "11111111111111111111111111111111\
                     11111111111111111111111111111111\
                     11111111111111110000000000001111\
                     11111111111111110000000000001111\
                     11111111111111100000000000000111\
                     11111111111111100011000000000111\
                     11111111111111100011000000000111\
                     11111111111111100000000000000111\
                     11111111111111100000000000000111\
                     11111111111111100000000000000111\
                     11111111111111100000001111111111\
                     11111111111111100000000000111111\
                     11001111111110000000000000111111\
                     11001111111100000000011111111111\
                     11001111111100000000011111111111\
                     11000011100000000000000011111111\
                     11000001000000000000000011111111\
                     11000001000000000000010011111111\
                     11000000000000000000011111111111\
                     11000000000000000000011111111111\
                     11000000000000000000011111111111\
                     11110000000000000000111111111111\
                     11111000000000000000111111111111\
                     11111000000000000000111111111111\
                     11111100000000000011111111111111\
                     11111111000010000111111111111111\
                     11111111000010000111111111111111\
                     11111111000111100111111111111111\
                     11111111001111100111111111111111\
                     11111111000111100011111111111111\
                     11111111000111100011111111111111\
                     11111111111111111111111111111111";

		if(hamming){
			msg = hamming_encode(msg, HAMMING_BLOCK_SIZE);
		}

    	strcpy(shared_mem.buffer, msg);

	} 
	else {
		errx(1, "Shared memory allocation failed");
	}

	op.params[1].memref.parent = shared_mem.buffer;
	op.params[1].memref.size   = 4100;
	op.params[1].memref.offset = 0;

	//     _______________________
	//____/ TA execution calls

	// Call the send_with_temp function on the TA
	res = TEEC_InvokeCommand(&sess, CMD_SEND_WITH_TEMP, &op, &err_origin);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_InvokeCommand failed with code 0x%x origin 0x%x", res, err_origin);

	//     ___________________
	//____/ TA finalization

	/*
	 * We're done with the TA, close the session and destroy the context. 
	 * The TA will print "Goodbye!" in the log when the session is closed.
	 */

	// Always free memory
    TEEC_ReleaseSharedMemory(&shared_mem);

	TEEC_CloseSession(&sess);

	TEEC_FinalizeContext(&ctx);

	return 0;
}