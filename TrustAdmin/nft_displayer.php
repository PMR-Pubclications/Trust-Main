<?php
// Enforce strict TrustAdmin clearance before rendering
require_once __DIR__ . '/auth_guard.php';

$page_title = "NFT Displayer";
$api_key = "f25c57a885754235a82996ee8ed9b342";
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="access-level" content="TrustAdmin">
    <title><?= htmlspecialchars($page_title) ?></title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 20px;
            background-color: #0b0e14;
            color: #e6edf3;
        }

        #image-container {
            margin-top: 20px;
        }

        button {
            padding: 10px 20px;
            font-weight: bold;
            background-color: #238636;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }

        button:hover {
            background-color: #2ea043;
        }

        img {
            max-width: 400px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>

<body>
    <h1><?= htmlspecialchars($page_title) ?></h1>
    <button onclick="fetchImage()">Load Image</button>
    <div id="image-container"></div>

    <script>
        const API_KEY = "<?= htmlspecialchars($api_key) ?>";

        function fetchImage() {
            // Placeholder API URL
            const apiUrl = 'https://jsonplaceholder.typicode.com/photos/1';

            // Make a fetch request to the API
            fetch(apiUrl, {
                headers: {
                    'x-api-key': API_KEY
                }
            })
                .then(response => response.json())
                .then(data => {
                    // Assuming the API returns an object with a 'url' property for the image
                    const imageUrl = data.url;

                    // Display the image in the #image-container div
                    document.getElementById('image-container').innerHTML = `
                        <img src="${imageUrl}" alt="API Image">
                    `;
                })
                .catch(error => {
                    console.error('Error fetching image:', error);
                });
        }
    </script>
</body>

</html>
