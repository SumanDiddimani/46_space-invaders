
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


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(width // 2 - 20, height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(width)

        self.player_bullets = []
        self.enemy_bullets = []
        self._shoot_cooldown = 0
        self.enemy_fire_chance = 0.01

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._shoot_cooldown <= 0 and not self.game_over:
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
            bullet for bullet in self.player_bullets
            if not bullet.off_screen(self.height)
        ]

        self.enemy_bullets = [
            bullet for bullet in self.enemy_bullets
            if not bullet.off_screen(self.height)
        ]

        # Task 1: Handle collisions safely without modifying
        # the bullet list while iterating over it.
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

        # Check enemy bullets hitting the player.
        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                break

        # Check whether enemies have reached the player.
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

        # Task 2: Display the Game Over screen and final score.
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            title_font = pygame.font.SysFont(
                "Arial", 48, bold=True
            )
            message_font = pygame.font.SysFont("Arial", 28)

            title = title_font.render(
                "GAME OVER", True, RED
            )
            final_score = message_font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            instruction = message_font.render(
                "Close the window to exit", True, WHITE
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 60
                    )
                )
            )

            screen.blit(
                final_score,
                final_score.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

            screen.blit(
                instruction,
                instruction.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 50
                    )
                )
            )
