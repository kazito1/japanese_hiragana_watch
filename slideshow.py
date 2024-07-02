import pygame
import time

class Slideshow:
    def __init__(self, screen, photo_manager, transition_time):
        print("Initializing Slideshow")
        self.screen = screen
        self.photo_manager = photo_manager
        self.transition_time = transition_time
        self.current_photo = None
        self.next_photo = None
        self.alpha = 255
        self.last_change = 0
        self.transitioning = False
        self.load_initial_photo()

    def load_initial_photo(self):
        print("Loading initial photo")
        photo_path = self.photo_manager.get_random_photo()
        if photo_path:
            self.current_photo = self.load_and_scale_photo(photo_path)
        else:
            print("Failed to load initial photo")

    def load_and_scale_photo(self, photo_path):
        print(f"Loading and scaling photo: {photo_path}")
        try:
            photo = pygame.image.load(photo_path)
            return self.scale_photo(photo)
        except pygame.error as e:
            print(f"Error loading image {photo_path}: {e}")
            return None

    def scale_photo(self, photo):
        screen_rect = self.screen.get_rect()
        photo_rect = photo.get_rect()
        
        scale = min(screen_rect.width / photo_rect.width, screen_rect.height / photo_rect.height)
        new_width = int(photo_rect.width * scale)
        new_height = int(photo_rect.height * scale)
        
        scaled_photo = pygame.transform.smoothscale(photo, (new_width, new_height))
        return scaled_photo

    def update(self):
        current_time = time.time()
        if not self.transitioning and current_time - self.last_change >= self.transition_time:
            self.start_transition()

        if self.transitioning and self.next_photo:
            self.alpha -= 5  # Adjust for smoother/faster transition
            if self.alpha <= 0:
                self.current_photo = self.next_photo
                self.next_photo = None
                self.alpha = 255
                self.last_change = current_time
                self.transitioning = False

    def start_transition(self):
        print("Starting transition")
        max_attempts = 5  # Try up to 5 times to get a valid photo
        for _ in range(max_attempts):
            new_photo_path = self.photo_manager.get_random_photo()
            if new_photo_path:
                loaded_photo = self.load_and_scale_photo(new_photo_path)
                if loaded_photo:
                    self.next_photo = loaded_photo
                    self.transitioning = True
                    return
            print("Failed to get or load new photo, trying again...")
        print("Failed to get a valid photo after multiple attempts")

    def draw(self):
        if self.current_photo:
            photo_rect = self.current_photo.get_rect()
            screen_rect = self.screen.get_rect()
            photo_pos = ((screen_rect.width - photo_rect.width) // 2,
                         (screen_rect.height - photo_rect.height) // 2)
            self.screen.blit(self.current_photo, photo_pos)
        
        if self.transitioning and self.next_photo:
            next_photo = self.next_photo.copy()
            next_photo.set_alpha(255 - self.alpha)
            photo_rect = next_photo.get_rect()
            screen_rect = self.screen.get_rect()
            photo_pos = ((screen_rect.width - photo_rect.width) // 2,
                         (screen_rect.height - photo_rect.height) // 2)
            self.screen.blit(next_photo, photo_pos)