# 🤖 AI Integration Setup Guide

## Tại sao cần AI API Keys?

Hệ thống A2A hiện tại sử dụng **logic đơn giản** để phân tích dự án. Để có **AI thông minh hơn**, bạn cần tích hợp các AI service:

### 🧠 AI Capabilities khi có API Keys:

- **Phân tích dự án thông minh**: Hiểu sâu yêu cầu, đánh giá độ phức tạp chính xác
- **Ước tính thời gian AI**: Dự đoán thời gian dựa trên dữ liệu thực tế
- **Phân tích kỹ năng**: Xác định chính xác kỹ năng cần thiết
- **Quản lý rủi ro**: Dự đoán và cảnh báo rủi ro tiềm ẩn
- **Tối ưu hóa team**: Gợi ý cấu trúc team tối ưu

## 🔑 Cách lấy API Keys:

### 1. OpenAI API Key (Khuyến nghị)

```bash
# Truy cập: https://platform.openai.com/api-keys
# Tạo account -> Generate API Key
# Copy key vào .env:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
```

### 2. Google AI API Key

```bash
# Truy cập: https://makersuite.google.com/app/apikey
# Tạo API key cho Gemini
# Copy vào .env:
GOOGLE_AI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxx
```

### 3. Anthropic Claude (Tùy chọn)

```bash
# Truy cập: https://console.anthropic.com/
# Tạo API key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxx
```

## ⚙️ Configuration trong .env:

```env
# Bật AI analysis
ENABLE_AI_ANALYSIS=true
AI_PROVIDER=openai

# OpenAI Settings (nếu chọn OpenAI)
OPENAI_API_KEY=your-real-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
```

## 🚀 So sánh: Trước và Sau khi có AI

### ❌ TRƯỚC (Logic đơn giản):

```
Mission: "Create e-commerce platform"
Analysis: "Complexity: Medium, Duration: 8 weeks"
```

### ✅ SAU (AI-powered):

```
Mission: "Create e-commerce platform"
AI Analysis:
- Complexity: COMPLEX (detected payment gateway, inventory, analytics)
- Duration: 12 weeks (realistic based on e-commerce projects)
- Technologies: React, Node.js, PostgreSQL, Redis, Docker
- Team Size: 5 members (frontend, backend, devops, QA, PM)
- Risk Factors: Payment security, scalability, data privacy
- Budget: $150,000 - $200,000
```

## 🧪 Test AI Integration:

1. **Thêm API key vào .env**
2. **Restart agents**
3. **Test thử mission phức tạp**:

```bash
python main.py
```

Mission test:

```
"Create a real-time collaborative document editing platform like Google Docs,
with video conferencing, AI-powered writing assistance, and enterprise SSO integration.
The system needs to handle 10,000 concurrent users and be GDPR compliant."
```

## 💰 Chi phí API:

- **OpenAI GPT-4**: ~$0.03/1K tokens (khoảng $0.1-0.5 per analysis)
- **Google Gemini**: ~$0.001/1K tokens (rẻ hơn nhiều)
- **Claude**: ~$0.015/1K tokens

## 🔧 Troubleshooting:

### Lỗi API Key không hợp lệ:

```bash
# Check .env file:
cat .env | grep API_KEY

# Restart agents sau khi update .env
```

### AI analysis bị lỗi:

- Hệ thống sẽ tự động fallback về logic đơn giản
- Check logs để xem lỗi cụ thể

### Rate limiting:

- Giảm `OPENAI_MAX_TOKENS` xuống 2000
- Tăng delay giữa các request

## 🎯 Kết luận:

- **Không có AI**: Hệ thống hoạt động với logic cơ bản ✅
- **Có AI**: Phân tích thông minh, chính xác hơn 🚀
- **Chi phí**: ~$1-5/ngày cho development, tùy usage

**Khuyến nghị**: Bắt đầu với Google AI (rẻ) hoặc OpenAI (tốt nhất) để thấy sự khác biệt!
