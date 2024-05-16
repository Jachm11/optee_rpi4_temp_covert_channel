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

// Function to execute the workload
long long runWorkload(int n){

	int A[SIZE][SIZE], B[SIZE][SIZE];
	// Initialize matrices A and B
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            A[i][j] = 69;  // Random numbers between 0 and 99
            B[i][j] = 100;  // Random numbers between 0 and 99
        }
    }

	int c = A[3][4] + B[1][0];

    if (n == 0 || n == 1)
        return 1;
    else
        return n * runWorkload(n - 1) + c;
}

// Function to parse the string and execute workload accordingly
void executeWorkload(char *str) {
    int len = strlen(str);
    for (int i = 0; i < len; i++) {
        if (str[i] == '1') {
			//TEE_Time *time;
			//TEE_GetSystemTime(time);
			//printf(time);
            printf("Executing workload for 5 seconds...\n");
			for (int j = 0; j < 2020; j++){
            	runWorkload(100000);
			}
        } else if (str[i] == '0') {
            printf("Sleeping for 5 seconds...\n");
            TEE_Wait(5000);
        } else {
            printf("Invalid character in string: %c\n", str[i]);
        }
    }
}

//      __________________________
//____/ Specific cmd functions

static TEE_Result send_with_temp(uint32_t param_types, TEE_Param params[4]) {

	uint32_t exp_param_types = TEE_PARAM_TYPES(TEE_PARAM_TYPE_VALUE_INPUT,
						   					   TEE_PARAM_TYPE_MEMREF_INOUT,
											   TEE_PARAM_TYPE_NONE,
						   					   TEE_PARAM_TYPE_NONE);

	DMSG("has been called");

	if (param_types != exp_param_types){
		return TEE_ERROR_BAD_PARAMETERS;
	}

	int sleep_time = params[0].value.a;
	IMSG("Sleep set to: %d", sleep_time);

	printf("Data from shared memory: %s\n", params[1].memref.buffer);

	//strcpy(params[1].memref.buffer, "Goodbye, shared memory!");

	TEE_Time tt;
	TEE_GetREETime(&tt);

	printf("time is %d\n",tt.seconds);



	//char input[] = "0100110101110"; // Change this string as per your requirement
    //executeWorkload(input);

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