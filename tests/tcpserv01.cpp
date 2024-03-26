#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stddef.h>
#include <sys/errno.h>

#include "tcp.h"

#define MAXLINE 1000

void str_echo(int connfd){
    static int t = 0;
    size_t n;
    char buf[MAXLINE];
    

    while((n = read(connfd, buf, MAXLINE)) > 0){
        // printf("Rec data...%s...%ld\n", buf, n);
        // sleep(5);
        write(connfd, buf, n);
    }

    if (n == 0){
        // sleep(5);
        printf("EOF...\n");
    }

    else if (n < 0)
    {
        perror("str_echo: read error");
    }    
}

int tcpserv01()
{
    int listenfd, connfd;

    pid_t childpid;
    socklen_t clilen;
    sockaddr_in cliaddr, servaddr;

    listenfd = socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(SERV_PORT);

    bind(listenfd, (sockaddr *)&servaddr, sizeof(servaddr));

    listen(listenfd, 3);

    for (;;){
        clilen = sizeof(cliaddr);
        connfd = accept(listenfd, (sockaddr *)&cliaddr, &clilen);

        if((childpid = fork()) == 0){
            close(listenfd);
            str_echo(connfd);
            printf("Server exiting...\n");
            close(connfd);
            exit(0);
        }

        close(connfd);
    }
}