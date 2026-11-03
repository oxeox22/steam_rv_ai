import os
import re
import requests
import random
from datetime import datetime, timedelta
from collections import Counter
from functools import lru_cache

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from transformers import pipeline

# Gpt 관련 함수 활용
from steam_analyzer import (
    analyze_review_deep,
    get_overall_insights_from_gpt,
)


load_dotenv()

# ==========================
# 1. 기본 설정
# ==========================

st.set_page_config(
    page_title="🎮 장르별 Steam 리뷰 인사이트 분석기",
    layout="wide",
)

st.title("🎮 장르별 Steam 리뷰 인사이트 분석기")
st.caption(
    "장르를 선택하면 해당 장르의 대표 게임 리뷰들을 수집하고, "
    "장르 특화 감정분석 + Gemini 심층 분석으로 인사이트를 제공합니다."
)

# --- 장르 목록 ---
GENRES = ["Casual", "FPS", "Horror", "Indie", "RPG"]

# --- 장르별 대표 게임 목록 (실제 App ID로 교체해서 사용) ---
GENRE_GAME_LIST = {
    "Casual": [
        {"name": "Stardew Valley", "app_id": 413150},
        {"name": "Among Us", "app_id": 945360},
        {"name": "Bloons TD 6", "app_id": 960090},
        {"name": "Vampire Survivors", "app_id": 1794680},
        {"name": "Balatro", "app_id": 2379780},
        {"name": "Plants vs. Zombies GOTY Edition", "app_id": 3590},
        {"name": "Brawlhalla", "app_id": 291550},
        {"name": "Brotato", "app_id": 1942280},
        {"name": "The Sims 4", "app_id": 1222670},
        {"name": "WEBFISHING", "app_id": 3146520},
        {"name": "Touhou Mystia's Izakaya", "app_id": 1584090},
        {"name": "Tabletop Simulator", "app_id": 286160},
        {"name": "Bongo Cat", "app_id": 3419430},
        {"name": "Peggle Deluxe", "app_id": 3480},
        {"name": "Muse Dash", "app_id": 774171},
    ],
    "FPS": [
        {"name": "Counter-Strike 2", "app_id": 730},
        {"name": "Garry's Mod", "app_id": 4000},
        {"name": "Team Fortress 2", "app_id": 440},
        {"name": "Rainbow Six Siege X", "app_id": 359550},
        {"name": "Rust", "app_id": 252490},
        {"name": "Deep Rock Galactic", "app_id": 548430},
        {"name": "PAYDAY2", "app_id": 218620},
        {"name": "Unturned", "app_id": 304930},
        {"name": "Half-Life2", "app_id": 220},
        {"name": "ULTRAKILL", "app_id": 1229490},
        {"name": "Titanfall® 2", "app_id": 1237970},
        {"name": "Arma3", "app_id": 107410},
        {"name": "Fallout 4", "app_id": 377160},
        {"name": "Half-Life: Alyx", "app_id": 546560},
        {"name": "DOOM", "app_id": 379720},
    ],
    "Horror": [
        {"name": "Left 4 Dead 2", "app_id": 550},
        {"name": "The Forest", "app_id": 242760},
        {"name": "Dying Light", "app_id": 239140},
        {"name": "Subnautica", "app_id": 264710},
        {"name": "R.E.P.O.", "app_id": 3241660},
        {"name": "Biohazard RE:4 (Resident Evil 4 Remake)", "app_id": 2050650},
        {"name": "Sons of the Forest", "app_id": 1326470},
        {"name": "Resident Evil Village", "app_id": 1196590},
        {"name": "Resident Evil 2 (Remake)", "app_id": 883710},
        {"name": "Fear & Hunger 2: Termina", "app_id": 2171440},
        {"name": "Outlast", "app_id": 238320},
        {"name": "MiSide", "app_id": 2527500},
        {"name": "Inscryption", "app_id": 1092790},
        {"name": "Buckshot Roulette", "app_id": 2835570},
        {"name": "Doki Doki Literature Club!", "app_id": 698780},
    ],
    "Indie": [
        {"name": "Hollow Knight", "app_id": 367520},
        {"name": "The Binding of Isaac: Rebirth", "app_id": 250900},
        {"name": "Hades", "app_id": 1145360},
        {"name": "Undertale", "app_id": 391540},
        {"name": "Palworld", "app_id": 1623730},
        {"name": "It Takes Two Friend's Pass", "app_id": 2995920},
        {"name": "Cuphead", "app_id": 268910},
        {"name": "Hollow Knight: Silksong", "app_id": 1030300},
        {"name": "Papers, Please", "app_id": 239030},
        {"name": "Totally Accurate Battle Simulator", "app_id": 508440},
        {"name": "Celeste", "app_id": 504230},
        {"name": "OMORI", "app_id": 1150690},
        {"name": "Hotline Miami", "app_id": 219150},
        {"name": "Don't Starve", "app_id": 219740},
        {"name": "Cookie Clicker", "app_id": 1454400},
    ],
    "RPG": [
        {"name": "Dota 2", "app_id": 570},
        {"name": "Where Winds Meet", "app_id": 3564740},
        {"name": "Path of Exile", "app_id": 238960},
        {"name": "Baldur's Gate 3", "app_id": 1086940},
        {"name": "Warframe", "app_id": 230410},
        {"name": "Enshrouded", "app_id": 1203620},
        {"name": "The Elder Scrolls V: Skyrim Special Edition", "app_id": 489830},
        {"name": "Terraria", "app_id": 105600},
        {"name": "Project Zomboid", "app_id": 108600},
        {"name": "Cyberpunk 2077", "app_id": 1091500},
        {"name": "INAZUMA ELEVEN: Victory Road", "app_id": 2799860},
        {"name": "Limbus Company", "app_id": 1973530},
        {"name": "ELDEN RING", "app_id": 1245620},
        {"name": "Black Desert", "app_id": 582660},
        {"name": "Mount & Blade II: Bannerlord", "app_id": 261550},
    ],
}

# --- 장르별 커스텀 모델 경로 ---
# (이미 학습해둔 폴더 이름을 여기에 매핑)
GENRE_MODEL_PATHS = {
    "Casual": "./models/casual_model",
    "FPS": "./models/fps_model",
    "Horror": "./models/horror_model",
    "Indie": "./models/casual_model",       # 나중에 Indie 모델로 수정
    "RPG": "./models/rpg_model",
}

# 커스텀 모델 로드 실패 시 사용할 기본 모델
BASE_FALLBACK_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"  # :contentReference[oaicite:2]{index=2}

# 리뷰 기준 → Steam API filter 파라미터 매핑
FILTER_LABEL_TO_PARAM = {
    "Most Helpful": "toprated",  # review_extraction.py 기준 :contentReference[oaicite:3]{index=3}
    "Most Recent": "mostrecent",
    "Funny": "funny",            # Steam 리뷰 API에서 지원
}

# 수집 범위 설정
DAYS_BACK = 365            # 최근 1년
MAX_REVIEWS_PER_GAME = 200 # 게임 하나당 최대 리뷰 수

# 키워드 추출용 간단 영어 stopword
STOPWORDS = {
    "the", "and", "you", "your", "for", "with", "this", "that", "have", "has",
    "but", "not", "are", "was", "were", "they", "them", "their", "it's",
    "game", "games", "play", "played", "playing", "will", "can", "just",
    "about", "really", "very", "there", "also", "been", "what", "when",
}

# ==========================
# 2. 모델 로딩 & 분석 함수
# ==========================

@lru_cache(maxsize=None)
def get_sentiment_pipeline(genre: str):
    """
    장르별 커스텀 감정분석 파이프라인 로드.
    실패하면 기본 distilbert 모델로 fallback.
    """
    model_dir = GENRE_MODEL_PATHS.get(genre, GENRE_MODEL_PATHS["RPG"])
    abs_path = os.path.abspath(model_dir)

    try:
        if os.path.exists(abs_path):
            print(f"✅ [{genre}] 커스텀 모델 로드: {abs_path}")
            return pipeline("sentiment-analysis", model=abs_path)
        else:
            raise FileNotFoundError(f"모델 폴더 없음: {abs_path}")
    except Exception as e:
        print(f"⚠️ [{genre}] 커스텀 모델 로드 실패 ({e}), 기본 모델 사용")
        return pipeline("sentiment-analysis", model=BASE_FALLBACK_MODEL)


def run_fast_sentiment_analysis(df: pd.DataFrame, genre: str) -> pd.DataFrame:
    """
    1차 감정 분석: 선택한 장르의 모델로 전체 리뷰 긍·부정/점수 계산.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["review"] = df["review"].fillna("").astype(str)
    df = df[df["review"].str.strip() != ""]
    if df.empty:
        return df

    analyzer = get_sentiment_pipeline(genre)

    try:
        results = analyzer(df["review"].tolist(), truncation=True)

        raw_labels = [r["label"] for r in results]
        scores = [r["score"] for r in results]

        # 🔹 여기서 라벨 통일
        normalized_labels = []
        for lab in raw_labels:
            if lab in ("LABEL_1", "POSITIVE"):
                normalized_labels.append("POSITIVE")
            elif lab in ("LABEL_0", "NEGATIVE"):
                normalized_labels.append("NEGATIVE")
            else:
                normalized_labels.append(lab)  # 혹시 모를 기타 값

        df["sentiment_label"] = normalized_labels
        df["sentiment_score"] = scores

    except Exception as e:
        print(f"감정 분석 오류: {e}")
        df["sentiment_label"] = "ERROR"
        df["sentiment_score"] = 0.0

    return df


def pick_and_run_deep_analysis(
    df: pd.DataFrame,
    ambiguity_threshold: float,
    max_deep_dives: int,
) -> pd.DataFrame:
    """
    1차 모델 점수가 0.5 주변(애매한)인 리뷰 중에서
    'votes_up'이 높은 순으로 최대 max_deep_dives개를 골라
    Gemini로 심층 분석 수행.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # 심층 분석용 컬럼 미리 생성
    deep_cols = ["final_sentiment", "positive_points", "negative_points", "suggestion"]
    for c in deep_cols:
        if c not in df.columns:
            df[c] = None

    lower = 0.5 - ambiguity_threshold
    upper = 0.5 + ambiguity_threshold

    ambiguous = df[
        (df["sentiment_score"] >= lower)
        & (df["sentiment_score"] <= upper)
    ].copy()

    if ambiguous.empty or max_deep_dives <= 0:
        return df

    # 도움이 많이 된(또는 funny) 리뷰 위주로 심층 분석 대상 선정
    if "votes_up" in ambiguous.columns:
        ambiguous = ambiguous.sort_values("votes_up", ascending=False)

    ambiguous = ambiguous.head(max_deep_dives)

    for idx, row in ambiguous.iterrows():
        deep_result = analyze_review_deep(row["review"])  # Gemini 호출

        # 결과 저장
        for col_name in deep_cols:
            df.at[idx, col_name] = deep_result.get(col_name)

        # 최종 감정을 기준으로 라벨 정제
        final_sent = deep_result.get("final_sentiment")
        if final_sent == "긍정적":
            df.at[idx, "sentiment_label"] = "POSITIVE"
        elif final_sent == "부정적":
            df.at[idx, "sentiment_label"] = "NEGATIVE"
        else:
            df.at[idx, "sentiment_label"] = "NEUTRAL"

    return df


# ==========================
# 3. 데이터 수집 / 키워드
# ==========================

def fetch_reviews_for_game(
    app_id: int,
    filter_param: str,
    days_back: int = DAYS_BACK,
    max_reviews: int = MAX_REVIEWS_PER_GAME,
) -> pd.DataFrame:
    """
    단일 게임(app_id)에 대해 Steam 리뷰 API로 리뷰 수집.
    review_extraction.py 구조를 참고해 구현. :contentReference[oaicite:4]{index=4}
    """
    now_utc = datetime.utcnow()
    start_dt = now_utc - timedelta(days=days_back)

    start_ts = int(start_dt.timestamp())
    end_ts = int(now_utc.timestamp())

    base_url = f"https://store.steampowered.com/appreviews/{app_id}"

    params = {
        "json": 1,
        "filter": filter_param,  # toprated / recent / funny
        "language": "english",
        "review_type": "all",
        "purchase_type": "all",
        "num_per_page": 100,
        "cursor": "*",
        "start_date": start_ts,
        "end_date": end_ts,
    }

    all_reviews = []
    page = 0
    MAX_PAGES = 500

    while True:
        if len(all_reviews) >= max_reviews:
            break

        page += 1
        resp = requests.get(base_url, params=params)
        if resp.status_code != 200:
            print(f"[{app_id}] 요청 실패:", resp.status_code, resp.text[:200])
            break

        data = resp.json()
        reviews = data.get("reviews", [])
        if not reviews:
            break

        for r in reviews:
            ts = r.get("timestamp_created")
            if ts is None:
                continue
            dt = datetime.utcfromtimestamp(ts)
            if start_dt <= dt <= now_utc:
                all_reviews.append(r)
                if len(all_reviews) >= max_reviews:
                    break

        cursor = data.get("cursor")
        if not cursor or page >= MAX_PAGES:
            break
        params["cursor"] = cursor

    rows = []
    for r in all_reviews:
        author = r.get("author", {})
        row = {
            "review_id": r.get("recommendationid"),
            "language": r.get("language"),
            "review": r.get("review"),
            "voted_up": r.get("voted_up"),
            "timestamp_created": r.get("timestamp_created"),
            "timestamp_updated": r.get("timestamp_updated"),
            "review_datetime_utc": datetime.utcfromtimestamp(
                r.get("timestamp_created", 0)
            ),
            "votes_up": r.get("votes_up"),
            "votes_funny": r.get("votes_funny"),
            "playtime_forever": author.get("playtime_forever"),
            "num_games_owned": author.get("num_games_owned"),
            "num_reviews": author.get("num_reviews"),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def collect_reviews_for_genre(
    genre: str,
    filter_param: str,
    days_back: int = DAYS_BACK,
    max_reviews_per_game: int = MAX_REVIEWS_PER_GAME,
) -> pd.DataFrame:
    """
    장르에 속한 여러 게임에 대해 리뷰를 수집하고 하나의 DataFrame으로 합치기.
    ➜ 장르 리스트(최대 20개) 중에서 매번 5개를 랜덤으로 골라서 수집.
    """
    games_all = GENRE_GAME_LIST.get(genre, [])
    if not games_all:
        return pd.DataFrame()

    # 여기서 20개 중 5개 랜덤 추출
    selected_games = random.sample(games_all, k=min(5, len(games_all)))

    dfs = []

    for g in selected_games:
        df_g = fetch_reviews_for_game(
            g["app_id"],
            filter_param=filter_param,
            days_back=days_back,
            max_reviews=max_reviews_per_game,
        )
        if not df_g.empty:
            df_g["game_name"] = g["name"]
            df_g["genre"] = genre
            dfs.append(df_g)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


def apply_keyword_filter(df: pd.DataFrame, keyword: str | None) -> pd.DataFrame:
    """
    키워드가 공란이면 그대로 사용, 입력되어 있으면 해당 키워드 포함 리뷰만 필터.
    """
    if df is None or df.empty:
        return df

    if keyword is None or keyword.strip() == "":
        return df

    kw = keyword.strip()
    mask = df["review"].str.contains(kw, case=False, na=False)
    return df[mask].copy()


def extract_top_keywords(df: pd.DataFrame, top_k: int = 20) -> pd.DataFrame:
    """
    리뷰 텍스트에서 자주 등장하는 단어 Top K 추출.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["keyword", "count"])

    text = " ".join(df["review"].dropna().astype(str).tolist()).lower()
    tokens = re.findall(r"[a-z']+", text)

    words = [
        w for w in tokens
        if len(w) > 2 and w not in STOPWORDS
    ]

    counter = Counter(words)
    common = counter.most_common(top_k)

    return pd.DataFrame(common, columns=["keyword", "count"])


def create_sentiment_chart(df: pd.DataFrame, genre: str):
    """
    선택된 장르 안에서 긍정/부정 리뷰 개수 막대 그래프.
    """
    if df is None or df.empty or "sentiment_label" not in df.columns:
        return None

    # 🔹 최종 라벨을 보기 좋게 매핑
    label_map = {
        "POSITIVE": "Positive",
        "NEGATIVE": "Negative",
        "NEUTRAL": "Neutral",
    }
    sentiment_series = df["sentiment_label"].map(lambda x: label_map.get(x, x))

    counts = sentiment_series.value_counts().reset_index()
    counts.columns = ["sentiment", "count"]

    fig = px.bar(
        counts,
        x="sentiment",
        y="count",
        title=f"{genre} 장르 리뷰 감정 분포",
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="리뷰 수", xaxis_title="감정")
    return fig


# ==========================
# 4. UI – 사이드바
# ==========================

with st.sidebar:
    st.header("⚙️ 분석 설정")

    selected_genre = st.selectbox("분석할 장르 선택", GENRES, index=4)  # 기본값 RPG

    filter_label = st.selectbox(
        "리뷰 기준",
        ["Most Helpful", "Most Recent", "Funny"],
        index=0,
        help="Steam 리뷰 API의 filter 파라미터로 매핑됩니다.",
    )

    keyword = st.text_input(
        "분석 키워드 (선택)",
        placeholder="예: patch, bug, balance ... (비워두면 전체 리뷰 분석)",
    )

    st.markdown("---")
    st.subheader("🔍 심층 분석 설정")
    ambiguity_threshold = st.slider(
        "1차 모델 점수가 얼마나 '애매해야' 심층 분석할까요?",
        min_value=0.05,
        max_value=0.5,
        value=0.15,
        step=0.05,
        help="0.5를 기준으로 ±값 안에 있는 리뷰만 Gemini로 심층 분석합니다.",
    )
    max_deep_dives = st.number_input(
        "최대 심층 분석 리뷰 수",
        min_value=0,
        max_value=5,
        value=3,
        step=1,
    )

    st.markdown("---")
    if st.button("🚀 장르 리뷰 분석 실행"):
        st.session_state["run_analysis"] = True
        st.session_state.pop("result_df", None)


# ==========================
# 5. 메인 로직
# ==========================

if st.session_state.get("run_analysis", False) and "result_df" not in st.session_state:
    filter_param = FILTER_LABEL_TO_PARAM[filter_label]

    with st.spinner("리뷰 수집 및 1차 감정 분석 중입니다..."):
        # 1) 장르 전체 게임 리뷰 수집
        raw_df = collect_reviews_for_genre(
            selected_genre,
            filter_param=filter_param,
            days_back=DAYS_BACK,
            max_reviews_per_game=MAX_REVIEWS_PER_GAME,
        )

        if raw_df is None or raw_df.empty:
            st.error("리뷰 데이터를 가져오지 못했습니다. App ID나 네트워크를 확인해주세요.")
            st.session_state["run_analysis"] = False
        else:
            # 2) 키워드 필터 적용 (공란이면 전체)
            filtered_df = apply_keyword_filter(raw_df, keyword)

            if filtered_df.empty:
                st.warning("해당 키워드를 포함하는 리뷰가 없습니다. 키워드를 변경하거나 비워두고 다시 시도해주세요.")
                st.session_state["run_analysis"] = False
            else:
                # 3) 1차 감정 분석
                scored_df = run_fast_sentiment_analysis(filtered_df, selected_genre)

                # 4) 2차 Gemini 심층 분석 (애매한 리뷰 위주)
                if max_deep_dives > 0:
                    scored_df = pick_and_run_deep_analysis(
                        scored_df,
                        ambiguity_threshold=ambiguity_threshold,
                        max_deep_dives=max_deep_dives,
                    )

                st.session_state["result_df"] = scored_df

# ==========================
# 6. 결과 시각화
# ==========================

if "result_df" in st.session_state:
    result_df = st.session_state["result_df"]

    total_games = result_df["game_name"].nunique() if "game_name" in result_df.columns else None
    total_reviews = len(result_df)

    st.markdown("## 📊 장르별 감정 분포 & 키워드")

    # 상단 요약 메트릭
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("분석 장르", selected_genre)
    with m2:
        st.metric("분석 리뷰 수", f"{total_reviews:,}")
    with m3:
        if total_games:
            st.metric("포함된 게임 수", total_games)

    # 감정 분포 그래프 + 키워드 Top N
    col_left, col_right = st.columns([1.4, 1.0], gap="large")
    with col_left:
        chart = create_sentiment_chart(result_df, selected_genre)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("감정 분포를 표시할 수 없습니다.")

    with col_right:
        st.subheader("📌 자주 등장하는 키워드")
        keyword_df = extract_top_keywords(result_df, top_k=20)
        if keyword_df.empty:
            st.write("키워드를 추출할 수 있는 리뷰가 없습니다.")
        else:
            st.dataframe(keyword_df, use_container_width=True, height=380)
            st.caption(
                "※ 공통적인 단어(the, game 등)는 제거하고, 길이 3 이상 단어 기준으로 계산했습니다."
            )

    # 종합 인사이트
    st.markdown("## 🧠 GPT 종합 인사이트")
    overall_text = get_overall_insights_from_gpt(
        result_df, keyword or ""
    )  # 키워드 공란도 허용
    st.markdown(overall_text)

    # 심층 분석 리뷰
    st.markdown("## 🔍 심층 분석 리뷰 (Gemini)")

    if "final_sentiment" in result_df.columns:
        deep_df = result_df.dropna(subset=["final_sentiment"])
    else:
        deep_df = pd.DataFrame()

    if deep_df.empty:
        st.info(
            "심층 분석 대상 리뷰가 없습니다. "
            "심층 분석 개수를 늘리거나 ambiguity threshold를 넓혀보세요."
        )
    else:
        for i, row in deep_df.iterrows():
            base_sent = row.get("sentiment_label", "")
            score = row.get("sentiment_score", 0.0)
            final_sent = row.get("final_sentiment", "N/A")

            title = (
                f"리뷰 #{i} | 1차: {base_sent} (score: {score:.2f}) "
                f"→ 최종 판단: **{final_sent}**"
            )

            with st.expander(title):
                st.caption(f"🎮 게임: {row.get('game_name', 'Unknown')}")
                st.markdown("> " + row["review"].strip()[:600] + "...")
                st.markdown("---")
                st.markdown(f"**✅ 긍정 요인**: {row.get('positive_points', 'N/A')}")
                st.markdown(f"**⚠️ 부정 요인**: {row.get('negative_points', 'N/A')}")
                st.markdown(f"**🛠 개발팀 제언**: {row.get('suggestion', 'N/A')}")

