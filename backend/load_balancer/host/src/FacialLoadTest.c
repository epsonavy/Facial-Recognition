/************************************************
 *
 * IBM Confidential
 * Fuck IBM
 *
 * FacialLoadBalancerServer.c
 * You should build this to make the server for the
 * facial recognizer load balancer.
 *
************************************************/
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/time.h>
#include <semaphore.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <string.h>

#include "FacialLoadEncryption.h"
#include "FacialLoadPackets.h"
#define MAX_SERVERS 100

int active = 0;
int reroute_socket;
int master_socket;

struct sockaddr_in master_addr;
struct sockaddr_in reroute_addr;

typedef struct FacialLoadPeer{
	int mem_usage;
	int cpu_usage;
	int tasks_remaining;
	int socket;
} FacialLoadPeer;

int some_array[1000];
FacialLoadPeer peers[MAX_SERVERS];

void* accept_thread(void* args){
	
	int poll_activity;
	struct pollfd* poll_sockets_ptr;
	struct pollfd master_poll;
	master_poll.fd = master_socket;
	master_poll.events = POLLIN;

	struct pollfd poll_sockets[MAX_SERVERS];
	poll_sockets[0] = master_poll;

	//have to uninitialize them
	for (int i=0; i<sizeof(poll_sockets) / sizeof(struct pollfd); i++){
		if(i != 0) poll_sockets[i].fd = -1;	
	}

	printf("Now accepting peers to list\n");
	while(active){
		poll_sockets_ptr = &poll_sockets[0];
		poll_activity = poll(poll_sockets_ptr, sizeof(poll_sockets) / sizeof(struct pollfd), -1);
		if(poll_activity < 0){
			perror("poll");
		}
		if (poll_sockets[0].revents & POLLIN){
			int new_socket;
			struct sockaddr_in client_address;
			int client_addrlen = sizeof(client_address);
			if ((new_socket = accept(master_socket, (struct sockaddr*) &client_address, (socklen_t*) &client_addrlen)) < 0){
				perror("accept");
			}else{
				struct pollfd add_socket;
				add_socket.fd = new_socket;
				add_socket.events = POLLIN;
				int free = 0;
				for(int i=0; i<sizeof(poll_sockets) / sizeof(struct pollfd); i++){
					if(poll_sockets[i].fd == -1){
						poll_sockets[i] = add_socket;
						free = 1;
					}
				}
				if (free){
					char* ip = inet_ntoa(client_address.sin_addr);
					printf("Peer was accepted at %s\n", ip);
				}else{
					printf("Peer was not accepted because of maximum server reached.\n");
				}
				char* write_address = "http://localhost:3000/upload\0";
				send(add_socket.fd, write_address, strlen(write_address), 0);
			}

		}
		//we must authenticate users before going here actually..
		//but we'll make it first
		for(int i=1; i<sizeof(poll_sockets) / sizeof(struct pollfd); i++){
			if (poll_sockets[i].revents & POLLIN){
				int s = poll_sockets[i].fd;
				struct FacialLoadPacket packet;
				if ((read(poll_sockets[i].fd, &packet, sizeof(struct FacialLoadPacket))) != 0){
					switch(packet.type){
						case Health:
						break;
						case Done:
						break;
					}
				}else{
					close(poll_sockets[i].fd);
					poll_sockets[i].fd = -1; //clear up for another person to get in
					
				}
			}
		}
	usleep(500);
	}
	return NULL;
}

void* reroute_thread(void* args){

	while(active){
		
	}
}

int main(int argc, char* argv[]){
	printf("Load Balancer Server for Facial Recognition starting...\n");
	
	reroute_socket = socket(AF_INET, SOCK_STREAM, 0);
	reroute_addr.sin_port = htons(27010);
	reroute_addr.sin_addr.s_addr = INADDR_ANY;
	
	if(bind(reroute_socket, (struct sockaddr*)&reroute_addr, sizeof(reroute_addr)) < 0){
		perror("reroute-bind");
	}

	if(listen(reroute_socket, 0)){
		perror("reroute-listen");
	}

	master_socket = socket(AF_INET, SOCK_STREAM, 0);
	master_addr.sin_port = htons(27015);
	master_addr.sin_addr.s_addr = INADDR_ANY;

	if(bind(master_socket, (struct sockaddr*)&master_addr, sizeof(master_addr)) < 0){
		perror("bind");
		return 1;
	}
	if(listen(master_socket, 0)){
		perror("listen");
		return 1;
	}
	
	active = 1;
	pthread_t acceptThread;
	pthread_create(&acceptThread, NULL, accept_thread, NULL);

	pthread_t rerouteThread;
	pthread_create(&rerouteThread, NULL, reroute_thread, NULL);

	pthread_join(acceptThread, NULL);
	pthread_join(rerouteThread, NULL);
	return 0;
}
