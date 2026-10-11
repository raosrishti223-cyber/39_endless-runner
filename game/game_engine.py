import pygame
from .player import Player
from .obstacle import Obstacle
from .audio import SoundEffects

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
MAX_SPEED = 14
DIFFICULTIES = {
    "Easy": (4, 90),
    "Medium": (6, 70),
    "Hard": (10, 50),
}
REPLAY_KEYS = {
    pygame.K_e: "Easy",
    pygame.K_m: "Medium",
    pygame.K_h: "Hard",
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.speed_increase_per_frame = 0.003
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.game_over_prompt_font = pygame.font.SysFont("Arial", 24)
        self.sound_effects = SoundEffects()
        self.reset_run("Medium")

    def reset_run(self, difficulty):
        self.difficulty = difficulty
        self.speed, self.spawn_interval = DIFFICULTIES[difficulty]
        self.player = Player(80, self.ground_y)
        self._spawn_timer = 0
        self.obstacles = []
        self.distance = 0
        self.score = 0
        self.game_over = False
        self.exit_requested = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in REPLAY_KEYS:
                    self.reset_run(REPLAY_KEYS[event.key])
                elif event.key == pygame.K_ESCAPE:
                    self.exit_requested = True
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            can_jump = self.player.on_ground
            self.player.jump()
            if can_jump:
                self.sound_effects.play("jump")

    def handle_input(self):
        # Reserved for continuously-held-key input; this runner only
        # needs an edge-triggered jump, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            return

        self.speed = min(self.speed + self.speed_increase_per_frame, MAX_SPEED)
        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        for obstacle in self.obstacles:
            previous_rect = obstacle.rect()
            obstacle.speed = self.speed
            obstacle.move()
            swept_rect = previous_rect.union(obstacle.rect())
            if swept_rect.colliderect(self.player.rect()):
                self.game_over = True
                self.sound_effects.play("game_over")
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self.sound_effects.play("score")

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(screen, BROWN, (0, self.ground_y), (self.width, self.ground_y), 4)

        pygame.draw.rect(screen, WHITE, self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            title = self.game_over_font.render("GAME OVER", True, WHITE)
            final_score = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            prompt = self.game_over_prompt_font.render(
                "E: Easy   M: Medium   H: Hard   Esc: Exit", True, WHITE
            )
            screen.blit(
                title,
                title.get_rect(center=(self.width // 2, self.height // 2 - 60)),
            )
            screen.blit(
                final_score,
                final_score.get_rect(center=(self.width // 2, self.height // 2)),
            )
            screen.blit(
                prompt,
                prompt.get_rect(center=(self.width // 2, self.height // 2 + 50)),
            )
