#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stddef.h>
#include <sys/errno.h>
#include <vector>

#include "tcp.h"

using namespace std;

#define MAXLINE 100

int tcpserv02()
{

    char buf[MAXLINE] = {0};

    sockaddr_in servaddr;

    int listenfd = socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(SERV_PORT);

    bind(listenfd, (sockaddr *)&servaddr, sizeof(servaddr));

    listen(listenfd, 3);

    fd_set rdset, rdtemp;

    FD_ZERO(&rdset);
    FD_SET(listenfd, &rdset);

    int maxfd = listenfd;

    vector<int> clientconns(FD_SETSIZE, -1);

    int c = 0;
    for (;;)
    {
        rdtemp = rdset;

        int nready = select(maxfd + 1, &rdtemp, NULL, NULL, NULL);

        // 新链接
        if(FD_ISSET(listenfd, &rdtemp)){
            int cfd = accept(listenfd, NULL, NULL);
            if(cfd < 0){
                perror("accepted failed");
                exit(-1);
            }

            // 寻找第一个可用的标识符位置
            // 目前没有加入异常处理，比如队列满
            for(auto& fd : clientconns){
                if(fd == -1){
                    fd = cfd;
                    break; 
                }
            }

            maxfd = max(maxfd, cfd);
            FD_SET(cfd, &rdset);
            printf("build connection %d\n", cfd);

            // 如果有效fd已经处理完，此次循环到此结束
            if(--nready <= 0)
                continue;
        }

        // 客户端链接处理
        for(auto& fd : clientconns){

            if (fd != -1)
            {
                if(FD_ISSET(fd, &rdtemp)){
                    size_t n;
                    
                    if((n = read(fd, buf, MAXLINE)) > 0){
                        // printf("Rec data...%s...%ld\n", buf, n);
                        write(fd, buf, n);
                    }
                    else if(n == 0){
                        FD_CLR(fd, &rdset);
                        close(fd);

                        if(maxfd <= fd){
                            for(auto i : clientconns)
                                maxfd = max(i, maxfd);
                        }

                        printf("Client close....%d\n", fd);

                        fd = -1;
                    }
                    else{
                        perror("str_echo: read error");
                        FD_CLR(fd, &rdset);
                        close(fd);
                    }

                    if(--nready <= 0)
                        continue;
                }
            }
        }
    }

    FD_CLR(listenfd, &rdset);
    close(listenfd);

    printf("Server close....\n");
}