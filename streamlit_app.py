import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Random;

public class TofuWaterGame extends JPanel implements ActionListener, KeyListener {
    Timer timer;
    int width = 500, height = 700;
    
    // 캐릭터
    int charX = 235, charY = 600, charW = 30, charH = 30;
    int velocityY = 0;
    boolean onTube = false;
    double charBounce = 0; // 캐릭터 통통 튀는 애니메이션
    
    // 중력
    final int GRAVITY = 1;
    final int JUMP = -15;
    
    // 물
    int waterLevel = 700;
    int waterRiseSpeed = 1;
    double waveOffset = 0; // 물결 애니메이션
    
    // 튜브들
    ArrayList<Tube> tubes = new ArrayList<>();
    ArrayList<Particle> particles = new ArrayList<>(); // 파티클 시스템
    ArrayList<Star> stars = new ArrayList<>(); // 별 배경
    
    Random rand = new Random();
    int score = 0;
    Font gameFont = new Font("맑은 고딕", Font.BOLD, 16);
    Font titleFont = new Font("맑은 고딕", Font.BOLD, 24);
    
    // 색상 정의
    Color skyColor1 = new Color(135, 206, 250);
    Color skyColor2 = new Color(255, 182, 193);
    Color waterColor1 = new Color(0, 119, 190);
    Color waterColor2 = new Color(0, 150, 255);
    
    public TofuWaterGame() {
        setPreferredSize(new Dimension(width, height));
        timer = new Timer(16, this); // 60 FPS
        timer.start();
        addKeyListener(this);
        setFocusable(true);
        
        // 배경 별들 생성
        for (int i = 0; i < 30; i++) {
            stars.add(new Star());
        }
        
        // 시작할 때 튜브 몇 개 추가
        for (int i = 0; i < 6; i++) {
            tubes.add(new Tube(rand.nextInt(width - 100), 650 - i * 120));
        }
    }
    
    // 튜브 클래스
    class Tube {
        int x, y, width = 100, height = 20;
        double bounce = 0;
        Color color;
        
        Tube(int x, int y) {
            this.x = x;
            this.y = y;
            // 랜덤 색상
            float hue = rand.nextFloat();
            this.color = Color.getHSBColor(hue, 0.7f, 0.9f);
        }
        
        Rectangle getBounds() {
            return new Rectangle(x, y, width, height);
        }
        
        void update() {
            bounce += 0.1;
        }
        
        void draw(Graphics2D g2d) {
            // 그라데이션 효과
            GradientPaint gp = new GradientPaint(x, y, color.brighter(), 
                                               x, y + height, color.darker());
            g2d.setPaint(gp);
            
            // 통통 튀는 효과
            int bounceY = y + (int)(Math.sin(bounce) * 2);
            RoundRectangle2D tube = new RoundRectangle2D.Double(x, bounceY, width, height, 15, 15);
            g2d.fill(tube);
            
            // 테두리
            g2d.setColor(Color.WHITE);
            g2d.setStroke(new BasicStroke(2));
            g2d.draw(tube);
        }
    }
    
    // 파티클 클래스
    class Particle {
        double x, y, vx, vy;
        Color color;
        int life = 30;
        int maxLife = 30;
        
        Particle(double x, double y) {
            this.x = x;
            this.y = y;
            this.vx = (rand.nextDouble() - 0.5) * 4;
            this.vy = (rand.nextDouble() - 0.5) * 4 - 2;
            this.color = new Color(255, 255, 255, 200);
        }
        
        void update() {
            x += vx;
            y += vy;
            vy += 0.1; // 중력
            life--;
        }
        
        void draw(Graphics2D g2d) {
            float alpha = (float)life / maxLife;
            g2d.setColor(new Color(1f, 1f, 1f, alpha * 0.8f));
            g2d.fillOval((int)x, (int)y, 4, 4);
        }
        
        boolean isDead() {
            return life <= 0;
        }
    }
    
    // 별 클래스
    class Star {
        int x, y, size;
        double twinkle = 0;
        Color color;
        
        Star() {
            x = rand.nextInt(width);
            y = rand.nextInt(height / 2);
            size = rand.nextInt(3) + 1;
            twinkle = rand.nextDouble() * Math.PI * 2;
            color = new Color(255, 255, 255, 150 + rand.nextInt(105));
        }
        
        void update() {
            twinkle += 0.05;
            y += waterRiseSpeed; // 물과 함께 움직임
            if (y > height / 2) {
                y = -10;
                x = rand.nextInt(width);
            }
        }
        
        void draw(Graphics2D g2d) {
            float alpha = (float)(0.5 + 0.5 * Math.sin(twinkle));
            g2d.setColor(new Color(1f, 1f, 1f, alpha * 0.8f));
            g2d.fillOval(x, y, size, size);
        }
    }
    
    @Override
    public void actionPerformed(ActionEvent e) {
        // 물 올라옴
        waterLevel -= waterRiseSpeed;
        waveOffset += 0.1;
        
        // 캐릭터 애니메이션
        charBounce += 0.15;
        
        // 캐릭터 중력 적용
        velocityY += GRAVITY;
        charY += velocityY;
        
        // 화면 경계 체크
        if (charX < 0) charX = 0;
        if (charX + charW > width) charX = width - charW;
        
        // 바닥 체크
        if (charY + charH > height) {
            charY = height - charH;
            velocityY = 0;
            onTube = true;
        }
        
        // 튜브 충돌 체크
        onTube = false;
        Rectangle charRect = new Rectangle(charX, charY, charW, charH);
        for (Tube tube : tubes) {
            if (charRect.intersects(tube.getBounds()) && velocityY >= 0) {
                charY = tube.y - charH;
                velocityY = 0;
                onTube = true;
                
                // 착지 파티클 효과
                for (int i = 0; i < 5; i++) {
                    particles.add(new Particle(charX + charW/2, charY + charH));
                }
                break;
            }
        }
        
        // 튜브 업데이트 및 이동
        Iterator<Tube> tubeIt = tubes.iterator();
        while (tubeIt.hasNext()) {
            Tube tube = tubeIt.next();
            tube.update();
            tube.y += waterRiseSpeed;
            
            if (tube.y > height) {
                tubeIt.remove();
                score += 10; // 점수 증가
                
                // 새로운 튜브 생성
                tubes.add(new Tube(rand.nextInt(width - 100), -30));
            }
        }
        
        // 파티클 업데이트
        Iterator<Particle> particleIt = particles.iterator();
        while (particleIt.hasNext()) {
            Particle p = particleIt.next();
            p.update();
            if (p.isDead()) {
                particleIt.remove();
            }
        }
        
        // 별 업데이트
        for (Star star : stars) {
            star.update();
        }
        
        // 수면 파티클 추가
        if (rand.nextInt(10) == 0) {
            particles.add(new Particle(rand.nextInt(width), waterLevel + rand.nextInt(20)));
        }
        
        // 게임오버 조건: 물에 빠짐
        if (charY + charH > waterLevel) {
            timer.stop();
            JOptionPane.showMessageDialog(this, 
                String.format("🌊 게임 오버! 🌊\n점수: %d점\n두부가 물에 빠졌어요! 🫧", score),
                "Game Over", JOptionPane.INFORMATION_MESSAGE);
        }
        
        // 물 상승 속도 점진적 증가
        if (score > 0 && score % 100 == 0) {
            waterRiseSpeed = Math.min(3, 1 + score / 200);
        }
        
        repaint();
    }
    
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
        
        // 배경 그라데이션
        GradientPaint skyGradient = new GradientPaint(0, 0, skyColor1, 0, waterLevel, skyColor2);
        g2d.setPaint(skyGradient);
        g2d.fillRect(0, 0, width, waterLevel);
        
        // 별들 그리기
        for (Star star : stars) {
            star.draw(g2d);
        }
        
        // 물 (물결 효과)
        GradientPaint waterGradient = new GradientPaint(0, waterLevel, waterColor1, 0, height, waterColor2);
        g2d.setPaint(waterGradient);
        
        // 물결 모양 만들기
        GeneralPath waterPath = new GeneralPath();
        waterPath.moveTo(0, waterLevel);
        for (int x = 0; x <= width; x += 2) {
            double wave = Math.sin((x * 0.02) + waveOffset) * 5;
            waterPath.lineTo(x, waterLevel + wave);
        }
        waterPath.lineTo(width, height);
        waterPath.lineTo(0, height);
        waterPath.closePath();
        g2d.fill(waterPath);
        
        // 물 표면 하이라이트
        g2d.setColor(new Color(255, 255, 255, 100));
        g2d.setStroke(new BasicStroke(2));
        GeneralPath waveLine = new GeneralPath();
        waveLine.moveTo(0, waterLevel);
        for (int x = 0; x <= width; x += 2) {
            double wave = Math.sin((x * 0.02) + waveOffset) * 5;
            waveLine.lineTo(x, waterLevel + wave);
        }
        g2d.draw(waveLine);
        
        // 튜브들 그리기
        for (Tube tube : tubes) {
            tube.draw(g2d);
        }
        
        // 캐릭터 (두부) 그리기
        int bounceOffset = (int)(Math.sin(charBounce) * 2);
        
        // 그림자
        g2d.setColor(new Color(0, 0, 0, 50));
        g2d.fillOval(charX + 2, charY + charH + 2, charW, 5);
        
        // 캐릭터 본체
        GradientPaint charGradient = new GradientPaint(charX, charY, Color.WHITE, 
                                                     charX, charY + charH, new Color(255, 240, 245));
        g2d.setPaint(charGradient);
        RoundRectangle2D character = new RoundRectangle2D.Double(
            charX, charY + bounceOffset, charW, charH, 10, 10);
        g2d.fill(character);
        
        // 캐릭터 테두리
        g2d.setColor(new Color(255, 105, 180));
        g2d.setStroke(new BasicStroke(2));
        g2d.draw(character);
        
        // 캐릭터 얼굴
        g2d.setColor(Color.BLACK);
        g2d.fillOval(charX + 8, charY + bounceOffset + 8, 3, 3); // 왼쪽 눈
        g2d.fillOval(charX + 19, charY + bounceOffset + 8, 3, 3); // 오른쪽 눈
        
        // 미소
        g2d.setStroke(new BasicStroke(2, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        Arc2D smile = new Arc2D.Double(charX + 10, charY + bounceOffset + 15, 10, 8, 0, -180, Arc2D.OPEN);
        g2d.draw(smile);
        
        // 파티클 그리기
        for (Particle particle : particles) {
            particle.draw(g2d);
        }
        
        // UI 요소들
        g2d.setColor(new Color(255, 255, 255, 200));
        g2d.fillRoundRect(10, 10, 150, 80, 10, 10);
        
        g2d.setColor(Color.BLACK);
        g2d.setFont(gameFont);
        g2d.drawString("점수: " + score, 20, 30);
        g2d.drawString("물 위험도: " + waterRiseSpeed, 20, 50);
        g2d.drawString("💧 높이: " + (700 - waterLevel), 20, 70);
        
        // 조작법 안내
        if (score < 50) {
            g2d.setColor(new Color(0, 0, 0, 150));
            g2d.fillRoundRect(width/2 - 100, height - 100, 200, 60, 10, 10);
            g2d.setColor(Color.WHITE);
            g2d.setFont(new Font("맑은 고딕", Font.BOLD, 12));
            g2d.drawString("← → 이동, SPACE 점프", width/2 - 80, height - 75);
            g2d.drawString("튜브 위에서만 점프 가능!", width/2 - 85, height - 55);
        }
    }
    
    @Override
    public void keyPressed(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.VK_SPACE && onTube) {
            velocityY = JUMP;
            // 점프 파티클 효과
            for (int i = 0; i < 8; i++) {
                particles.add(new Particle(charX + charW/2, charY + charH));
            }
        }
        if (e.getKeyCode() == KeyEvent.VK_LEFT) charX -= 8;
        if (e.getKeyCode() == KeyEvent.VK_RIGHT) charX += 8;
    }
    
    @Override public void keyReleased(KeyEvent e) {}
    @Override public void keyTyped(KeyEvent e) {}
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("🛟 엄지공주 두부 튜브 게임 🛟");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setResizable(false);
            
            TofuWaterGame game = new TofuWaterGame();
            frame.add(game);
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
            
            // 게임 시작 메시지
            JOptionPane.showMessageDialog(frame, 
                "🌟 두부 튜브 게임에 오신 걸 환영해요! 🌟\n\n" +
                "물이 점점 차올라와요! 💧\n" +
                "튜브를 타고 계속 위로 올라가세요! 🛟\n\n" +
                "조작법:\n" +
                "← → : 좌우 이동\n" +
                "SPACE : 점프 (튜브 위에서만!)\n\n" +
                "행운을 빌어요! 🍀",
                "게임 시작!", JOptionPane.INFORMATION_MESSAGE);
        });
    }
}