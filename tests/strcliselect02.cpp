#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <stddef.h>
#include <algorithm>
#include <sys/select.h>

#include "tcp.h"
using namespace std;
#define MAXLINE 50

void str_cli(FILE* fp, int sockfd)
{
    int maxfdp1, stdineof;
    fd_set reset;
    char buf[MAXLINE];
    int n;

    stdineof = 0;
    FD_ZERO(&reset);

    for (;;)
    {
        if(stdineof == 0)
            FD_SET(fileno(fp), &reset);

        FD_SET(sockfd, &reset);
        maxfdp1 = max(fileno(fp), sockfd) + 1;

        select(maxfdp1, &reset, NULL, NULL, NULL);

        if(FD_ISSET(sockfd, &reset)){
            // 只要套接字内存有东西就去读，每次最多读MAXLINE字节
            // 内存中剩下的下次继续读，指针位置由内核自动修改
            if((n = read(sockfd, buf, MAXLINE)) == 0){
                if(stdineof == 1){
                    // printf("Client quit....%d\n", time);
                    return;
                }
                else{
                    perror("str_cli: server terminated prematurely");
                    exit(-1);
                }
            }

            if(n == -1){
                perror("str_cli: something gose wrong");
                exit(-1);
            }

            // printf("Echo data....%d\n", time);

            // 缓存有多少写多少
            write(fileno(stdout), buf, n);
        }

        if(FD_ISSET(fileno(fp), &reset)){
            // 只要文件句柄有内容可以读，每次最多读MAXLINE
            // 和Socket应用原理一样，如果内存有剩余数据，select会继续返回
            if((n = read(fileno(fp), buf, MAXLINE)) == 0){
                stdineof = 1;
                shutdown(sockfd, SHUT_WR);
                FD_CLR(fileno(fp), &reset);

                // 跳过write的部分
                // 感觉上没有把EOF送给服务器，那么服务器如何能回传EOF呢？
                // printf("EOF check....%d\n", time);
                continue;
            }
            
            // 正常发送
            // printf("Normal send....\n");
            write(sockfd, buf, n);
            sleep(2);
            // for (int i = 0; i < n; i++){

            //     write(sockfd, &buf[i], 1);
            //     sleep(5);
            // }
        }
    }

    
}

int main(int argc, char ** argv){
    int sockfd;
    sockaddr_in servaddr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERV_PORT);
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);

    connect(sockfd, (sockaddr*)&servaddr, sizeof(servaddr));

    str_cli(stdin, sockfd);

    close(sockfd);

    exit(0);
}