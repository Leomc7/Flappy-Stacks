import pygame
from sys import exit
import random
import time

pygame.init()
pygame.mixer.init()  # Initialize the mixer
clock = pygame.time.Clock()

# Load the sound file
pygame.mixer.music.load("assets/caching.mp3")  # Correct path to the sound file

# Test the sound
pygame.mixer.music.play()
pygame.time.delay(2000)  # Wait for 2 seconds to hear the sound

# Window
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Images
bird_image = pygame.image.load("assets/bagflappy_png.png")
skyline_image = pygame.image.load("assets/background_551x720.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")

# Game
scroll_speed = 1
bird_start_position = (100, 250)
score = 0
record = 0  # Track the highest score
coins = 0  # Coins collected
font = pygame.font.SysFont('Segoe', 26)
game_stopped = True
paused = False  # Pause state
hard_mode = False  # Hard mode state

# Power-ups
shield_active = False
slow_motion_active = False
double_coins_active = False


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_image
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.vel = 0
        self.flap = False
        self.alive = True

    def update(self, user_input):
        # Gravity and Flap
        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        # Rotate Bird
        self.image = pygame.transform.rotate(bird_image, self.vel * -7)

        # User Input
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # Horizontal movement
        speed = scroll_speed * 1.5 if hard_mode else scroll_speed
        self.rect.x -= speed
        
        if self.rect.x <= -win_width:
            self.kill()
        
        if self.pipe_type == 'bottom' and not self.passed:
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                global score
                score += 1
                pygame.mixer.music.play()  # Play the sound here


class Ground:
    def __init__(self):
        self.image = ground_image
        self.x1 = 0
        self.x2 = win_width
        self.y = 520

    def update(self):
        if hard_mode:
            self.x1 -= scroll_speed * 1.5  # Ground moves faster in hard mode
            self.x2 -= scroll_speed * 1.5
        else:
            self.x1 -= scroll_speed
            self.x2 -= scroll_speed
        if self.x1 <= -win_width:
            self.x1 = self.x2 + win_width
        if self.x2 <= -win_width:
            self.x2 = self.x1 + win_width

    def draw(self, window):
        window.blit(self.image, (self.x1, self.y))
        window.blit(self.image, (self.x2, self.y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 223, 0), (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        if hard_mode:
            self.rect.x -= scroll_speed * 1.5  # Coins move faster in hard mode
        else:
            self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()


def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def main():
    global score, coins, shield_active, slow_motion_active, double_coins_active, record, paused, hard_mode
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())
    pipe_timer = 0
    coin_timer = 0
    pipes = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    ground = Ground()

    run = True
    while run:
        quit_game()
        user_input = pygame.key.get_pressed()

        if user_input[pygame.K_p]:
            paused = not paused
            time.sleep(0.2)  # Debounce to avoid multiple toggles

        if not paused:
            window.fill((0, 0, 0))
            window.blit(skyline_image, (0, 0))

            pipes.draw(window)
            coins_group.draw(window)
            ground.draw(window)
            bird.draw(window)

            # Display score, coins, and record with a black rectangle background
            black_rect = pygame.Surface((200, 90))  # Adjust size as needed
            black_rect.set_alpha(128)  # Semi-transparent
            black_rect.fill((0, 0, 0))  # Black color
            window.blit(black_rect, (10, 10))  # Position the rectangle

            # Render and display the text on top of the rectangle
            score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
            coin_text = font.render('Coins: ' + str(coins), True, pygame.Color(255, 223, 0))
            record_text = font.render('Record: ' + str(record), True, pygame.Color(0, 255, 255))  # Cyan color
            window.blit(score_text, (20, 20))
            window.blit(coin_text, (20, 50))
            window.blit(record_text, (20, 80))

            # Display mode text
            if hard_mode:
                mode_text = font.render('Hard Mode', True, pygame.Color(255, 0, 0))  # Red for hard mode
                switch_text = font.render('Press N for Normal Mode', True, pygame.Color(0, 255, 0))  # Green for switching
            else:
                mode_text = font.render('Normal Mode', True, pygame.Color(0, 255, 0))  # Green for normal mode
                switch_text = font.render('Press H for Hard Mode', True, pygame.Color(255, 0, 0))  # Red for switching

            window.blit(mode_text, (win_width - mode_text.get_width() - 20, 20))
            window.blit(switch_text, (win_width - switch_text.get_width() - 20, 50))

            if bird.sprite.alive:
                pipes.update()
                coins_group.update()
                ground.update()
            bird.update(user_input)

            # Check for collisions with coins
            collected_coins = pygame.sprite.spritecollide(bird.sprite, coins_group, True)
            if double_coins_active:
                coins += len(collected_coins) * 2  # Double coins if power-up is active
            else:
                coins += len(collected_coins)  # Normal coins

            # Check for collisions with pipes and ground
            collision_pipes = pygame.sprite.spritecollide(bird.sprite, pipes, False)
            if bird.sprite.rect.y >= 500:
                collision_ground = True
            else:
                collision_ground = False

            if (collision_pipes or collision_ground) and not shield_active:
                bird.sprite.alive = False
                if collision_ground:
                    # Update record if the current score is higher
                    if score > record:
                        record = score
                    # Display game over screen with record
                    window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                                win_height // 2 - game_over_image.get_height() // 2))
                    record_text = font.render('Record: ' + str(record), True, pygame.Color(0, 255, 255))
                    window.blit(record_text, (win_width // 2 - record_text.get_width() // 2, 400))
                    if user_input[pygame.K_r]:
                        score = 0
                        shield_active = False
                        slow_motion_active = False
                        double_coins_active = False
                        break

            # Shield power-up: Respawn bird in front of the next pipe
            if (collision_pipes or collision_ground) and shield_active:
                # Find the next pipe
                next_pipe = None
                for pipe in pipes:
                    if pipe.rect.x > bird.sprite.rect.x:
                        next_pipe = pipe
                        break

                if next_pipe:
                    # Respawn bird in front of the next pipe
                    bird.sprite.rect.center = (next_pipe.rect.x - 100, bird_start_position[1])  # 100 pixels in front
                else:
                    # If no next pipe, respawn at starting position
                    bird.sprite.rect.center = bird_start_position

                shield_active = False  # Shield is used up

            # Spawn pipes
            if pipe_timer <= 0 and bird.sprite.alive:
                x_top, x_bottom = 550, 550
                # Increased vertical gap in hard mode
                pipe_gap = random.randint(100, 130) if hard_mode else random.randint(90, 130)
                y_top = random.randint(-600, -480)
                y_bottom = y_top + pipe_gap + bottom_pipe_image.get_height()
                pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
                pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
                # Faster pipe spawning in hard mode
                pipe_timer = random.randint(100, 150) if hard_mode else random.randint(180, 250)
            pipe_timer -= 1

            # Spawn coins (more frequently and in better positions)
            if coin_timer <= 0 and bird.sprite.alive:
                x_coin = 550
                y_coin = random.randint(150, 450)  # Spawn coins in the middle of the screen
                coins_group.add(Coin(x_coin, y_coin))
                coin_timer = random.randint(100, 150)  # Spawn coins more frequently
            coin_timer -= 1

            # Adjust scroll speed based on slow motion
            if slow_motion_active:
                clock.tick(60 * 0.7)  # 30% slower
            else:
                clock.tick(60)

            # Switch between hard and normal mode
            if user_input[pygame.K_h]:
                hard_mode = True
            if user_input[pygame.K_n]:
                hard_mode = False

            pygame.display.update()
        else:
            # Display pause text
            pause_text = font.render('Paused', True, pygame.Color(255, 255, 255))
            window.blit(pause_text, (win_width // 2 - pause_text.get_width() // 2, win_height // 2 - pause_text.get_height() // 2))
            pygame.display.update()


def shop():
    global coins, shield_active, slow_motion_active, double_coins_active
    while True:
        quit_game()
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))

        shop_text = font.render('Shop', True, pygame.Color(255, 255, 255))
        coin_text = font.render('Coins: ' + str(coins), True, pygame.Color(255, 223, 0))
        window.blit(shop_text, (win_width // 2 - shop_text.get_width() // 2, 20))
        window.blit(coin_text, (win_width // 2 - coin_text.get_width() // 2, 60))

        shield_text = font.render('1. Shield (10 coins)', True, pygame.Color(0, 255, 0))
        slow_motion_text = font.render('2. Slow Motion (15 coins)', True, pygame.Color(0, 0, 255))
        double_coins_text = font.render('3. Double Coins (20 coins)', True, pygame.Color(255, 0, 0))
        window.blit(shield_text, (win_width // 2 - shield_text.get_width() // 2, 120))
        window.blit(slow_motion_text, (win_width // 2 - slow_motion_text.get_width() // 2, 160))
        window.blit(double_coins_text, (win_width // 2 - double_coins_text.get_width() // 2, 200))

        back_text = font.render('Press B to go back', True, pygame.Color(255, 255, 255))
        window.blit(back_text, (win_width // 2 - back_text.get_width() // 2, 260))

        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_1] and coins >= 10:
            coins -= 10
            shield_active = True
        if user_input[pygame.K_2] and coins >= 15:
            coins -= 15
            slow_motion_active = True
        if user_input[pygame.K_3] and coins >= 20:
            coins -= 20
            double_coins_active = True
        if user_input[pygame.K_b]:
            break

        pygame.display.update()


def menu():
    global game_stopped
    while game_stopped:
        quit_game()
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(bird_image, (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                win_height // 2 - start_image.get_height() // 2))

        # Add text for starting the game and going to the shop with background rectangles
        texts = [
            ('Press SPACE to Start', (255, 255, 255), 400),
            ('Press S to go to the Shop', (0, 255, 0), 440),
            ('Press H for Hard Mode', (255, 0, 0), 480)
        ]
        
        for text, color, y_pos in texts:
            text_surf = font.render(text, True, color)
            text_surf = pygame.transform.scale(text_surf, (int(text_surf.get_width() * 1.2), int(text_surf.get_height() * 1.2)))
            # Background rectangle
            bg_rect = pygame.Surface((text_surf.get_width() + 20, text_surf.get_height() + 10))
            bg_rect.set_alpha(150)
            bg_rect.fill((0, 0, 0))
            window.blit(bg_rect, (win_width // 2 - (text_surf.get_width() + 20) // 2, y_pos - 5))
            window.blit(text_surf, (win_width // 2 - text_surf.get_width() // 2, y_pos))

        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()
        if user_input[pygame.K_s]:
            shop()
        if user_input[pygame.K_h]:
            global hard_mode
            hard_mode = True
            main()

        pygame.display.update()


menu()