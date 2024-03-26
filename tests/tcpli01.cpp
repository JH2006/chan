#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stddef.h>

#include "tcp.h"

void str_cli(FILE* fp, int sockfd){
    char sendline[MAXLINE], recvline[MAXLINE];

    while(fgets(sendline, MAXLINE, fp) != NULL){
        write(sockfd, sendline, strlen(sendline));

        if(read(sockfd, recvline, MAXLINE) == 0){
            perror("str_cli: server terminated prematurely");
            exit(-1);
        }

        fputs(recvline, stdout);
    }

    printf("Client existing...\n");
}

int main(int argc, char ** argv){
    int sockfd;
    sockaddr_in servaddr;

    if(argc != 2)
        perror("usage: tcpcli parameter is wrong");

    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERV_PORT);
    inet_pton(AF_INET, argv[1], &servaddr.sin_addr);

    connect(sockfd, (sockaddr*)&servaddr, sizeof(servaddr));

    str_cli(stdin, sockfd);

    close(sockfd);

    exit(0);
}