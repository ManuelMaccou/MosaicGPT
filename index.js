require('dotenv').config();

const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

const { streamOpenAIResponse } = require('./answers.js');

app.post('/triggerStreaming', async (req, res) => {
    try {
        const userQuery = req.body.userQuery;
        const context = req.body.context;

        // This function is assumed to handle the response to be sent back to Bubble.
        // You will need to implement the actual mechanism to send data back to Bubble.
        const bubble_fn_openAiResponce = (data) => {
            console.log('Data to send back to Bubble:', data);
            // Implementation for sending data back to Bubble goes here
        };

        // Awaiting the response from the streamOpenAIResponse function
        await streamOpenAIResponse({ param1: userQuery, param2: context }, bubble_fn_openAiResponce);

        // Sending a success response back to the caller
        res.status(200).send('Streaming triggered successfully');
    } catch (error) {
        console.error('Error in /triggerStreaming:', error);

        // Sending an error response back to the caller
        res.status(500).send('Error triggering streaming');
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
