// script/ui.js

/* =========================================
   HELPER: Lấy Element an toàn
   ========================================= */
const getEl = (id) => document.getElementById(id);
const getElQuery = (selector) => document.querySelector(selector);
const getAllQuery = (selector) => document.querySelectorAll(selector);

/* =========================================
   1. QUẢN LÝ TRẠNG THÁI LOADING (Index Page)
   ========================================= */

export function showLoading() {
    const btnAnalyze = getEl("btnAnalyze");
    const btnReset = getEl("btnReset");
    const loadingArea = getEl("loadingArea");
    const circleBorder = getEl("circleBorder");

    if (btnAnalyze) btnAnalyze.style.display = 'none';
    if (btnReset) btnReset.style.display = 'none';
    if (loadingArea) {
        loadingArea.classList.remove("hidden");
        loadingArea.style.display = "flex";
    }
    if (circleBorder) circleBorder.classList.add("spinning");
    updateAiBubble("Mình đang nhận diện\nBạn chờ chút nhé!");
}

export function updateProgressBar(percent) {
    const progressText = getEl("progressText");
    const progressBar = getEl("progressBar");
    if (progressText) progressText.innerText = percent + "%";
    if (progressBar) progressBar.style.width = percent + "%";
}

export function hideLoading() {
    const loadingArea = getEl("loadingArea");
    const btnAnalyze = getEl("btnAnalyze");
    const btnReset = getEl("btnReset");
    const circleBorder = getEl("circleBorder");

    if (loadingArea) {
        loadingArea.classList.add("hidden");
        loadingArea.style.display = "none";
    }
    if (btnAnalyze) btnAnalyze.style.display = "inline-block";
    if (btnReset) btnReset.style.display = "inline-block";
    if (circleBorder) circleBorder.classList.remove("spinning");
    updateProgressBar(0);
}

export function getCurrentPercent() {
    const progressText = getEl("progressText");
    if (progressText) {
        return parseInt(progressText.innerText) || 0;
    }
    return 0;
}

/* =========================================
   2. QUẢN LÝ THÔNG BÁO AI (Bubble Chat)
   ========================================= */

export function updateAiBubble(text, color = "black") {
    // Ưu tiên tìm ID bubble-text (Result) rồi mới đến aiBubble (Index)
    const bubble = getEl("bubble-text") || getEl("aiBubble");
    if (bubble) {
        bubble.innerText = text;
        bubble.style.color = color;
    }
}

/* =========================================
   3. QUẢN LÝ FORM INPUT (Index Page)
   ========================================= */

export function resetInputFields() {
    getAllQuery('input[type="text"], input[type="date"], input[type="number"], textarea').forEach(el => el.value = '');
    getAllQuery('input[type="checkbox"]').forEach(el => el.checked = false);
    const source = getEl('source');
    if (source) source.selectedIndex = 0;
    updateAiBubble("Đã làm mới dữ liệu!\nBạn nhập thông tin khác đi.");
}

export function initIndexEvents(cancelCallback) {
    // Xử lý nút X (Xóa từng ô)
    getAllQuery('.clear-btn').forEach(button => {
        button.onclick = function() {
            const inputField = this.parentElement.querySelector('input, textarea');
            if (inputField) {
                inputField.value = '';
                inputField.focus();
            }
        };
    });

    // Xử lý nút Nhập lại
    const btnReset = getEl('btnReset');
    if (btnReset) {
        btnReset.onclick = () => resetInputFields();
    }

    // Xử lý nút Hủy khi đang loading
    const btnCancel = getEl('btnCancel');
    if (btnCancel) {
        btnCancel.onclick = () => {
            if (cancelCallback) cancelCallback();
            hideLoading();
            updateAiBubble("Đã huỷ quá trình nhận diện.");
        };
    }
}

/* =========================================
   4. HIỂN THỊ KẾT QUẢ (Result Page)
   ========================================= */

export function renderResult(data) {
    if (!data) return;

    const resTitle = getEl("resTitle");
    const resProb = getEl("resProb");
    const resLevel = getEl("resLevel");
    const msgHeader = getEl("msgHeader");
    const msgBody = getEl("msgBody");
    const resLevelLabel = getEl("resLevelLabel");

    const colorClass = data.result?.ui_state?.color_class || "text-gray";

    const resetColor = (el) => { 
        if(el) el.className = el.className.replace(/text-\w+/g, "").trim(); 
    };

    if (resTitle) {
        resTitle.innerHTML = data.result.final_label_text;
        resetColor(resTitle);
        resTitle.classList.add(colorClass);
    }

    if (resProb) {
        resProb.innerText = Math.round(data.result.confidence * 100) + "%";
        resProb.className = "percent";
        resProb.classList.add(colorClass);
    }

    if (resLevel) {
        const levelMap = {
            "HIGH": "CAO",
            "MEDIUM": "TRUNG BÌNH",
            "LOW": "THẤP",
            "UNKNOWN": "KHÔNG XÁC ĐỊNH"
        };

        const rawLevel = (data.result.confidence_level || "UNKNOWN").toUpperCase();

        resLevel.innerText = levelMap[rawLevel] || rawLevel;

        resetColor(resLevel);
        resLevel.classList.add(colorClass);
        
        if (resLevelLabel) {
            resetColor(resLevelLabel);
            resLevelLabel.classList.add(colorClass);
        }
    }

    if (msgHeader) {
        msgHeader.innerText = data.result.ui_state.border_class;
        msgHeader.className = "content-header";
        msgHeader.classList.add(colorClass);
    }

    if (msgBody) {
        msgBody.innerHTML = ""; 
        if (data.result.confidence_level === "medium" && data.top_predictions) {
            const ul = document.createElement("ul");
            data.top_predictions.forEach(p => {
                const li = document.createElement("li");
                li.innerText = `${p.label}: ${Math.round(p.probability * 100)}%`;
                ul.appendChild(li);
            });
            msgBody.appendChild(ul);
        } else if (data.reasons && data.reasons.summary) {
            data.reasons.summary.forEach(r => {
                const p = document.createElement("p");
                p.innerText = "• " + r;
                msgBody.appendChild(p);
            });
        } else {
             msgBody.innerText = data.result.ui_state.body_msg || "Không có thông tin chi tiết.";
        }
    }
    
    // Reset form feedback khi có kết quả mới
    resetFeedbackFormUI();
}

/* =========================================
   5. QUẢN LÝ FORM FEEDBACK (Result Page)
   ========================================= */

export function highlightFeedbackRating(selectedIndex) {
    const ratingButtons = getAllQuery('.circle-btn');
    ratingButtons.forEach((btn, index) => {
        if (index + 1 === selectedIndex) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

export function lockFeedbackFormUI() {
    const btnSubmitFeedback = document.querySelector('.btn-submit-feedback');
    const feedbackArea = document.querySelector('.feedback-input-area textarea');
    const ratingButtons = document.querySelectorAll('.circle-btn');

    if (btnSubmitFeedback) {
        btnSubmitFeedback.disabled = true;
        btnSubmitFeedback.innerText = "ĐÃ GỬI";
        btnSubmitFeedback.style.backgroundColor = "#ccc";
        btnSubmitFeedback.style.pointerEvents = "none"; // Chặn mọi cú click sau này
    }

    if (feedbackArea) {
        feedbackArea.disabled = true;
        feedbackArea.style.opacity = "0.6";
        feedbackArea.placeholder = "Đánh giá đã được ghi lại.";
    }

    ratingButtons.forEach(btn => {
        btn.style.pointerEvents = "none"; // Khóa không cho chọn lại điểm
        btn.style.opacity = "0.5";
        btn.classList.remove('active'); // Hoặc giữ lại nút đang chọn tùy ý bạn
    });
}

export function resetFeedbackFormUI() {
    const btnSubmitFeedback = getElQuery('.btn-submit-feedback');
    const feedbackArea = getElQuery('.feedback-input-area textarea');
    const ratingButtons = getAllQuery('.circle-btn');

    if (btnSubmitFeedback) {
        btnSubmitFeedback.disabled = false;
        btnSubmitFeedback.innerText = "GỬI ĐÁNH GIÁ";
        btnSubmitFeedback.style.background = ""; 
        btnSubmitFeedback.style.cursor = "pointer";
        btnSubmitFeedback.style.pointerEvents = "auto";
    }

    if (feedbackArea) {
        feedbackArea.value = "";
        feedbackArea.disabled = false;
        feedbackArea.style.opacity = "1";
        feedbackArea.style.cursor = "auto";
        feedbackArea.placeholder = "Nhập ý kiến của bạn (tùy chọn)...";
    }

    ratingButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.style.cursor = "pointer";
        btn.style.opacity = "1";
        btn.style.pointerEvents = "auto";
    });

    updateAiBubble("Bạn thấy kết quả này thế nào?\nHãy đánh giá giúp mình nhé!", "black");
}
