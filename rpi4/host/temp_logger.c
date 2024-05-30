#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_BUF 256

int main(int argc, char *argv[]){

    // Check measurements param
    if(argc != 3) {
        printf("Usage: %s <measurements> <sampling> \n", argv[0]);
        return 1;
    }
    long long int measurements = atoi(argv[1]);
    long int sampling = atoi(argv[2]);

    FILE *fp;
    char buf[MAX_BUF];

    // Path to the file containing CPU temperature (specific to Linux systems)
    const char *temp_file = "/sys/class/thermal/thermal_zone0/temp";

    for (long long int i = 0; i < measurements; i++) {
        fp = fopen(temp_file, "r");
        if (fp == NULL) {
            printf("Error opening temperature file\n");
            exit(1);
        }

        // Read temperature value
        fgets(buf, MAX_BUF, fp);
        fclose(fp);

        // Convert string to integer (temperature is in millidegrees Celsius)
        float temp = atof(buf) / 1000;

        printf("%f\n", temp);

        // Wait for 10 milliseconds
        usleep(sampling);
    }
    return 0;
}