import os
import random
import logging
import glob

class PhotoManager:
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

    def __init__(self, photos_directory='./photos'):
        """
        Initialize PhotoManager to load photos from a local directory.

        Args:
            photos_directory: Path to directory containing photos
        """
        self.photos_directory = os.path.abspath(photos_directory)
        self.photo_list = []
        self.rescan_interval = 300  # Rescan directory every 5 minutes
        self.last_scan_time = 0

        logging.info(f"PhotoManager initialized with directory: {self.photos_directory}")

        if not os.path.exists(self.photos_directory):
            logging.warning(f"Photos directory does not exist: {self.photos_directory}")
            logging.info(f"Creating directory: {self.photos_directory}")
            try:
                os.makedirs(self.photos_directory)
            except Exception as e:
                logging.error(f"Failed to create photos directory: {e}")

        self.scan_photos()

    def scan_photos(self):
        """Scan the photos directory and build a list of image files."""
        import time
        current_time = time.time()

        # Only rescan if enough time has passed
        if self.photo_list and (current_time - self.last_scan_time < self.rescan_interval):
            return

        logging.info(f"Scanning photos directory: {self.photos_directory}")
        self.photo_list = []

        try:
            for ext in self.SUPPORTED_FORMATS:
                # Search for files with this extension (case-insensitive)
                pattern = os.path.join(self.photos_directory, f'*{ext}')
                self.photo_list.extend(glob.glob(pattern))
                # Also check uppercase extensions
                pattern_upper = os.path.join(self.photos_directory, f'*{ext.upper()}')
                self.photo_list.extend(glob.glob(pattern_upper))

            # Remove duplicates and sort
            self.photo_list = sorted(list(set(self.photo_list)))

            logging.info(f"Found {len(self.photo_list)} photos in directory")
            if len(self.photo_list) == 0:
                logging.warning(f"No photos found in {self.photos_directory}")
                logging.warning(f"Please add image files ({', '.join(self.SUPPORTED_FORMATS)}) to this directory")
            else:
                logging.debug(f"Sample photos: {self.photo_list[:3]}")

            self.last_scan_time = current_time

        except Exception as e:
            logging.error(f"Error scanning photos directory: {e}")
            self.photo_list = []

    def get_random_photo(self):
        """
        Get a random photo from the photos directory.

        Returns:
            str: Full path to a random photo file, or None if no photos available
        """
        # Rescan directory periodically (in case new photos were added)
        self.scan_photos()

        if not self.photo_list:
            logging.warning("No photos available to display")
            return None

        # Return a random photo
        photo_path = random.choice(self.photo_list)
        logging.debug(f"Selected photo: {photo_path}")
        return photo_path
