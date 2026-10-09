
import pygame
import random
from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)


class GameEngine:
    def __init__(self, width, height, difficulty="Medium"):
        self.width = width
        self.height = height
        self.difficulty = difficulty

        self.reset_game()

    def reset_game(self):
        self.player = Player(
            self.width // 2 - 20, self.height - 50, 40, 20
        )

        speeds = {"Easy": 0.8, "Medium": 1.5, "Hard": 3.0}
        fire_rates = {"Easy": 0.003, "Medium": 0.01, "Hard": 0.025}

        self.enemy_grid = EnemyGrid(
            self.width, speed=speeds[self.difficulty]
        )

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        self.enemy_fire_chance = fire_rates[self.difficulty]

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False
        self.menu_choice = 0

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_choice = (self.menu_choice - 1) % 5
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_choice = (self.menu_choice + 1) % 5
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.difficulty = {
                        "Easy": "Medium",
                        "Medium": "Hard",
                        "Hard": "Easy"
                    }[self.difficulty]
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.difficulty = {
                        "Easy": "Hard",
                        "Medium": "Easy",
                        "Hard": "Medium"
                    }[self.difficulty]
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.menu_choice == 4:
                        pygame.event.post(
                            pygame.event.Event(pygame.QUIT)
                        )
                    else:
                        self.reset_game()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0:
                bullet_x = self.player.center_x() - 2
                self.player_bullets.append(
                    Bullet(bullet_x, self.player.y, direction=-1)
                )
                self._shoot_cooldown = 15

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    def update(self):
        if self.game_over:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        self.enemy_grid.move()

        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2
                self.enemy_bullets.append(
                    Bullet(
                        bullet_x,
                        enemy.y + enemy.height,
                        direction=1
                    )
                )

        for bullet in self.player_bullets:
            bullet.move()

        for bullet in self.enemy_bullets:
            bullet.move()

        self.player_bullets = [
            b for b in self.player_bullets if not b.off_screen(self.height)
        ]
        self.enemy_bullets = [
            b for b in self.enemy_bullets if not b.off_screen(self.height)
        ]

        # Task 1: Safe bullet-enemy collision handling.
        remaining_bullets = []

        for bullet in self.player_bullets:
            hit = False

            for enemy in self.enemy_grid.alive_enemies():
                if bullet.rect().colliderect(enemy.rect()):
                    enemy.alive = False
                    self.score += 1
                    hit = True
                    break

            if not hit:
                remaining_bullets.append(bullet)

        self.player_bullets = remaining_bullets

        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                break

        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True

    def render(self, screen):
        screen.fill(BLACK)

        pygame.draw.rect(screen, GREEN, self.player.rect())

        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())

        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        score_text = self.font.render(
            f"Score: {self.score}", True, WHITE
        )
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(210)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            title_font = pygame.font.SysFont("Arial", 44, bold=True)
            message_font = pygame.font.SysFont("Arial", 25)

            title = title_font.render("GAME OVER", True, RED)
            final_score = message_font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            difficulty_text = message_font.render(
                f"Difficulty: {self.difficulty}  (Left/Right to change)",
                True, YELLOW
            )

            screen.blit(
                title,
                title.get_rect(center=(self.width // 2, 150))
            )
            screen.blit(
                final_score,
                final_score.get_rect(center=(self.width // 2, 205))
            )
            screen.blit(
                difficulty_text,
                difficulty_text.get_rect(center=(self.width // 2, 260))
            )

            options = [
                "Play Again",
                "Select Easy",
                "Select Medium",
                "Select Hard",
                "Exit"
            ]

            for index, option in enumerate(options):
                color = YELLOW if index == self.menu_choice else WHITE
                label = message_font.render(option, True, color)
                screen.blit(
                    label,
                    label.get_rect(
                        center=(self.width // 2, 335 + index * 42)
                    )
                )

            hint = pygame.font.SysFont("Arial", 18).render(
                "Up/Down: Choose  |  Enter: Confirm  |  Left/Right: Difficulty",
                True, WHITE
            )
            screen.blit(
                hint,
                hint.get_rect(center=(self.width // 2, self.height - 25))
            )
