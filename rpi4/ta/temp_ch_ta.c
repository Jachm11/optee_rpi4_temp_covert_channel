#include <stdio.h>
#include <string.h>
#include <tee_internal_api.h>
#include <tee_internal_api_extensions.h>
#include "temp_ch_ta.h"

//      __________________________
//____/ TEE specific functions

/*
 * Called when the instance of the TA is created. This is the first call in
 * the TA.
 */
TEE_Result TA_CreateEntryPoint(void)
{
	DMSG("has been called");
	return TEE_SUCCESS;
}

/*
 * Called when the instance of the TA is destroyed if the TA has not
 * crashed or panicked. This is the last call in the TA.
 */
void TA_DestroyEntryPoint(void)
{
	DMSG("has been called");
}

/*
 * Called when a new session is opened to the TA. *sess_ctx can be updated
 * with a value to be able to identify this session in subsequent calls to the
 * TA. In this function you will normally do the global initialization for the
 * TA.
 */
TEE_Result TA_OpenSessionEntryPoint(uint32_t param_types,
									TEE_Param __maybe_unused params[4],
									void __maybe_unused **sess_ctx) {

	uint32_t exp_param_types = TEE_PARAM_TYPES(TEE_PARAM_TYPE_NONE,
						   					   TEE_PARAM_TYPE_NONE,
						   					   TEE_PARAM_TYPE_NONE,
						   					   TEE_PARAM_TYPE_NONE);

	DMSG("has been called");

	if (param_types != exp_param_types){
		return TEE_ERROR_BAD_PARAMETERS;
	}

	/* Unused parameters */
	(void)&params;
	(void)&sess_ctx;

	/* If return value != TEE_SUCCESS the session will not be created. */
	return TEE_SUCCESS;
}

/*
 * Called when a session is closed, sess_ctx hold the value that was
 * assigned by TA_OpenSessionEntryPoint().
 */
void TA_CloseSessionEntryPoint(void __maybe_unused *sess_ctx) {
	(void)&sess_ctx; /* Unused parameter */
	IMSG("Goodbye!\n");
}

//      __________________________
//____/ Utility functions

/**
 * Executes a workload that involves matrix initialization and a recursive computation.
 *
 * @param n An integer input for the recursive computation.
 * @return A long long integer result of the recursive computation.
 */
long long run_workload(int n){

	int A[SIZE][SIZE], B[SIZE][SIZE];
	// Initialize matrices A and B
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            A[i][j] = 69;
            B[i][j] = 99;
        }
    }

	// Calculate a constant value based on elements from A and B
    int c = A[3][4] + B[1][0];

    // Base cases for the recursion
    if (n == 0 || n == 1)
        return 1;
    else
        // Recursive computation with the additional constant c
        return n * run_workload(n - 1) + c;
}

/**
 * Parses the input string and executes the workload accordingly.
 *
 * @param str The input string consisting of '1's and '0's.
 *            '1' indicates executing the workload, and '0' indicates sleeping.
 * @param bit_time The time in milliseconds to run the workload or to sleep.
 */
void execute_workload(char *str, int bit_time) {
    int len = strlen(str);
    for (int i = 0; i < len; i++) {
        if (str[i] == '1') {
			TEE_Time start_time;
			TEE_Time current_time;
			TEE_GetREETime(&start_time);
			int ready = 0;
            printf("Executing workload for %d miliseconds...\n",bit_time);
			while (!ready){
            	run_workload(1000);
				TEE_GetREETime(&current_time);
				if (bit_time >= 1000){
					if (current_time.seconds - start_time.seconds >= (bit_time/1000)){
						ready = 1;
					}
				}
				else{
					if (current_time.millis - start_time.millis >= (bit_time)){
						ready = 1;
					}
				}
			}
        } else if (str[i] == '0') {
            printf("Sleeping for %d miliseconds...\n",bit_time);
            TEE_Wait(bit_time);
        } else {
            printf("Invalid character in string: %c\n", str[i]);
        }
    }
}

//      __________________________
//____/ Specific cmd functions

/**
 * Executes a covert channel with temperature based on parameters received
 *
 * @param param_types The types of parameters passed to the function.
 * @param params The array of parameters.
 * @return A TEE_Result indicating success or failure.
 */
static TEE_Result send_with_temp(uint32_t param_types, TEE_Param params[4]) {

	uint32_t exp_param_types = TEE_PARAM_TYPES(TEE_PARAM_TYPE_VALUE_INPUT,
						   					   TEE_PARAM_TYPE_MEMREF_INOUT,
											   TEE_PARAM_TYPE_NONE,
						   					   TEE_PARAM_TYPE_NONE);

	DMSG("has been called");

	if (param_types != exp_param_types){
		return TEE_ERROR_BAD_PARAMETERS;
	}

	int bit_time = params[0].value.a;
	char* msg = params[1].memref.buffer;
	IMSG("Sleep set to: %d", bit_time);

	IMSG("Data from shared memory: %s", params[1].memref.buffer);

    execute_workload(msg,bit_time);

	return TEE_SUCCESS;
}

//      __________________________
//____/ General entry point

/*
 * Called when a TA is invoked. sess_ctx hold that value that was
 * assigned by TA_OpenSessionEntryPoint(). The rest of the paramters
 * comes from normal world.
 */
TEE_Result TA_InvokeCommandEntryPoint(void __maybe_unused *sess_ctx, uint32_t cmd_id,
									  uint32_t param_types, TEE_Param params[4]) {

	(void)&sess_ctx; /* Unused parameter */

	switch (cmd_id) {
	case CMD_SEND_WITH_TEMP:
		return send_with_temp(param_types, params);
	default:
		return TEE_ERROR_BAD_PARAMETERS;
	}
}