#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 9999
#define MAX_BUFFER 1024

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[MAX_BUFFER];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 1) < 0) {
        perror("Listen");
        exit(EXIT_FAILURE);
    }

    printf("Listening on port %d...\n", PORT);

    new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
    if (new_socket < 0) {
        perror("Accept");
        exit(EXIT_FAILURE);
    }

    printf("Connection received from %s:%d\n", inet_ntoa(address.sin_addr), ntohs(address.sin_port));

    fd_set fdset;
    while (1) {
        FD_ZERO(&fdset);
        FD_SET(0, &fdset); // stdin
        FD_SET(new_socket, &fdset);

        if (select(new_socket + 1, &fdset, NULL, NULL, NULL) < 0) {
            perror("Select error");
            exit(EXIT_FAILURE);
        }

        // Check if data is coming from remote shell
        if (FD_ISSET(new_socket, &fdset)) {
            memset(buffer, 0, MAX_BUFFER);
            int valread = read(new_socket, buffer, MAX_BUFFER - 1);
            if (valread <= 0) {
                printf("Connection closed by remote host.\n");
                break;
            }
            printf("%s", buffer);
            fflush(stdout);
        }

        // Check if user types input
        if (FD_ISSET(0, &fdset)) {
            memset(buffer, 0, MAX_BUFFER);
            fgets(buffer, MAX_BUFFER, stdin);
            send(new_socket, buffer, strlen(buffer), 0);
        }
    }

    close(new_socket);
    close(server_fd);
    return 0;
}
