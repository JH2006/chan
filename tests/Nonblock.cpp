#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

#define MAXLINE 500

char buf[MAXLINE];

void readn(int fd, void* vptr, size_t n) {
	size_t nleft;
	size_t nread;
	size_t totalsize = 0;
	char* ptr;

	ptr = (char*)vptr;
	nleft = n;

	while (true) {
		if ((nread = read(fd, ptr, MAXLINE)) < 0) {
			if (errno == EINTR) {
				nread = 0;
			}
			else {
				perror("wrong read");
				_exit(-1);
			}
				
		}
		else if (nread == 0) {
			printf("EOF\n");
			break;
		}

		nleft -= nread;
		totalsize += nread;
		printf("%ld bytes to read, %ld total read\n", nleft, totalsize);
	}
}

int main(void)
{

	readn(STDIN_FILENO, buf, MAXLINE);

	int ntowrite, nwrite; 
	char* ptr = nullptr;


	// Set Non-block property 
	int flags;

	/*if ((flags = fcntl(STDOUT_FILENO, F_GETFL, 0)) == -1) {
		perror("Error getting flags");
		return -1; 
	}

	flags |= O_NONBLOCK;
	if (fcntl(STDOUT_FILENO, F_SETFL, flags) == -1) {
		perror("Error setting non-blocking flag");
		return -1;
	}*/

	ptr = buf;

	// // Reset the Non black flags
	// flags &= ~O_NONBLOCK;
	// if (fcntl(STDOUT_FILENO, F_SETFL, flags) == -1) {
	// 	perror("Error resetting non-blocking flag");
	// 	return -1;
	// }

	// size_t totalsize = 0;
	// while (true) {

	// 	nwrite = write(STDOUT_FILENO, ptr, MAXLINE);
	// 	printf("nwrite = %d, errno = %d\n", nwrite, errno);

	// 	if (nwrite > 0) {
	// 		ptr += nwrite;
	// 		ntowrite -= nwrite;
	// 		totalsize += nwrite;
	// 	}

	// 注意：这个条件出不来，write没有类似read能识别EOF的机制，只能靠字节数
	// 	else if (nwrite == 0){
	// 		printf("EOF\n");
	// 		break;
	// 	}

	// 	printf("%d bytes to read, %ld total read\n", nwrite, totalsize);

	// }

	// printf("Writing completed\n");

	// Reset the Non black flags
	// flags &= ~O_NONBLOCK;
	// if (fcntl(STDOUT_FILENO, F_SETFL, flags) == -1) {
	// 	perror("Error resetting non-blocking flag");
	// 	return -1;
	// }

	return 0;


}

