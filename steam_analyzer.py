import os
import re

from dotenv import load_dotenv
from openai import OpenAI

# .env 로드 및 OpenAI 클라이언트 생성
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _call_gpt(system_prompt: str, user_prompt: str, max_tokens: int = 400) -> str:
    """
    공통 GPT 호출 함수 - chat.completions 기반
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def analyze_review_deep(review_text: str) -> dict:
    """
    2차 심층 분석: 하나의 리뷰를 GPT에게 보내서 정리된 분석을 받는다.
    반환 형식:
    {
        "final_sentiment": "긍정적 / 부정적 / 중립적 / 분석 불가",
        "positive_points": "...",
        "negative_points": "...",
        "suggestion": "..."
    }
    """

    system_prompt = (
        "당신은 게임 리뷰의 뉘앙스를 분석하는 전문 분석가입니다. "
        "사용자 리뷰를 읽고 감정과 요인을 한국어로 정리해 주세요."
    )

    user_prompt = f"""
다음 Steam 리뷰를 읽고 아래 형식 그대로 한국어로 답변하세요.

--- 리뷰 원문 ---
{review_text}
----------------

[출력 형식]
1. 최종 감정: 긍정적 / 부정적 / 중립적 중 하나만 작성
2. 긍정적 요인: 사용자가 긍정적으로 평가하는 핵심 이유 1~2가지 요약
3. 부정적 요인: 사용자가 부정적으로 평가하는 핵심 이유 1~2가지 요약
4. 개발팀을 위한 제언: 이 리뷰를 바탕으로 개발팀이 참고할 만한 구체적인 제안 1문장
"""

    try:
        text = _call_gpt(system_prompt, user_prompt, max_tokens=400)

        analysis = {}

        # 1. 최종 감정
        m1 = re.search(r"1\.\s*최종 감정:\s*(.*)", text)
        analysis["final_sentiment"] = m1.group(1).strip() if m1 else "분석 불가"

        # 2. 긍정적 요인
        m2 = re.search(r"2\.\s*긍정적 요인:\s*(.*)", text)
        analysis["positive_points"] = m2.group(1).strip() if m2 else "없음"

        # 3. 부정적 요인
        m3 = re.search(r"3\.\s*부정적 요인:\s*(.*)", text)
        analysis["negative_points"] = m3.group(1).strip() if m3 else "없음"

        # 4. 제언
        m4 = re.search(r"4\.\s*개발팀을 위한 제언:\s*(.*)", text)
        analysis["suggestion"] = m4.group(1).strip() if m4 else "없음"

        return analysis

    except Exception as e:
        print(f"GPT 심층 분석 오류: {e}")
        return {
            "final_sentiment": "분석 실패",
            "positive_points": "오류",
            "negative_points": "오류",
            "suggestion": "오류",
        }


def get_overall_insights_from_gpt(analyzed_df, keyword: str) -> str:
    """
    (이름은 기존 app.py와 맞추기 위해 유지)
    GPT를 사용해서 종합 인사이트를 생성한다.
    """
    try:
        positive_reviews = analyzed_df[
            analyzed_df["sentiment_label"] == "POSITIVE"
        ].shape[0]
        negative_reviews = analyzed_df[
            analyzed_df["sentiment_label"] == "NEGATIVE"
        ].shape[0]
        total_reviews = analyzed_df.shape[0]
    except Exception as e:
        print(f"종합 인사이트용 통계 계산 오류: {e}")
        return "⚠️ 분석 데이터 통계를 계산하는 중 오류가 발생했습니다."

    keyword_display = keyword.strip() if keyword and keyword.strip() else "전체"

    summary = (
        f"'{keyword_display}' 키워드 관련 리뷰 {total_reviews}개 분석 결과:\n"
        f"- 긍정적 반응: {positive_reviews}개\n"
        f"- 부정적 반응: {negative_reviews}개"
    )

    system_prompt = (
        "당신은 게임 개발 디렉터입니다. "
        "주어진 감정 분석 요약을 바탕으로 업데이트/밸런싱 방향에 대한 인사이트를 제시하세요."
    )

    user_prompt = f"""
다음은 특정 키워드에 대한 유저 리뷰 감정 분석 요약입니다.

--- 분석 요약 ---
{summary}

[작성 규칙]
- 장점/강점: 어떤 부분이 잘 작동하고 있는지, 어떻게 더 강화할 수 있는지
- 문제점/리스크: 어떤 부분에서 유저 불만이 집중되는지, 왜 그런지
- 향후 방향: 패치/이벤트/밸런스 조정 등으로 어떤 액션을 취하면 좋을지
- 전체 분량은 3~6문장 정도의 한국어 문단으로 작성
"""

    try:
        text = _call_gpt(system_prompt, user_prompt, max_tokens=400)
        return text

    except Exception as e:
        print(f"GPT 종합 인사이트 오류: {e}")
        return (
            "⚠️ GPT API 호출 중 오류가 발생하여 종합 인사이트를 생성할 수 없습니다.\n"
            "OPENAI_API_KEY 설정과 네트워크 상태를 확인한 뒤 다시 시도해주세요."
        )

