import streamlit as st
import plotly.graph_objects as go
import time
import random
import math

# 페이지 설정
st.set_page_config(
    page_title="🛟 두부 튜브 게임",
    page_icon="🛟",
    layout="wide"
)

# 게임 상수
GAME_WIDTH = 500
GAME_HEIGHT = 600
CHAR_SIZE = 30
GRAVITY = 1
JUMP_POWER = -15
TUBE_WIDTH = 100
TUBE_HEIGHT = 20

# 게임 상태 초기화
def init_game():
    if 'game_data' not in st.session_state:
        st.session_state.game_data = {
            'char_x': GAME_WIDTH // 2 - CHAR_SIZE // 2,
            'char_y': GAME_HEIGHT - 100,
            'velocity_y': 0,
            'water_level': GAME_HEIGHT,
            'tubes': [],
            'score': 0,
            'game_over': False,
            'on_tube': False,
            'wave_offset': 0,
            'char_bounce': 0,
            'water_rise_speed': 1,
            'game_started': False,
            'high_score': 0,
            'frame_count': 0
        }
        create_initial_tubes()

def create_initial_tubes():
    st.session_state.game_data['tubes'] = []
    for i in range(6):
        tube = {
            'x': random.randint(50, GAME_WIDTH - TUBE_WIDTH - 50),
            'y': GAME_HEIGHT - 150 - i * 100,
            'width': TUBE_WIDTH,
            'height': TUBE_HEIGHT,
            'color': f'hsl({random.randint(0, 360)}, 70%, 60%)',
            'bounce': random.random() * 2 * math.pi
        }
        st.session_state.game_data['tubes'].append(tube)

def reset_game():
    st.session_state.game_data = {
        'char_x': GAME_WIDTH // 2 - CHAR_SIZE // 2,
        'char_y': GAME_HEIGHT - 100,
        'velocity_y': 0,
        'water_level': GAME_HEIGHT,
        'tubes': [],
        'score': 0,
        'game_over': False,
        'on_tube': False,
        'wave_offset': 0,
        'char_bounce': 0,
        'water_rise_speed': 1,
        'game_started': True,
        'high_score': st.session_state.game_data.get('high_score', 0),
        'frame_count': 0
    }
    create_initial_tubes()

def update_game():
    game = st.session_state.game_data
    
    if game['game_over'] or not game['game_started']:
        return
    
    # 애니메이션 업데이트
    game['wave_offset'] += 0.1
    game['char_bounce'] += 0.15
    game['frame_count'] += 1
    
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
    
    # 게임오버 체크
    if game['char_y'] + CHAR_SIZE > game['water_level']:
        game['game_over'] = True
        if game['score'] > game['high_score']:
            game['high_score'] = game['score']
    
    # 난이도 증가
    if game['score'] > 0 and game['score'] % 100 == 0:
        game['water_rise_speed'] = min(3, 1 + game['score'] // 200)

def create_game_visualization():
    game = st.session_state.game_data
    
    fig = go.Figure()
    
    # 배경 설정
    fig.update_layout(
        width=GAME_WIDTH + 100,
        height=GAME_HEIGHT + 100,
        xaxis=dict(range=[0, GAME_WIDTH], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[GAME_HEIGHT, 0], showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='lightblue',
        paper_bgcolor='lightpink',
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )
    
    # 물 (물결 효과)
    wave_x = list(range(0, GAME_WIDTH + 1, 10))
    wave_y = []
    for x in wave_x:
        wave = 5 * math.sin((x * 0.03) + game['wave_offset'])
        wave_y.append(game['water_level'] + wave)
    
    # 물 영역 채우기
    water_x = [0] + wave_x + [GAME_WIDTH, 0]
    water_y = [GAME_HEIGHT] + wave_y + [GAME_HEIGHT, GAME_HEIGHT]
    
    fig.add_scatter(
        x=water_x, y=water_y,
        fill='toself',
        fillcolor='blue',
        line=dict(color='white', width=2),
        hoverinfo='skip',
        opacity=0.7
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
    bounce_offset = 3 * math.sin(game['char_bounce'])
    char_y_with_bounce = game['char_y'] + bounce_offset
    
    # 캐릭터 그림자
    fig.add_shape(
        type="rect",
        x0=game['char_x'] + 2, y0=game['char_y'] + CHAR_SIZE + 2,
        x1=game['char_x'] + CHAR_SIZE + 2, y1=game['char_y'] + CHAR_SIZE + 5,
        fillcolor="gray",
        line=dict(width=0),
        opacity=0.5
    )
    
    # 캐릭터 본체
    fig.add_shape(
        type="rect",
        x0=game['char_x'], y0=char_y_with_bounce,
        x1=game['char_x'] + CHAR_SIZE, y1=char_y_with_bounce + CHAR_SIZE,
        fillcolor="white",
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
    
    # 미소
    smile_x = game['char_x'] + 15
    smile_y = char_y_with_bounce + 20
    fig.add_scatter(
        x=[smile_x], y=[smile_y],
        mode='markers',
        marker=dict(size=4, color='red', symbol='circle'),
        hoverinfo='skip'
    )
    
    return fig

def main():
    init_game()
    
    st.title("🛟 엄지공주 두부 튜브 게임 🛟")
    st.subheader("물이 차올라와요! 튜브를 타고 계속 위로 올라가세요!")
    
    game = st.session_state.game_data
    
    # 점수 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("현재 점수", game['score'])
    
    with col2:
        st.metric("최고 점수", game['high_score'])
    
    with col3:
        st.metric("물 위험도", game['water_rise_speed'])
    
    with col4:
        st.metric("물 높이", int(GAME_HEIGHT - game['water_level']))
    
    # 게임 화면과 컨트롤
    game_col, control_col = st.columns([3, 1])
    
    with game_col:
        # 게임오버 메시지
        if game['game_over']:
            st.error(f"🌊 게임 오버! 🌊\n점수: {game['score']}점\n두부가 물에 빠졌어요! 🫧")
        
        elif not game['game_started']:
            st.info("🌟 게임을 시작하려면 '시작' 버튼을 눌러주세요! 🌟")
        
        # 게임 업데이트
        if game['game_started'] and not game['game_over']:
            update_game()
        
        # 게임 시각화
        game_fig = create_game_visualization()
        st.plotly_chart(game_fig, use_container_width=True, key="game_display")
        
        # 컨트롤 버튼
        st.subheader("🎮 게임 조작")
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)
        
        with btn_col1:
            if st.button("⬅️ 왼쪽", key="left_btn"):
                if not game['game_over'] and game['game_started']:
                    game['char_x'] = max(0, game['char_x'] - 25)
                    st.rerun()
        
        with btn_col2:
            jump_enabled = game['on_tube'] and game['game_started'] and not game['game_over']
            if st.button("⬆️ 점프", key="jump_btn", disabled=not jump_enabled):
                if jump_enabled:
                    game['velocity_y'] = JUMP_POWER
                    st.rerun()
        
        with btn_col3:
            if st.button("➡️ 오른쪽", key="right_btn"):
                if not game['game_over'] and game['game_started']:
                    game['char_x'] = min(GAME_WIDTH - CHAR_SIZE, game['char_x'] + 25)
                    st.rerun()
        
        with btn_col4:
            if st.button("🎮 시작/재시작", key="start_btn"):
                reset_game()
                st.rerun()
        
        with btn_col5:
            if game['game_started'] and not game['game_over']:
                if st.button("⏸️ 일시정지", key="pause_btn"):
                    game['game_started'] = False
            else:
                if st.button("▶️ 계속", key="resume_btn"):
                    if not game['game_over']:
                        game['game_started'] = True
                        st.rerun()
    
    with control_col:
        st.subheader("🎯 게임 도움말")
        st.write("**조작법:**")
        st.write("- ⬅️ ➡️ : 좌우 이동")
        st.write("- ⬆️ : 점프 (튜브 위에서만!)")
        st.write("- 🎮 : 게임 시작/재시작")
        st.write("- ⏸️ ▶️ : 일시정지/재개")
        
        st.write("**게임 목표:**")
        st.write("- 물이 차오르기 전에 튜브를 타고 위로!")
        st.write("- 점수를 많이 획득하세요!")
        st.write("- 물에 빠지면 게임오버!")
        
        st.write("**팁:**")
        st.write("- 튜브 위에서만 점프 가능")
        st.write("- 점수가 높을수록 물이 빨리 차올라요")
        st.write("- 타이밍을 잘 맞춰서 점프하세요!")
        
        if game['score'] > 0:
            st.write(f"**현재 기록:**")
            st.write(f"- 점수: {game['score']}점")
            st.write(f"- 생존 시간: {game['frame_count'] // 10}초")
    
    # 자동 업데이트
    if game['game_started'] and not game['game_over']:
        time.sleep(0.1)
        st.rerun()

if __name__ == "__main__":
    main()