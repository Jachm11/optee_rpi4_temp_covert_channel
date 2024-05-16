#include <err.h>
#include <stdio.h>
#include <string.h>

/* OP-TEE TEE client API (built by optee_client) */
#include <tee_client_api.h>

/* For the UUID (found in the TA's h-file(s)) */
#include "../ta/temp_ch_ta.h"

int main(void)
{
	TEEC_Result res;
	TEEC_Context ctx;
	TEEC_Session sess;
	TEEC_Operation op;
	TEEC_UUID uuid = TEMP_CH_TA_UUID;
	uint32_t err_origin;

	/* Initialize a context connecting us to the TEE */
	res = TEEC_InitializeContext(NULL, &ctx);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_InitializeContext failed with code 0x%x", res);

	/*
	 * Open a session to the "hello world" TA, the TA will print "hello
	 * world!" in the log when the session is created.
	 */
	res = TEEC_OpenSession(&ctx, &sess, &uuid,
			       TEEC_LOGIN_PUBLIC, NULL, NULL, &err_origin);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_Opensession failed with code 0x%x origin 0x%x",
			res, err_origin);

	/*
	 * Execute a function in the TA by invoking it, in this case
	 * we're incrementing a number.
	 *
	 * The value of command ID part and how the parameters are
	 * interpreted is part of the interface provided by the TA.
	 */

	/* Clear the TEEC_Operation struct */
	memset(&op, 0, sizeof(op));

	/*
	 * Prepare the argument. Pass a value in the first parameter,
	 * the remaining three parameters are unused.
	 */
	op.paramTypes = TEEC_PARAM_TYPES(TEEC_VALUE_INOUT, 
				TEEC_NONE,
				TEEC_MEMREF_TEMP_INOUT, 
				TEEC_NONE);

	op.params[0].value.a = 68;

	TEEC_SharedMemory shared_mem;
	shared_mem.size = 1024;
	shared_mem.flags = TEEC_MEM_INPUT | TEEC_MEM_OUTPUT;
	
	res = TEEC_AllocateSharedMemory(&ctx,&shared_mem);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_AllocateSharedMemory failed with code 0x%x", res);

	if (shared_mem.buffer != NULL) {
    // Shared memory allocation successful
    // You can now access and use the shared memory through the buffer pointer

    // Example: Writing data to shared memory
    strcpy(shared_mem.buffer, "Hello, shared memory!");

	} else {
		// Shared memory allocation failed
		errx(1, "Shared memory allocation failed");
	}

	op.params[2].memref.parent = shared_mem.buffer;
	op.params[2].memref.size = 1024;
	op.params[2].memref.offset = 0;

	printf("Data from shared memory: %s\n", shared_mem.buffer);

	/*
	 * TA_HELLO_WORLD_CMD_INC_VALUE is the actual function in the TA to be
	 * called.
	 */
	printf("Invoking TA to increment %d\n", op.params[0].value.a);
	res = TEEC_InvokeCommand(&sess, CMD_SEND_WITH_TEMP, &op, &err_origin);
	if (res != TEEC_SUCCESS)
		errx(1, "TEEC_InvokeCommand failed with code 0x%x origin 0x%x",
			res, err_origin);
	printf("TA incremented value to %d\n", op.params[0].value.a);

	/*
	 * We're done with the TA, close the session and
	 * destroy the context.
	 *
	 * The TA will print "Goodbye!" in the log when the
	 * session is closed.
	 */

	printf("Data from shared memory: %s\n", shared_mem.buffer);

    TEEC_ReleaseSharedMemory(&shared_mem);

	TEEC_CloseSession(&sess);

	TEEC_FinalizeContext(&ctx);

	return 0;
}