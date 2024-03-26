//
// Created by root on 1/28/24.
//

#ifndef ENGINE_CLIENT_H
#define ENGINE_CLIENT_H
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>

int main(){
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if(fd == -1){
        perror("Scoket");
        exit(0);
    }

    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9999);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    int ret = connect(fd, (sockaddr*)& addr, sizeof(addr));
    if(ret == -1){
        perror("connect");
        exit(0);
    }
    
    while(1){
        char recvBuf[] = "Hello world\n";
        // fgets(recvBuf, sizeof(recvBuf), stdin);
        write(fd, recvBuf, sizeof(recvBuf));
        // read(fd, recvBuf, sizeof(recvBuf));
        // printf("recv buf: %s", recvBuf );
        sleep(1);
    }

    close(fd);

    return 0;

}
#endif //ENGINE_CLIENT_H
