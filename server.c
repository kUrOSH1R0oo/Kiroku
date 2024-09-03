#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 8080
#define BUFFER_SIZE 1024
#define FILENAME "key_captures.txt"

// Function to handle the client request
void handle_request(int new_socket) {
    char buffer[BUFFER_SIZE] = {0};
    int valread = read(new_socket, buffer, BUFFER_SIZE);

    if (valread > 0) {
        FILE *file = fopen(FILENAME, "w");
        if (file == NULL) {
            perror("Could not open file");
            exit(EXIT_FAILURE);
        }
        fprintf(file, "%s", buffer);
        fclose(file);
        char *success_message = "Successfully set the data";
        send(new_socket, success_message, strlen(success_message), 0);
    } else {
        perror("Failed to read data");
    }
    close(new_socket);
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Bind the socket to the port
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Listen for incoming connections
    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("[+] Server is listening on port %d...\n", PORT);

    while (1) {
        // Accept a new connection
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0) {
            perror("Accept failed");
            close(server_fd);
            exit(EXIT_FAILURE);
        }

        // Handle the request
        handle_request(new_socket);
    }

    return 0;
}
