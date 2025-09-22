import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
import random
import math
import requests
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="🛟 두부 튜브 게임",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 게임 상수
GAME_WIDTH = 500
GAME_HEIGHT = 700
CHAR_SIZE = 30
GRAVITY = 1
JUMP_POWER = -15
TUBE_WIDTH = 100
TUBE_HEIGHT = 20

# CSS 스타일
st.markdown("""
<style>
    .game-container {
        border: 3px solid #ff69b4;
        border-radius: 15px;
        padding: 20px;
        background: linear-gradient(180deg, #87ceeb 0%, #ffb6c1 100%);
        margin: 20px 0;
    }
    .score-board {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
    }
    .game-over {
        background: rgba(255, 0, 0, 0.1);
        border: 2px solid #ff4444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .controls {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 게임 상태 초기화
def init_game_state():
    if 'game' not in st.session_state:
        st.session_state.game = {
            'char_x': GAME_WIDTH // 2 - CHAR_SIZE // 2,
            'char_y': GAME_HEIGHT - 100,
            'velocity_y': 0,
            'water_level': GAME_HEIGHT,
            'tubes': [],
            'score': 0,
            'game_over': False,
            'on_tube': False,
            'particles': [],
            'stars': [],
            'wave_offset': 0,
            'char_bounce': 0,
            'water_rise_speed': 1,
            'game_started': False,
            'high_score': 0,
            'frame_count': 0,
            'last_update': time.time()
        }
        generate_initial_content()

def generate_initial_content():
    # 초기 튜브 생성
    st.session_state.game['tubes'] = []
    for i in range(6):
        tube = {
            'x': random.randint(50, GAME_WIDTH - TUBE_WIDTH - 50),
            'y': GAME_HEIGHT - 150 - i * 120,
            'width': TUBE_WIDTH,
            'height': TUBE_HEIGHT,
            'color': f'hsl({random.randint(0, 360)}, 70%, 60%)',
            'bounce': random.random() * 2 * math.pi
        }
        st.session_state.game['tubes'].append(tube)
    
    # 별 생성
    st.session_state.game['stars'] = []
    for _ in range(30):
        star = {
            'x': random.randint(0, GAME_WIDTH),
            'y': random.randint(0, GAME_HEIGHT // 2),
            'size': random.randint(2, 4),
            'twinkle': random.random() * 2 * math.pi
        }
        st.session_state.game['stars'].append(star)

def update_game():
    game = st.session_state.game
    
    if game['game_over'] or not game['game_started']:
        return
    
    current_time = time.time()
    dt = current_time - game['last_update']
    game['last_update'] = current_time
    game['frame_count'] += 1
    
    # 애니메이션 업데이트
    game['wave_offset'] += 0.1
    game['char_bounce'] += 0.15
    
    # 물 상승
    game['water_level'] -= game['water_rise_speed']
    
    # 캐릭터 물리 (중력)
    game['velocity_y'] += GRAVITY
    game['char_y'] += game['velocity_y']
    
    # 경계 체크
    if game['char_x'] < 0:
        game['char_x'] = 0
    if game['char_x'] + CHAR_SIZE > GAME_WIDTH:
        game['char_x'] = GAME_WIDTH - CHAR_SIZE
    
    # 바닥 체크
    if game['char_y'] + CHAR_SIZE > GAME_HEIGHT:
        game['char_y'] = GAME_HEIGHT - CHAR_SIZE
        game['velocity_y'] = 0
        game['on_tube'] = True
    
    # 튜브 충돌 체크
    game['on_tube'] = False
    char_rect = {
        'x': game['char_x'],
        'y': game['char_y'],
        'width': CHAR_SIZE,
        'height': CHAR_SIZE
    }
    
    for tube in game['tubes']:
        if (char_rect['x'] < tube['x'] + tube['width'] and
            char_rect['x'] + char_rect['width'] > tube['x'] and
            char_rect['y'] < tube['y'] + tube['height'] and
            char_rect['y'] + char_rect['height'] > tube['y'] and
            game['velocity_y'] >= 0):
            
            game['char_y'] = tube['y'] - CHAR_SIZE
            game['velocity_y'] = 0
            game['on_tube'] = True
            break
    
    # 튜브 업데이트
    tubes_to_remove = []
    for i, tube in enumerate(game['tubes']):
        tube['bounce'] += 0.1
        tube['y'] += game['water_rise_speed']
        
        if tube['y'] > GAME_HEIGHT:
            tubes_to_remove.append(i)
            game['score'] += 10
    
    # 화면 밖 튜브 제거 및 새 튜브 생성
    for i in reversed(tubes_to_remove):
        game['tubes'].pop(i)
        new_tube = {
            'x': random.randint(50, GAME_WIDTH - TUBE_WIDTH - 50),
            'y': -50,
            'width': TUBE_WIDTH,
            'height': TUBE_HEIGHT,
            'color': f'hsl({random.randint(0, 360)}, 70%, 60%)',
            'bounce': random.random() * 2 * math.pi
        }
        game['tubes'].append(new_tube)
    
    # 별 업데이트
    for star in game['stars']:
        star['twinkle'] += 0.05
        star['y'] += game['water_rise_speed']
        if star['y'] > GAME_HEIGHT // 2:
            star['y'] = -10
            star['x'] = random.randint(0, GAME_WIDTH)
    
    # 게임오버 체크
    if game['char_y'] + CHAR_SIZE > game['water_level']:
        game['game_over'] = True
        if game['score'] > game['high_score']:
            game['high_score'] = game['score']
    
    # 난이도 증가
    if game['score'] > 0 and game['score'] % 100 == 0:
        game['water_rise_speed'] = min(3, 1 + game['score'] // 200)

def create_game_plot():
    game = st.session_state.game
    
    fig = go.Figure()
    
    # 배경 설정
    fig.update_layout(
        width=GAME_WIDTH + 100,
        height=GAME_HEIGHT + 100,
        xaxis=dict(range=[0, GAME_WIDTH], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[GAME_HEIGHT, 0], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )
    
    # 하늘 배경
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=GAME_WIDTH, y1=game['water_level'],
        fillcolor="rgba(135, 206, 250, 0.6)",
        line=dict(width=0),
        layer="below"
    )
    
    # 별들
    if game['stars']:
        star_x = [s['x'] for s in game['stars']]
        star_y = [s['y'] for s in game['stars']]
        star_sizes = [s['size'] * (1 + 0.3 * math.sin(s['twinkle'])) for s in game['stars']]
        
        fig.add_scatter(
            x=star_x, y=star_y,
            mode='markers',
            marker=dict(
                size=star_sizes,
                color='white',
                opacity=0.8,
                symbol='star'
            ),
            hoverinfo='skip'
        )
    
    # 물 (물결 효과)
    wave_x = list(range(0, GAME_WIDTH + 1, 5))
    wave_y = []
    for x in wave_x:
        wave = 5 * math.sin((x * 0.02) + game['wave_offset'])
        wave_y.append(game['water_level'] + wave)
    
    # 물 영역 채우기
    water_x = [0] + wave_x + [GAME_WIDTH, 0]
    water_y = [GAME_HEIGHT] + wave_y + [GAME_HEIGHT, GAME_HEIGHT]
    
    fig.add_scatter(
        x=water_x, y=water_y,
        fill='toself',
        fillcolor='rgba(0, 119, 190, 0.7)',
        line=dict(color='rgba(255, 255, 255, 0.8)', width=2),
        hoverinfo='skip'
    )
    
    # 튜브들
    for tube in game['tubes']:
        bounce_offset = 2 * math.sin(tube['bounce'])
        tube_y = tube['y'] + bounce_offset
        
        fig.add_shape(
            type="rect",
            x0=tube['x'], y0=tube_y,
            x1=tube['x'] + tube['width'], y1=tube_y + tube['height'],
            fillcolor=tube['color'],
            line=dict(color="white", width=2)
        )
    
    # 캐릭터 (두부)
    bounce_offset = 2 * math.sin(game['char_bounce'])
    char_y_with_bounce = game['char_y'] + bounce_offset
    
    # 캐릭터 그림자
    fig.add_shape(
        type="rect",
        x0=game['char_x'] + 2, y0=game['char_y'] + CHAR_SIZE + 2,
        x1=game['char_x'] + CHAR_SIZE + 2, y1=game['char_y'] + CHAR_SIZE + 7,
        fillcolor="rgba(0, 0, 0, 0.3)",
        line=dict(width=0)
    )
    
    # 캐릭터 본체
    fig.add_shape(
        type="rect",
        x0=game['char_x'], y0=char_y_with_bounce,
        x1=game['char_x'] + CHAR_SIZE, y1=char_y_with_bounce + CHAR_SIZE,
        fillcolor="rgba(255, 255, 255, 0.9)",
        line=dict(color="hotpink", width=3)
    )
    
    # 캐릭터 얼굴
    eye_y = char_y_with_bounce + 8
    fig.add_scatter(
        x=[game['char_x'] + 8, game['char_x'] + 22],
        y=[eye_y, eye_y],
        mode='markers',
        marker=dict(size=6, color='black'),
        hoverinfo='skip'
    )
    
    # 미소 (근사치)
    smile_x = game['char_x'] + 15
    smile_y = char_y_with_bounce + 20
    fig.add_scatter(
        x=[smile_x], y=[smile_y],
        mode='markers',
        marker=dict(size=8, color='red', symbol='circle'),
        hoverinfo='skip'
    )
    
    return fig

def handle_controls():
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("⬅️ 왼쪽", key="left"):
            if not st.session_state.game['game_over']:
                st.session_state.game['char_x'] = max(0, st.session_state.game['char_x'] - 15)
    
    with col2:
        if st.button("⬆️ 점프", key="jump"):
            if not st.session_state.game['game_over'] and st.session_state.game['on_tube']:
                st.session_state.game['velocity_y'] = JUMP_POWER
    
    with col3:
        if st.button("➡️ 오른쪽", key="right"):
            if not st.session_state.game['game_over']:
                st.session_state.game['char_x'] = min(GAME_WIDTH - CHAR_SIZE, st.session_state.game['char_x'] + 15)
    
    with col4:
        if st.button("🎮 시작/재시작", key="restart"):
            init_game_state()
            st.session_state.game['game_started'] = True
            st.session_state.game['game_over'] = False
    
    with col5:
        if st.button("⏸️ 일시정지", key="pause"):
            st.session_state.game['game_started'] = not st.session_state.game['game_started']

# 메인 게임 로직
def main():
    init_game_state()
    
    st.title("🛟 엄지공주 두부 튜브 게임 🛟")
    st.markdown("### 물이 차올라와요! 튜브를 타고 계속 위로 올라가세요!")
    
    # 사이드바 - 게임 정보
    with st.sidebar:
        st.header("🎮 게임 정보")
        
        game = st.session_state.game
        
        st.markdown(f"""
        <div class="score-board">
            <div>🏆 현재 점수: {game['score']}</div>
            <div>⭐ 최고 점수: {game['high_score']}</div>
            <div>💧 물 위험도: {game['water_rise_speed']}</div>
            <div>📏 물 높이: {GAME_HEIGHT - game['water_level']:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="controls">
            <h4>🎯 조작법</h4>
            <p>⬅️ ➡️ : 좌우 이동</p>
            <p>⬆️ : 점프 (튜브 위에서만!)</p>
            <p>🎮 : 게임 시작/재시작</p>
            <p>⏸️ : 일시정지</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 게임 통계 보기"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
    
    # 게임 화면
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 게임오버 메시지
        if st.session_state.game['game_over']:
            st.markdown(f"""
            <div class="game-over">
                <h2>🌊 게임 오버! 🌊</h2>
                <p>점수: {st.session_state.game['score']}점</p>
                <p>두부가 물에 빠졌어요! 🫧</p>
                <p>다시 도전해보세요!</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif not st.session_state.game['game_started']:
            st.markdown("""
            <div class="game-container">
                <h3 style="text-align: center;">🌟 게임을 시작하려면 '🎮 시작/재시작' 버튼을 눌러주세요! 🌟</h3>
                <p style="text-align: center;">물이 점점 차올라와요! 튜브를 타고 계속 위로 올라가세요!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 게임 업데이트 및 렌더링
        if st.session_state.game['game_started'] and not st.session_state.game['game_over']:
            update_game()
        
        # 게임 플롯
        game_plot = create_game_plot()
        st.plotly_chart(game_plot, use_container_width=True, key="game_plot")
        
        # 컨트롤 버튼
        handle_controls()
    
    with col2:
        if st.session_state.get('show_stats', False):
            st.subheader("📊 게임 통계")
            
            # 가상의 통계 데이터
            stats_data = pd.DataFrame({
                '게임 회차': range(1, 11),
                '점수': [random.randint(50, 500) for _ in range(10)],
                '생존 시간(초)': [random.randint(30, 300) for _ in range(10)]
            })
            
            fig_stats = px.line(stats_data, x='게임 회차', y='점수', 
                               title='점수 추이', markers=True)
            st.plotly_chart(fig_stats, use_container_width=True)
            
            st.dataframe(stats_data, use_container_width=True)
    
    # 자동 업데이트를 위한 타이머
    if st.session_state.game['game_started'] and not st.session_state.game['game_over']:
        time.sleep(0.1)
        st.rerun()

# 게임 실행
main()