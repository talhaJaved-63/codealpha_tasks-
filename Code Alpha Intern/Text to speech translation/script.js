const API_URL = 'https://api.mymemory.translated.net/get';

const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const sourceLang = document.getElementById('sourceLang');
const targetLang = document.getElementById('targetLang');
const translateBtn = document.getElementById('translateBtn');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyBtn');
const speakBtn = document.getElementById('speakBtn');
const swapBtn = document.getElementById('swapBtn');
const charCount = document.getElementById('charCount');
const status = document.getElementById('status');

function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
}

function hideStatus() {
    status.style.display = 'none';
}

async function translateText() {
    const text = inputText.value.trim();

    if (!text) {
        showStatus('Please enter text to translate', 'error');
        return;
    }

    const source = sourceLang.value;
    const target = targetLang.value;

    if (source === target) {
        outputText.textContent = text;
        showStatus('Source and target languages are the same', 'success');
        return;
    }

    showStatus('Translating...', 'loading');
    translateBtn.disabled = true;
    translateBtn.textContent = 'Translating...';

    try {
        const langPair = source === 'auto' ? `|${target}` : `${source}|${target}`;
        const url = `${API_URL}?q=${encodeURIComponent(text)}&langpair=${encodeURIComponent(langPair)}`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data.responseStatus === 200 && data.responseData) {
            outputText.textContent = data.responseData.translatedText;
            showStatus('Translation completed successfully!', 'success');
        } else {
            throw new Error(data.responseData?.translatedText || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        showStatus(`Error: ${error.message}. Please try again.`, 'error');
        outputText.textContent = 'Translation failed. Please try again.';
    } finally {
        translateBtn.disabled = false;
        translateBtn.textContent = 'Translate';
        setTimeout(hideStatus, 5000);
    }
}

function clearInput() {
    inputText.value = '';
    outputText.textContent = 'Translation will appear here...';
    charCount.textContent = '0 / 5000';
    hideStatus();
}

function copyTranslation() {
    const text = outputText.textContent;

    if (text === 'Translation will appear here...' || text === 'Translation failed. Please try again.') {
        showStatus('No translation to copy', 'error');
        return;
    }

    navigator.clipboard.writeText(text).then(() => {
        showStatus('Copied to clipboard!', 'success');
        setTimeout(hideStatus, 2000);
    }).catch(() => {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showStatus('Copied to clipboard!', 'success');
        setTimeout(hideStatus, 2000);
    });
}

function speakTranslation() {
    const text = outputText.textContent;

    if (text === 'Translation will appear here...' || text === 'Translation failed. Please try again.') {
        showStatus('No translation to speak', 'error');
        return;
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = targetLang.value;
        utterance.rate = 0.9;
        utterance.pitch = 1;

        utterance.onstart = () => {
            speakBtn.textContent = '🔊 Speaking...';
            speakBtn.disabled = true;
        };

        utterance.onend = () => {
            speakBtn.textContent = '🔊 Speak';
            speakBtn.disabled = false;
        };

        utterance.onerror = () => {
            speakBtn.textContent = '🔊 Speak';
            speakBtn.disabled = false;
            showStatus('Text-to-speech failed', 'error');
        };

        window.speechSynthesis.speak(utterance);
    } else {
        showStatus('Text-to-speech is not supported in your browser', 'error');
    }
}

function swapLanguages() {
    if (sourceLang.value === 'auto') {
        showStatus('Cannot swap when source is set to Auto Detect', 'error');
        setTimeout(hideStatus, 2000);
        return;
    }

    const temp = sourceLang.value;
    sourceLang.value = targetLang.value;
    targetLang.value = temp;

    const tempText = inputText.value;
    inputText.value = outputText.textContent;
    outputText.textContent = tempText || 'Translation will appear here...';

    updateCharCount();
}

function updateCharCount() {
    const count = inputText.value.length;
    charCount.textContent = `${count} / 5000`;
}

translateBtn.addEventListener('click', translateText);
clearBtn.addEventListener('click', clearInput);
copyBtn.addEventListener('click', copyTranslation);
speakBtn.addEventListener('click', speakTranslation);
swapBtn.addEventListener('click', swapLanguages);
inputText.addEventListener('input', updateCharCount);

inputText.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        translateText();
    }
});

updateCharCount();