const sendButton = document.getElementById('sendButton');
const userInput = document.getElementById('userInput');
const messageArea = document.getElementById('messageArea');
const uploadFile = document.getElementById('uploadFile');
const studyWithAIButton = document.getElementById('studyWithAI');
const gradingButton = document.getElementById('grading');

const studyWithAIInterface = document.getElementById('studyWithAIInterface');
const gradingInterface = document.getElementById('gradingInterface');

const introButton = document.getElementById('introMode'); // Nút giới thiệu
const introInterface = document.getElementById('introInterface'); // Giao diện giới thiệu

// Khu vực phản hồi cho chấm điểm
const gradingResponseArea = document.getElementById('gradingResponseArea'); 

// Biến để lưu chế độ hiện tại
let currentMode = 'introMode'; // Mặc định là "giới thiệu"

// Hàm xử lý Markdown thủ công và tách các phần
function formatResponse(responseText) {
    const links = [];
    responseText = responseText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
        const index = links.length;
        links.push({ text, url });
        return `{{LINK${index}}}`;  
    });

    const codeBlocks = [];
    responseText = responseText.replace(/```(.*?)```/gs, (match, code) => {
        const index = codeBlocks.length;
        codeBlocks.push(code);  
        return `{{CODEBLOCK${index}}}`;  
    });

    const lists = [];
    responseText = responseText.replace(/^\s*-\s(.*?)(?=\n|$)/gm, (match, listItem) => {
        const index = lists.length;
        lists.push(listItem);  
        return `{{LIST${index}}}`;  
    });

    const sentences = responseText.split(/(?<=\.)|\n/).map(sentence => sentence.trim()).filter(sentence => sentence.length > 0);

    const listItems = sentences.map(sentence => `<li>${sentence}</li>`).join('');
    responseText = `<ul>${listItems}</ul>`; 

    responseText = responseText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');  
    responseText = responseText.replace(/__(.*?)__/g, '<strong>$1</strong>');      

    responseText = responseText.replace(/\*(.*?)\*/g, '<em>$1</em>');  
    responseText = responseText.replace(/_(.*?)_/g, '<em>$1</em>');    

    links.forEach((link, index) => {
        const placeholder = `{{LINK${index}}}`;
        responseText = responseText.replace(placeholder, `<a href="${link.url}" target="_blank">${link.text}</a>`);
    });

    codeBlocks.forEach((code, index) => {
        const placeholder = `{{CODEBLOCK${index}}}`;
        responseText = responseText.replace(placeholder, `<pre><code>${code}</code></pre>`);  
    });

    lists.forEach((listItem, index) => {
        const placeholder = `{{LIST${index}}}`;
        responseText = responseText.replace(placeholder, `<li>${listItem}</li>`);  
    });

    return responseText;
}

// Hàm thêm tin nhắn vào giao diện
function addMessage(type, content) {
    if (!content) return;  

    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    
    if (type === 'received') {
        messageElement.innerHTML = formatResponse(content);  
    } else {
        messageElement.innerHTML = `<strong></strong> ${content}`;
    }

    if (currentMode === 'studyWithAI') {
        messageArea.appendChild(messageElement);
        messageArea.scrollTop = messageArea.scrollHeight; // Cuộn xuống cuối
    } else if (currentMode === 'grading') {
        gradingResponseArea.appendChild(messageElement); // Thêm phản hồi vào khu vực chấm điểm
        gradingResponseArea.scrollTop = gradingResponseArea.scrollHeight; // Cuộn xuống cuối
    }
}

// Hàm hiển thị trạng thái "Đang xử lý..."
function setLoadingState(isLoading) {
    sendButton.disabled = isLoading;
    sendButton.classList.toggle('loading', isLoading);
    sendButton.textContent = isLoading ? "Đang xử lý..." : "Gửi";
}

// Sự kiện nhấn nút "Gửi"
sendButton.addEventListener('click', () => {
    const userText = userInput.value.trim();
    const file = uploadFile.files[0];
    const testCase = document.getElementById('testCase') ? document.getElementById('testCase').value : ''; // Lấy test case từ textarea

    if (!userText && !file && !testCase) {
        addMessage('received', "Vui lòng nhập câu hỏi hoặc tải lên file!");
        return;
    }

    setLoadingState(true);

    if (userText) {
        addMessage('sent', userText);
    } else if (file) {
        addMessage('sent', `Đã tải lên: ${file.name}`);
    }

    const formData = new FormData();
    if (file) formData.append('file', file);
    if (userText) formData.append('user_input', userText);
    if (testCase && currentMode === 'grading') formData.append('test_case', testCase); // Thêm test case nếu chế độ là grading
    formData.append('mode', currentMode); // Thêm chế độ vào form data

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.output) {
            addMessage('received', data.output);  
        } else {
            addMessage('received', 'Không nhận được phản hồi!');
        }
    })
    .catch(error => {
        console.error("Error:", error);
        addMessage('received', `Lỗi xử lý: ${error.message}`);
    })
    .finally(() => {
        setLoadingState(false);
        userInput.value = ""; // Xóa nội dung trong ô nhập liệu
        uploadFile.value = ""; // Reset ô chọn file
    });
});

// Sự kiện cho phép gửi tin nhắn bằng phím Enter và xuống dòng bằng Shift + Enter
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            userInput.value += '\n';
        } else {
            e.preventDefault();  
            sendButton.click();  
        }
    }
});

// Hàm chuyển giao diện
function switchMode(mode) {
    if (mode === 'studyWithAI') {
        studyWithAIInterface.style.display = 'block';
        gradingInterface.style.display = 'none';
        introInterface.style.display = 'none'; // Ẩn giới thiệu khi chuyển sang chế độ khác
        studyWithAIButton.classList.add('active');
        gradingButton.classList.remove('active');
        introButton.classList.remove('active');
    } else if (mode === 'grading') {
        studyWithAIInterface.style.display = 'none';
        gradingInterface.style.display = 'block';
        introInterface.style.display = 'none'; // Ẩn giới thiệu khi chuyển sang chế độ khác
        gradingButton.classList.add('active');
        studyWithAIButton.classList.remove('active');
        introButton.classList.remove('active');
    } else if (mode === 'intro') {
        studyWithAIInterface.style.display = 'none';
        gradingInterface.style.display = 'none';
        introInterface.style.display = 'block'; // Hiển thị giao diện giới thiệu
        introButton.classList.add('active');
        studyWithAIButton.classList.remove('active');
        gradingButton.classList.remove('active');
    }
}

// Lắng nghe sự kiện chọn chế độ
studyWithAIButton.addEventListener('click', () => {
    currentMode = 'studyWithAI';
    switchMode(currentMode);
});

gradingButton.addEventListener('click', () => {
    currentMode = 'grading';
    switchMode(currentMode);
});

introButton.addEventListener('click', () => {
    currentMode = 'intro';
    switchMode(currentMode);
});