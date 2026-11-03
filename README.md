# steam_rv_ai
# 🎮 Steam 게임 리뷰 감정분석 및 인사이트 제공 시스템

Steam 게임 리뷰를 수집하고 감정분석 모델과 GPT를 활용하여  
**장르별 유저 반응, 주요 키워드, 긍·부정 요인 및 게임 개선 인사이트**를 제공하는 Streamlit 기반 웹 애플리케이션입니다.

---

## 📌 프로젝트 개요

게임 개발과 운영 과정에서는 Steam과 같은 플랫폼에 축적되는 대량의 유저 리뷰를 빠르게 분석하고, 실제 개발 및 패치 방향에 활용하는 과정이 중요합니다.

본 프로젝트는 Steam 리뷰 데이터를 자동으로 수집한 뒤 감정분석 모델을 적용하여 긍정·부정 반응을 분석하고, GPT를 통해 리뷰 내용을 종합하여 **개발팀이 참고할 수 있는 인사이트를 제공하는 시스템**을 구현하는 것을 목표로 합니다.

---

## 🔄 전체 프로세스

```text
Steam Review API
      ↓
장르별 게임 리뷰 수집
      ↓
키워드 필터링 및 데이터 정제
      ↓
DistilBERT 기반 감정분석
      ↓
긍정 / 부정 리뷰 분류
      ↓
애매한 리뷰 GPT 심층분석
      ↓
GPT 기반 종합 인사이트 생성
      ↓
Streamlit 대시보드 시각화
```

---

## ✨ 주요 기능

### 1. Steam 리뷰 자동 수집

Steam Review API를 활용하여 장르별 대표 게임의 리뷰를 수집합니다.

지원 장르:

- Casual
- FPS
- Horror
- Indie
- RPG

리뷰 수집 기준:

- Most Helpful
- Most Recent
- Funny

각 장르에 포함된 게임 중 일부를 선택하여 최근 리뷰 데이터를 수집합니다.

---

### 2. 키워드 기반 리뷰 필터링

사용자가 특정 키워드를 입력하면 해당 키워드가 포함된 리뷰만 분석할 수 있습니다.

예:

```text
patch
bug
balance
story
performance
```

키워드를 입력하지 않을 경우 전체 리뷰를 대상으로 분석합니다.

---

### 3. 감정분석 모델 적용

Hugging Face Transformers 기반 감정분석 모델을 이용하여 리뷰를

```text
POSITIVE
NEGATIVE
```

로 분류합니다.

장르별 파인튜닝 모델이 존재하는 경우 해당 모델을 우선 사용하며, 모델을 찾을 수 없는 경우 기본 DistilBERT 감정분석 모델을 사용합니다.

```python
distilbert-base-uncased-finetuned-sst-2-english
```

---

### 4. GPT 기반 리뷰 심층분석

1차 감정분석 결과 중 모델 판단이 모호한 리뷰를 선별하여 GPT를 이용해 추가 분석합니다.

분석 항목:

- 최종 감정
- 긍정적 요인
- 부정적 요인
- 개발팀을 위한 개선 제안

예시:

```text
최종 감정: 부정적

긍정적 요인:
전투 시스템과 그래픽에 대한 평가는 긍정적

부정적 요인:
최근 패치 이후 밸런스와 성능 문제 발생

개발팀 제언:
최근 패치에서 변경된 밸런스와 성능 최적화를 우선적으로 점검할 필요가 있음
```

---

### 5. GPT 기반 종합 인사이트

전체 감정분석 결과를 GPT에 전달하여 게임 개발 관점의 종합 인사이트를 생성합니다.

주요 분석 항목:

- 장점 및 강점
- 유저 불만이 집중되는 부분
- 잠재적 리스크
- 패치 및 밸런스 개선 방향

---

### 6. Streamlit 데이터 시각화

분석 결과를 Streamlit 기반 대시보드에서 확인할 수 있습니다.

제공 정보:

- 분석 장르
- 분석 리뷰 수
- 포함된 게임 수
- 긍정 / 부정 리뷰 분포
- 주요 키워드 Top 20
- GPT 종합 인사이트
- 개별 리뷰 심층분석 결과

---

## 🛠 Tech Stack

### Language
- Python

### Data
- Pandas
- Steam Review API
- Requests

### AI / NLP
- Hugging Face Transformers
- DistilBERT
- OpenAI API

### Visualization
- Streamlit
- Plotly

---

## 📁 Project Structure

```text
project/
│
├── app.py
│   └── Steam 리뷰 수집
│       감정분석 모델 적용
│       키워드 분석
│       Streamlit UI
│
├── steam_analyzer.py
│   └── GPT 리뷰 심층분석
│       GPT 종합 인사이트 생성
│
├── .env
│   └── OPENAI_API_KEY
│
└── models/
    ├── casual_model/
    ├── fps_model/
    ├── horror_model/
    ├── indie_model/
    └── rpg_model/
```

> `models/` 폴더가 존재하지 않을 경우 기본 DistilBERT 모델을 사용합니다.

---

## ⚙️ 실행 방법

### 1. Repository Clone

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. 라이브러리 설치

```bash
pip install streamlit pandas requests plotly transformers torch python-dotenv openai
```

### 3. OpenAI API Key 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

### 4. Streamlit 실행

```bash
streamlit run app.py
```

---

## 🧩 주요 코드 구성

### `app.py`

전체 애플리케이션 흐름을 담당합니다.

```text
Steam 리뷰 수집
→ 키워드 필터링
→ 감정분석
→ GPT 심층분석
→ 키워드 추출
→ 결과 시각화
```

### `steam_analyzer.py`

OpenAI API를 활용한 자연어 분석을 담당합니다.

```text
개별 리뷰 심층분석
→ 긍정·부정 요인 추출
→ 개발팀 제언 생성

전체 감정분석 결과
→ GPT 종합 인사이트 생성
```

---

## ⚠️ 현재 한계

- 게임별 리뷰 수가 많을 경우 API 호출 및 모델 추론 시간이 길어질 수 있습니다.
- 기본 감정분석 모델은 영어 리뷰를 중심으로 동작합니다.
- 장르별 파인튜닝 모델이 없는 경우 기본 DistilBERT 모델로 fallback됩니다.
- 현재 키워드 추출은 빈도 기반 방식으로 문맥적 중요도를 완전히 반영하지 못합니다.
- LLM 분석 결과는 생성형 AI의 특성상 일관성이 달라질 수 있습니다.

---

## 🚀 향후 개선 방향

- 장르별 감정분석 모델 고도화
- 다국어 리뷰 지원
- 키워드 추출 방식 개선
- 리뷰 수집 및 모델 추론 속도 최적화
- 게임별 시계열 감정 변화 분석
- 패치 전·후 리뷰 감정 비교 기능 추가
- LLM 기반 개발 인사이트 품질 개선

---

## 👤 Contribution

- Steam API 기반 리뷰 수집 파이프라인 구축
- 감정분석 모델과 리뷰 데이터 연동
- 감정분석 결과와 GPT API를 연결한 인사이트 생성 흐름 구현
- Steam 리뷰 수집 → 감정분석 → LLM 인사이트 생성으로 이어지는 데이터·AI 파이프라인 설계
