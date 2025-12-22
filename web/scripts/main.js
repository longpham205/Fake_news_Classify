// scripts/main.js

import { predictNews, sendFeedback } from "./api.js";
import * as UI from "./ui.js";

/* =========================================
    BIẾN TOÀN CỤC (GLOBAL STATE)
   ========================================= */
let animationFrame;
let isCancelled = false;
let apiResult = null;
let currentRating = null; 
let isSubmitted = false; 

function goResultPage() {
    const isBackend = window.location.port === "8000";
    window.location.href = isBackend ? "/result" : "result.html";
}

function goHomePage() {
    const isBackend = window.location.port === "8000";
    window.location.href = isBackend ? "/" : "index.html";
}

document.addEventListener('DOMContentLoaded', () => {

    /* =========================================
        1. XỬ LÝ TRANG CHỦ (INDEX.HTML)
       ========================================= */
    const btnAnalyze = document.getElementById("btnAnalyze");

    if (btnAnalyze) {
        UI.initIndexEvents(() => {
            isCancelled = true;
            cancelAnimationFrame(animationFrame);
            console.log("Đã hủy quá trình nhận diện.");
        });

        btnAnalyze.onclick = async (e) => {
            e.preventDefault();


            isCancelled = false;
            apiResult = null; 
            isSubmitted = false;
            
            const contentInput = document.getElementById("content");
            const text = contentInput?.value.trim();

            if (!text) {
                UI.updateAiBubble("Bạn cần nhập nội dung chính trước nhé!", "red");
                contentInput?.focus();
                return;
            }

            const payload = {
                title: document.getElementById("title")?.value || "",
                author: document.getElementById("author")?.value || "",
                text: text,
                source: document.getElementById("source")?.value || "Khác",
                url: document.getElementById("link")?.value || "",
                date: document.getElementById("news-date")?.value || "",
                has_images: !!document.getElementById("has-image")?.checked,
                has_videos: !!document.getElementById("has-video")?.checked,
                num_shares: parseInt(document.getElementById("shares")?.value) || -1,
                num_comments: parseInt(document.getElementById("comments")?.value) || -1
            };

            UI.showLoading();
            let startTime = performance.now();

            function updateProgress() {
                if (isCancelled) return;
                const now = performance.now();
                const elapsed = now - startTime;
                let percent;

                if (!apiResult) {
                    percent = Math.floor((elapsed / 5000) * 90);
                    if (percent > 90) percent = 90;
                } else {
                    percent = UI.getCurrentPercent() + 5; 
                    if (percent > 100) percent = 100;
                }

                UI.updateProgressBar(percent);

                if (percent < 100) {
                    animationFrame = requestAnimationFrame(updateProgress);
                } else {
                    UI.updateAiBubble("Hoàn tất! Đang hiển thị kết quả...", "#2e7d32");
                    setTimeout(() => {
                        if (!isCancelled) goResultPage();
                    }, 800);
                }
            }
            animationFrame = requestAnimationFrame(updateProgress);

            try {
                const result = await predictNews(payload);
                if (isCancelled) return;
                localStorage.setItem("evaluation", JSON.stringify({
                    news_input: payload,
                    model_output: result
                }));
                apiResult = result;
            } catch (error) {
                if (!isCancelled) {
                    isCancelled = true; 
                    cancelAnimationFrame(animationFrame);
                    UI.hideLoading();
                    UI.updateAiBubble("Lỗi kết nối hệ thống. Vui lòng thử lại!", "red");
                }
            }
        };
    }

    /* =========================================
        2. XỬ LÝ TRANG KẾT QUẢ (RESULT.HTML)
       ========================================= */
    const btnBack = document.getElementById("btnBack");
    if (btnBack) {
        btnBack.addEventListener("click", goHomePage);
    }

    const resultTitle = document.getElementById("resTitle");
    if (resultTitle) {
        const rawData = localStorage.getItem("evaluation");

        if (!rawData) {
            console.warn("⚠ Không có dữ liệu đánh giá, quay về trang chủ");
            goHomePage();
            return;
        }
        else {
            const data = JSON.parse(rawData);
            UI.renderResult(data.model_output);

            const ratingButtons = document.querySelectorAll('.circle-btn');
            const btnSubmitFeedback = document.querySelector('.btn-submit-feedback');
            const feedbackArea = document.querySelector('.feedback-input-area textarea');
            const bubbleText = document.querySelector('.bubble-text');

            // A. Xử lý click chọn điểm
            ratingButtons.forEach((btn, index) => {
                btn.onclick = (e) => {
                    if (e) e.preventDefault();
                    if (isSubmitted) return; 

                    currentRating = index + 1;
                    UI.highlightFeedbackRating(currentRating);

                    const messages = {
                        1: "Xin lỗi vì đã đoán sai!<br> Phản hồi của bạn sẽ giúp mình sửa chữa sai lầm này!",
                        2: "Kết quả của mình khiến bạn phân vân sao!<br> Hãy gửi phản hồi để mình cải thiện nhé!",
                        3: "Cảm ơn đã tin tưởng đánh giá của mình!<br> Hi vọng mình giúp được bạn thêm nhiều lần tới!"
                    };

                    const color = {
                        1: "#8f0101ff",
                        2: "#02035cff",
                        3: "#023a05ff"
                    };

                    if (bubbleText) {
                        bubbleText.innerHTML = messages[currentRating];
                        bubbleText.style.color = color[currentRating]; 
                    }
                };
            });

            // B. Xử lý gửi Feedback
            if (btnSubmitFeedback) {
                btnSubmitFeedback.onclick = async (e) => {
                    // CHẶN HÀNH VI LOAD LẠI TRANG MẶC ĐỊNH
                    if (e) e.preventDefault();

                    if (isSubmitted) return;

                    if (currentRating === null) {
                        if (bubbleText) {
                            bubbleText.innerText = "Bạn hãy chọn điểm số để gửi đánh giá nha!";
                            bubbleText.style.color = "#d93025";
                        }
                        return;
                    }

                    // KHÓA TRẠNG THÁI NGAY LẬP TỨC
                    isSubmitted = true; 
                    btnSubmitFeedback.disabled = true;
                    btnSubmitFeedback.innerText = "ĐANG GỬI...";
                    
                    // Gọi hàm UI để khóa textarea và các nút tròn
                    UI.lockFeedbackFormUI(); 

                    // Định nghĩa text tương ứng với điểm số
                    const scoreTexts = { 1: "Sai hoàn toàn", 2: "Không chắc", 3: "Chính xác" };

                    // TẠO PAYLOAD ĐẦY ĐỦ ĐỊNH DẠNG
                    const fullFeedbackPayload = {
                        feedback_id: `fb_${new Date().toISOString().replace(/[-:T.Z]/g, "").slice(0, 14)}_${Math.floor(Math.random() * 1000)}`,
                        evaluation_id: data.model_output?.id || "eval_unknown",
                        created_at: new Date().toISOString(),

                        // Lấy lại dữ liệu đầu vào từ biến data
                        news_input: data.news_input || {},

                        // Lấy lại kết quả dự đoán của model từ biến data
                        model_output: data.model_output || {},

                        // Thông tin phản hồi của người dùng
                        user_feedback: {
                            score: currentRating,
                            score_text: scoreTexts[currentRating],
                            comment: feedbackArea?.value || ""
                        }
                    };

                    try {
                        await sendFeedback(fullFeedbackPayload);
                        if (bubbleText) {
                            bubbleText.innerHTML = "Cảm ơn bạn!<br>Đánh giá đã được ghi lại thành công.";
                            bubbleText.style.color = "black";
                        }
                        btnSubmitFeedback.innerText = "ĐÃ GỬI XONG";
                    } catch (err) {
                        // Nếu lỗi, mở lại cho phép gửi lại
                        isSubmitted = false;
                        btnSubmitFeedback.disabled = false;
                        btnSubmitFeedback.innerText = "GỬI LẠI";
                        if (bubbleText) {
                            bubbleText.innerText = "Lỗi khi gửi, vui lòng thử lại!";
                            bubbleText.style.color = "red";
                        }
                    }
                };
            }
        }
    }
});
