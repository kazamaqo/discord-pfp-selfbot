document.addEventListener('DOMContentLoaded', async () => {
    const tokenInput = document.getElementById('tokenInput');
    const extractBtn = document.getElementById('extractBtn');
    const sendBtn = document.getElementById('sendBtn');
    const statusDiv = document.getElementById('status');
    const botUrlInput = document.getElementById('botUrl');

    // Try to extract token when popup opens
    extractBtn.addEventListener('click', async () => {
        statusDiv.textContent = '🔍 Extracting token...';
        statusDiv.className = 'status loading';

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            chrome.tabs.sendMessage(tab.id, { action: 'getToken' }, (response) => {
                if (chrome.runtime.lastError) {
                    statusDiv.textContent = '❌ Error: Make sure you\'re on discord.com';
                    statusDiv.className = 'status error';
                    return;
                }

                if (response && response.token) {
                    tokenInput.value = response.token;
                    statusDiv.textContent = '✓ Token extracted! Click "Send to Bot" to proceed.';
                    statusDiv.className = 'status success';
                } else {
                    statusDiv.textContent = '❌ Could not extract token. Try refreshing Discord.';
                    statusDiv.className = 'status error';
                }
            });
        } catch (error) {
            statusDiv.textContent = '❌ Error: ' + error.message;
            statusDiv.className = 'status error';
        }
    });

    // Send token to bot
    sendBtn.addEventListener('click', async () => {
        const token = tokenInput.value.trim();
        const botUrl = botUrlInput.value.trim();

        if (!token) {
            statusDiv.textContent = '❌ Please extract a token first';
            statusDiv.className = 'status error';
            return;
        }

        if (!botUrl) {
            statusDiv.textContent = '❌ Please enter bot URL';
            statusDiv.className = 'status error';
            return;
        }

        statusDiv.textContent = '📤 Sending token to bot...';
        statusDiv.className = 'status loading';

        try {
            const response = await fetch(`${botUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `token=${encodeURIComponent(token)}`
            });

            if (response.ok) {
                statusDiv.textContent = '✓ Token sent! Check your bot logs.';
                statusDiv.className = 'status success';
                tokenInput.value = '';

                // Save bot URL for next time
                chrome.storage.local.set({ botUrl: botUrl });

                setTimeout(() => {
                    window.close();
                }, 2000);
            } else {
                statusDiv.textContent = '❌ Failed to send token. Check bot URL.';
                statusDiv.className = 'status error';
            }
        } catch (error) {
            statusDiv.textContent = '❌ Error: ' + error.message;
            statusDiv.className = 'status error';
        }
    });

    // Load saved bot URL
    chrome.storage.local.get(['botUrl'], (result) => {
        if (result.botUrl) {
            botUrlInput.value = result.botUrl;
        }
    });
});
