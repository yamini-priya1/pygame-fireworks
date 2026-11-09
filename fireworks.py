import pygame, random, math, colorsys, sys

pygame.init()

# Robust fullscreen init: fall back to a windowed mode if fullscreen fails
try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except pygame.error:
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h))

width, height = screen.get_size()
pygame.display.set_caption("Ultimate Sparkling Cursor")
clock = pygame.time.Clock()


class Spark:
    def __init__(self, x, y, color, size_mult=1, speed_mult=1):
        self.x = x
        self.y = y
        self.color = color
        # Cast to int: some pygame/SDL builds require integer Surface sizes
        self.radius = max(1, int(random.randint(1, 4) * size_mult))
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 8) * speed_mult
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.fade = random.uniform(0.85, 0.95)
        self.gravity = 0.15
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y, self.life))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed + self.gravity
        self.speed *= self.fade
        self.gravity += 0.02
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            # Draw trail
            for i, (tx, ty, tlife) in enumerate(self.trail):
                trail_alpha = int(100 * (i / len(self.trail)) * (self.life / self.max_life))
                if trail_alpha > 0:
                    s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*self.color, trail_alpha),
                                     (self.radius, self.radius), max(1, self.radius // 2))
                    surface.blit(s, (int(tx - self.radius), int(ty - self.radius)))

            # Draw main spark with glow
            alpha = max(0, int(255 * (self.life / self.max_life)))
            s = pygame.Surface((self.radius * 6, self.radius * 6), pygame.SRCALPHA)

            # Outer glow
            pygame.draw.circle(s, (*self.color, alpha // 3),
                             (self.radius * 3, self.radius * 3), self.radius * 3)
            # Middle glow
            pygame.draw.circle(s, (*self.color, alpha // 2),
                             (self.radius * 3, self.radius * 3), self.radius * 2)
            # Core
            pygame.draw.circle(s, (*self.color, alpha),
                             (self.radius * 3, self.radius * 3), self.radius)

            surface.blit(s, (int(self.x - self.radius * 3), int(self.y - self.radius * 3)))


class ShockWave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 5
        self.max_radius = 100
        self.life = 30

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.2
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = int(200 * (self.life / 30))
            s = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha),
                             (self.max_radius, self.max_radius), int(self.radius), 3)
            surface.blit(s, (int(self.x - self.max_radius), int(self.y - self.max_radius)))


class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = bright_color()
        self.sparks = []
        self.exploded = False
        self.vy = random.uniform(-15, -10)
        self.life = random.randint(20, 40)

    def explode(self):
        if not self.exploded:
            for _ in range(80):
                self.sparks.append(Spark(self.x, self.y, self.color, 1.5, 1.2))
            self.exploded = True

    def update(self):
        if not self.exploded:
            self.y += self.vy
            self.vy += 0.3
            self.life -= 1
            if self.life <= 0:
                self.explode()
        else:
            for s in self.sparks[:]:
                s.update()
                if s.life <= 0:
                    self.sparks.remove(s)

    def draw(self, surface):
        if not self.exploded:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)
        else:
            for s in self.sparks:
                s.draw(surface)


def bright_color():
    hue = random.random()
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
    return (r, g, b)


def rainbow_color(offset=0):
    hue = (pygame.time.get_ticks() / 1000 + offset) % 1
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1, 1)]
    return (r, g, b)


# Game state
sparks = []
shockwaves = []
fireworks = []
mode = 0  # 0: normal, 1: rainbow, 2: fireworks, 3: mega sparks
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

modes_text = ["Normal Sparks", "Rainbow Trail", "Fireworks", "Mega Burst"]
instructions = [
    "Move mouse or click to sparkle",
    "RIGHT CLICK for shockwave",
    "SPACE for firework",
    "M to change mode",
    "ESC to exit"
]

running = True
last_spark_time = 0

while running:
    current_time = pygame.time.get_ticks()

    # Dark background with fade effect
    fade = pygame.Surface((width, height))
    fade.set_alpha(30)
    fade.fill((0, 0, 10))
    screen.blit(fade, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                mode = (mode + 1) % 4
            elif event.key == pygame.K_SPACE:
                mx_pos, _ = pygame.mouse.get_pos()
                fireworks.append(Firework(mx_pos, height))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click
                cx, cy = pygame.mouse.get_pos()
                shockwaves.append(ShockWave(cx, cy, bright_color()))
                for _ in range(50):
                    sparks.append(Spark(cx, cy, bright_color(), 1.2, 1.5))

    x, y = pygame.mouse.get_pos()
    mx, my = pygame.mouse.get_rel()
    left_click = pygame.mouse.get_pressed()[0]

    # Note: pygame.mouse.get_focused() is unreliable across window managers
    # (e.g. some Linux/Wayland setups) even in fullscreen, so we no longer
    # gate spark generation on it -- that was silently disabling the whole
    # effect on some systems.
    spark_count = 0
    size_mult = 1
    speed_mult = 1
    color = (255, 255, 255)  # safe default, always overwritten below when used

    if mode == 0:  # Normal sparks
        if abs(mx) > 0 or abs(my) > 0 or left_click:
            spark_count = 15 if left_click else 8

    elif mode == 1:  # Rainbow trail
        if abs(mx) > 0 or abs(my) > 0 or left_click:
            spark_count = 20 if left_click else 10

    elif mode == 2:  # Fireworks mode
        if left_click and current_time - last_spark_time > 200:
            fireworks.append(Firework(x, height))
            last_spark_time = current_time

    elif mode == 3:  # Mega sparks
        if abs(mx) > 0 or abs(my) > 0 or left_click:
            spark_count = 40 if left_click else 20
            size_mult = 1.5
            speed_mult = 1.2

    # Create sparks (color/size chosen per-spark for real variety)
    if spark_count > 0:
        for _ in range(spark_count):
            if mode == 1:
                offset = random.uniform(0, 0.2)
                spark_color = rainbow_color(offset)
            else:
                spark_color = bright_color()
            sparks.append(Spark(x, y, spark_color, size_mult, speed_mult))

    # Update and draw everything
    for s in sparks[:]:
        s.update()
        s.draw(screen)
        if s.life <= 0:
            sparks.remove(s)

    for w in shockwaves[:]:
        w.update()
        w.draw(screen)
        if w.life <= 0:
            shockwaves.remove(w)

    for f in fireworks[:]:
        f.update()
        f.draw(screen)
        if f.exploded and len(f.sparks) == 0:
            fireworks.remove(f)

    # Draw UI
    mode_text = font.render(f"Mode: {modes_text[mode]}", True, (255, 255, 255))
    screen.blit(mode_text, (20, 20))

    y_offset = 60
    for instruction in instructions:
        inst_text = small_font.render(instruction, True, (200, 200, 200))
        screen.blit(inst_text, (20, y_offset))
        y_offset += 25

    # Particle count
    count_text = small_font.render(f"Particles: {len(sparks) + sum(len(f.sparks) for f in fireworks)}",
                                   True, (150, 150, 150))
    screen.blit(count_text, (width - 180, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()