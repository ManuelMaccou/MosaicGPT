require('dotenv').config();
const fetch = require('node-fetch');


export async function streamOpenAIResponse(properties, bubble_fn_openAiResponce) {
    console.log("Starting the streamOpenAIResponse function...");

    const url = "https://api.openai.com/v1/chat/completions";
    const headers = {
        "Authorization": "Bearer " + process.env.OPENAI_API_KEY,
        "Content-Type": "application/json"
    };
    const body = JSON.stringify({
        model: "gpt-4-1106-preview",
        messages: [
            {"role": "system", "content": "You are an expert in Web3 and love teaching people all about it. When questions come in, give a helpful answer, but keep responses concise and short."},
            {"role": "user", "content": "Using the following context, answer this question: " + properties.param1 + " Context: " + properties.param2}
        ],
        stream: true
    });

    console.log("Context being sent to OpenAI:", properties.param2);

    try {
        const response = await fetch(url, { method: 'POST', headers: headers, body: body });
        console.log("Received a response:", response);

        const reader = response.body.getReader();
        let accumulatedContent = "";
        let done, value;

        while (true) {
            ({ done, value } = await reader.read());
            if (done) {
                console.log("Stream complete");
                break;
            }

            const rawChunk = new TextDecoder("utf-8").decode(value);
            console.log("Received raw chunk:", rawChunk);

            const lines = rawChunk.split('\n');
            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const jsonStr = line.replace(/^data: /, '').trim();
                    if (jsonStr === "[DONE]") {
                        console.log("Received end-of-stream marker.");
                        break;
                    }

                    const data = JSON.parse(jsonStr);
                    if (data.choices && data.choices[0] && data.choices[0].delta && data.choices[0].delta.content) {
                        console.log("Parsed content from line:", data.choices[0].delta.content);
                        accumulatedContent += data.choices[0].delta.content;
                        bubble_fn_openAiResponce(accumulatedContent);
                    }
                }
            }
        }
    } catch (error) {
        console.error("Streaming failed:", error);
    }
}
