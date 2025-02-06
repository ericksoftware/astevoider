import pygame
import random

# Inicializa Pygame
pygame.init()

# Dimensiones de la pantalla
WIDTH, HEIGHT = 1280, 720

# Establece el modo de pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
fullscreen = False

last_player_angle = 0 # Variable global para almacenar la última dirección del jugador

# Cargar imagen de fondo y ajustarla al tamaño de la pantalla sin deformarla
background = pygame.image.load("may.png")

# Posiciones iniciales del fondo para el desplazamiento infinito
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 0.2  # Velocidad del desplazamiento del fondo

# Tamaño de los objetos
cube_size = 50
ball_size = 50
enemy_size = 50

# Cargar imagen del jugador y ajustarla al tamaño del cuadro
player_image = pygame.image.load("ship.png")
player_image = pygame.transform.scale(player_image, (45, 60))

# Cargar imagen de la bola (asteroide)
ball_image = pygame.image.load("asteroiddef.png")
ball_image = pygame.transform.scale(ball_image, (ball_size, ball_size))

# Posición inicial del jugador
player = pygame.Rect(WIDTH // 2 - cube_size // 2, HEIGHT // 2 - cube_size // 2, cube_size, cube_size)

# Lista de bolas
balls = []

# Reloj para controlar la tasa de FPS
clock = pygame.time.Clock()

# Función para generar una bola en una posición aleatoria fuera de la pantalla
def generate_ball():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WIDTH)
        y = -ball_size
    elif side == 'bottom':
        x = random.randint(0, WIDTH)
        y = HEIGHT + ball_size
    elif side == 'left':
        x = -ball_size
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH + ball_size
        y = random.randint(0, HEIGHT)
    
    direction_x = (WIDTH // 2 - x) / 1000
    direction_y = (HEIGHT // 2 - y) / 1000
    ball = pygame.Rect(x, y, ball_size, ball_size)
    angle = random.randint(0, 360)  # Ángulo inicial aleatorio para variar
    return ball, direction_x, direction_y, angle

# Generar bolas iniciales (4)
for _ in range(4):
    ball, dir_x, dir_y, angle = generate_ball()
    balls.append((ball, dir_x, dir_y, angle))

# Variables de tiempo y dificultad
last_ball_time = 0
difficulty_time = pygame.time.get_ticks()  # Para aumentar bolas cada 10 segundos
more_balls = 4  # Inicialmente genera entre 1 y 4 bolas

# Variables del enemigo
enemy_active = False
enemy_spawn_time = pygame.time.get_ticks()
enemy = pygame.Rect(-enemy_size, -enemy_size, enemy_size, enemy_size)

# Función para mostrar la pantalla inicial
def show_initial_screen():
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fondo negro para la pantalla de inicio
        screen.blit(background, (0, 0))  # Fondo del juego

        font = pygame.font.SysFont(None, 75)
        message_text = font.render("Presiona cualquier tecla para iniciar", True, (255, 255, 255))
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))

        global bg_y1, bg_y2
        bg_y1 += bg_speed
        bg_y2 += bg_speed

        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT

        screen.blit(background, (0, bg_y1))
        screen.blit(background, (0, bg_y2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return 'start'

        pygame.display.flip()

# Bucle principal del juego
if show_initial_screen() == 'start':
    running = True
    game_started = False

    while running:
        current_time = pygame.time.get_ticks()

        if not game_started:
            game_started = True
            start_time = pygame.time.get_ticks()

        if current_time - difficulty_time > 10000:
            more_balls += 1
            difficulty_time = current_time

        bg_y1 += bg_speed
        bg_y2 += bg_speed

        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT

        screen.blit(background, (0, bg_y1))
        screen.blit(background, (0, bg_y2))

        # screen.blit(player_image, (player.x, player.y))

        if current_time - last_ball_time > random.randint(1000, 2000):
            last_ball_time = current_time
            for _ in range(random.randint(1, more_balls)):
                ball, dir_x, dir_y, angle = generate_ball()
                balls.append((ball, dir_x, dir_y, angle))

        new_balls = []
        for ball, dir_x, dir_y, angle in balls:
            ball.x += dir_x * 5
            ball.y += dir_y * 5
            angle += .5  

            rotated_image = pygame.transform.rotate(ball_image, angle)
            new_rect = rotated_image.get_rect(center=ball.center)

            screen.blit(rotated_image, new_rect.topleft)

            # Verificar colisión con el jugador
            if player.colliderect(ball):
                running = False  # Terminar el juego si colisiona con un asteroide

            if -ball_size < ball.x < WIDTH and -ball_size < ball.y < HEIGHT:
                new_balls.append((ball, dir_x, dir_y, angle))

        balls = new_balls  

        if not enemy_active and current_time - enemy_spawn_time > 5000:
            enemy_active = True
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                enemy.x, enemy.y = random.randint(0, WIDTH), -enemy_size
            elif side == 'bottom':
                enemy.x, enemy.y = random.randint(0, WIDTH), HEIGHT + enemy_size
            elif side == 'left':
                enemy.x, enemy.y = -enemy_size, random.randint(0, HEIGHT)
            else:
                enemy.x, enemy.y = WIDTH + enemy_size, random.randint(0, HEIGHT)

        # Cargar imagen del enemigo (alien)
        enemy_image = pygame.image.load("aliendef.png")
        enemy_image = pygame.transform.scale(enemy_image, (65, 40))  # Ajustar al tamaño adecuado

        # Calcular el ángulo de rotación para el alien según su dirección
        def get_enemy_angle(enemy, player):
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            angle = pygame.math.Vector2(dx, dy).angle_to(pygame.math.Vector2(1, 0))  # Calcular el ángulo
            return angle

        # Dentro de tu bucle principal donde mueves al enemigo:
        if enemy_active:
            # Mover el enemigo hacia el jugador
            if enemy.x < player.x:
                enemy.x += 2
            if enemy.x > player.x:
                enemy.x -= 2
            if enemy.y < player.y:
                enemy.y += 2
            if enemy.y > player.y:
                enemy.y -= 2

            # Calcular el ángulo de rotación del enemigo
            enemy_angle = get_enemy_angle(enemy, player)

            # Rotar la imagen del enemigo según el ángulo calculado
            rotated_enemy_image = pygame.transform.rotate(enemy_image, enemy_angle)
            rotated_rect = rotated_enemy_image.get_rect(center=enemy.center)  # Ajustar el rectángulo para la rotación

            # Dibujar la imagen del enemigo rotada en la pantalla
            screen.blit(rotated_enemy_image, rotated_rect.topleft)

            # Verificar colisión con el jugador
            if player.colliderect(enemy):
                running = False  # Terminar el juego si colisiona con el enemigo


        # Control de movimiento del jugador
        keys = pygame.key.get_pressed()
        speed = 5
        moved = False  # Detecta si el jugador se movió

        # Configura un ángulo de transición suave (gradual)
        angle_smoothness = 10  # Qué tan suave será el giro. Cuanto mayor el valor, más lento el giro

        # Variable para almacenar el ángulo actual de la nave
        current_angle = last_player_angle  # Inicializamos con el último ángulo del jugador

        # Variable para el nuevo ángulo objetivo
        target_angle = last_player_angle  # Inicialmente es el último ángulo conocido

        # Bucle de movimiento y ángulos para diagonales
        if (keys[pygame.K_w] and keys[pygame.K_a]) or (keys[pygame.K_UP] and keys[pygame.K_LEFT]):  # Arriba izquierda
            player.x -= speed
            player.y -= speed
            target_angle = 45  
            moved = True
        elif (keys[pygame.K_w] and keys[pygame.K_d]) or (keys[pygame.K_UP] and keys[pygame.K_RIGHT]):  # Arriba derecha
            player.x += speed
            player.y -= speed
            target_angle = -45  
            moved = True
        elif (keys[pygame.K_s] and keys[pygame.K_a]) or (keys[pygame.K_DOWN] and keys[pygame.K_LEFT]):  # Abajo izquierda
            player.x -= speed
            player.y += speed
            target_angle = 135  
            moved = True
        elif (keys[pygame.K_s] and keys[pygame.K_d]) or (keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]):  # Abajo derecha
            player.x += speed
            player.y += speed
            target_angle = -135  
            moved = True
        else:  # Movimiento en direcciones simples
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # Izquierda
                player.x -= speed
                target_angle = 90  
                moved = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # Derecha
                player.x += speed
                target_angle = -90  
                moved = True
            if keys[pygame.K_w] or keys[pygame.K_UP]:  # Arriba
                player.y -= speed
                target_angle = 0  
                moved = True
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # Abajo
                player.y += speed
                target_angle = 180  
                moved = True

        # Asegurarse de que la transición hacia el nuevo ángulo sea suave y correcta
        if current_angle != target_angle:
            # Calcula la diferencia en ángulo
            angle_diff = target_angle - current_angle

            # Si la diferencia es mayor a 180, gira en la dirección opuesta (la más corta)
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360

            # Ajusta el ángulo suavemente hacia el objetivo
            if angle_diff > 0:
                current_angle += angle_smoothness
                if current_angle > target_angle:
                    current_angle = target_angle
            elif angle_diff < 0:
                current_angle -= angle_smoothness
                if current_angle < target_angle:
                    current_angle = target_angle

        # Establece el ángulo final para el giro suave
        last_player_angle = current_angle

        # Limitar el movimiento dentro de la pantalla
        player.x = max(0, min(WIDTH - cube_size, player.x))
        player.y = max(0, min(HEIGHT - cube_size, player.y))

        # Dibujar la nave con la rotación suave
        rotated_player = pygame.transform.rotate(player_image, last_player_angle)
        player_rect = rotated_player.get_rect(center=player.center)
        screen.blit(rotated_player, player_rect.topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen else pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        survival_time = (current_time - start_time) // 1000
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Survival Time: {survival_time}s", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(59)

# Pantalla de "Game Over"
font = pygame.font.SysFont(None, 75)
game_over_text = font.render("Game Over", True, (255, 0, 0))
score_final_text = font.render(f"Your Final Score: {survival_time}s", True, (255, 255, 0))

screen.fill((0, 0, 0))
screen.blit(game_over_text, (400, 250))
screen.blit(score_final_text, (400, 350))
pygame.display.flip()
pygame.time.wait(3000)

font = pygame.font.SysFont(None, 75)
pygame.quit()
