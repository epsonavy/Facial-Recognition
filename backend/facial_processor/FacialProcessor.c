#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/time.h>
#include <semaphore.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

long MAX_TASKS;

int active = 0;

typedef struct FacialProcessorTask
{
	const char* command;
} FacialProcessorSingle;

//These will just contain C or 
void* scan_files(void* args){
	while(active){
	//this will perform a DFS search of the /videos directory repeatedly..
	//moving those in /videos into /queue/
	//once finished.. it will be in the static folder of NGINX
	//it will send a request to the main Node.js server
	//and send a packet to it's own peer load balancer, which will send a packet to the main load balancer
	}
}

int main(int argc, char* argv[]){
	MAX_TASKS = sysconf(_SC_NPROCESSORS_ONLN); //we will store the max number of processors
	active = 1;
	pthread_t scanFilesThread;
	pthread_create(&scanFilesThread, NULL, scan_files, NULL);
	pthread_join(scanFilesThread, NULL);
}
