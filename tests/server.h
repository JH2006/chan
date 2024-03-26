#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stddef.h>

// int lfd = 0;
// int maxfd = 0;
// fd_set rdset;
// fd_set rdtemp;

void server()
{
    // 1. Socket
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    int maxfd = lfd;

    // 2. Bind
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9999);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(lfd, (sockaddr*)&addr, sizeof(addr));

    // 3. Listen
    listen(lfd, 10);

    fd_set rdset;
    // fd_set rdtemp;

    FD_ZERO(&rdset);
    FD_SET(lfd, &rdset);

    while(1){
        fd_set rdtemp = rdset;
        int num = select(maxfd + 1, &rdtemp, NULL, NULL, NULL);

        // New connection
        if(FD_ISSET(lfd, &rdtemp)){
            // sockaddr_in clientaddr;
            // socklen_t clientlen = sizeof(clientaddr);
            // int cfd = accept(lfd, (sockaddr*)& clientaddr, &clientlen);

            int cfd = accept(lfd, NULL, NULL);

            if(cfd < 0){
                perror("accepted failed\n");
                exit(-1);
            }

            FD_SET(cfd, &rdset);
            maxfd = maxfd > cfd? maxfd : cfd;
            printf("Build connection %d\n", cfd);
        }
        
        for(int i = 0; i < maxfd + 1; i ++){
            if(i != lfd && FD_ISSET(i, &rdtemp)){

                char buf[1024] = {0};
                int len = read(i, buf, sizeof(buf));

                if(len == 0){
                    printf("客户端关闭链接....\n");
                    FD_CLR(i, &rdset);
                    close(i);
                }
                else if(len > 0){
                    printf("发送数据...%s", buf);
                    write(i, buf, strlen(buf) + 1);
                }
                else{
                    printf("客户端异常....\n");
                    FD_CLR(i, &rdset);
                    close(i);
                }
            }
        }
    }

    close(lfd);
}