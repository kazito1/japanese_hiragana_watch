#!/usr/bin/env python3

"""
iCloud Photo Sync Script for Japanese Hiragana Watch

This companion script downloads photos from iCloud Photos to your local
photos_directory for use with the Japanese Hiragana Watch slideshow.

It can optionally filter for favorite photos only, or download from specific albums.

Requirements:
    pip install pyicloud

Usage:
    python3 icloud_photo_sync.py --config config.ini

Optional arguments:
    --favorites-only    Download only favorite photos
    --album NAME        Download from a specific album (e.g., "Favorites")
    --max-photos N      Limit the number of photos to download (default: 50)
"""

import argparse
import configparser
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from pyicloud import PyiCloudService
except ImportError:
    print("Error: pyicloud library not found.")
    print("Please install it using: pip install pyicloud")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    filename='icloud_sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def authenticate_icloud(username, password):
    """
    Authenticate with iCloud service.

    Args:
        username: iCloud email address
        password: iCloud password

    Returns:
        PyiCloudService instance or None if authentication failed
    """
    try:
        api = PyiCloudService(username, password)

        # Handle two-factor authentication
        if api.requires_2fa:
            print("Two-factor authentication required.")
            print("A verification code has been sent to your trusted devices.")
            code = input("Enter the verification code: ")

            result = api.validate_2fa_code(code)
            if not result:
                print("Failed to verify security code")
                logging.error("2FA verification failed")
                return None

            print("Two-factor authentication successful")
            logging.info("2FA authentication successful")

        # Handle two-step authentication (older method)
        elif api.requires_2sa:
            print("Two-step authentication required.")
            devices = api.trusted_devices

            for i, device in enumerate(devices):
                print(f"  {i}: {device.get('deviceName', 'Unknown device')}")

            device_index = int(input("Select device to receive code: "))
            device = devices[device_index]

            if not api.send_verification_code(device):
                print("Failed to send verification code")
                logging.error("Failed to send 2SA verification code")
                return None

            code = input("Enter the verification code: ")
            if not api.validate_verification_code(device, code):
                print("Failed to verify security code")
                logging.error("2SA verification failed")
                return None

            print("Two-step authentication successful")
            logging.info("2SA authentication successful")

        logging.info(f"Successfully authenticated as {username}")
        return api

    except Exception as e:
        print(f"Authentication error: {e}")
        logging.error(f"Authentication error: {e}")
        return None


def get_photos_to_download(api, favorites_only=False, album_name=None, max_photos=50):
    """
    Get list of photos to download from iCloud.

    Args:
        api: PyiCloudService instance
        favorites_only: If True, only download favorites
        album_name: Name of specific album to download from
        max_photos: Maximum number of photos to download

    Returns:
        List of photo objects to download
    """
    photos_to_download = []

    try:
        # List available albums
        print("\nAvailable albums:")
        for album_name_item in api.photos.albums:
            album = api.photos.albums[album_name_item]
            print(f"  - {album_name_item} ({len(album)} photos)")

        # Determine which photos to download
        if album_name:
            if album_name not in api.photos.albums:
                print(f"Error: Album '{album_name}' not found")
                logging.error(f"Album '{album_name}' not found")
                return []

            print(f"\nDownloading from album: {album_name}")
            photos_to_download = list(api.photos.albums[album_name])[:max_photos]

        elif favorites_only:
            # Try to find Favorites album
            favorites_album_names = ['Favorites', 'Favourites', 'お気に入り']
            found = False

            for fav_name in favorites_album_names:
                if fav_name in api.photos.albums:
                    print(f"\nDownloading from Favorites album: {fav_name}")
                    photos_to_download = list(api.photos.albums[fav_name])[:max_photos]
                    found = True
                    break

            if not found:
                print("Warning: Favorites album not found. Downloading from All Photos instead.")
                logging.warning("Favorites album not found, using All Photos")
                photos_to_download = list(api.photos.all)[:max_photos]
        else:
            print(f"\nDownloading from All Photos (max {max_photos})")
            photos_to_download = list(api.photos.all)[:max_photos]

        logging.info(f"Found {len(photos_to_download)} photos to download")
        return photos_to_download

    except Exception as e:
        print(f"Error getting photos: {e}")
        logging.error(f"Error getting photos: {e}")
        return []


def download_photos(photos, output_directory):
    """
    Download photos to the specified directory.

    Args:
        photos: List of photo objects to download
        output_directory: Directory to save photos

    Returns:
        Number of successfully downloaded photos
    """
    # Create output directory if it doesn't exist
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    downloaded_count = 0
    skipped_count = 0
    error_count = 0

    print(f"\nDownloading {len(photos)} photos to {output_directory}")

    for i, photo in enumerate(photos, 1):
        try:
            filename = photo.filename
            output_path = os.path.join(output_directory, filename)

            # Skip if file already exists
            if os.path.exists(output_path):
                print(f"  [{i}/{len(photos)}] Skipping {filename} (already exists)")
                skipped_count += 1
                continue

            print(f"  [{i}/{len(photos)}] Downloading {filename}...")

            # Download the original version
            download = photo.download()

            with open(output_path, 'wb') as file:
                file.write(download.raw.read())

            downloaded_count += 1
            logging.info(f"Downloaded: {filename}")

        except Exception as e:
            print(f"  Error downloading {photo.filename}: {e}")
            logging.error(f"Error downloading {photo.filename}: {e}")
            error_count += 1

    print(f"\nDownload complete:")
    print(f"  Successfully downloaded: {downloaded_count}")
    print(f"  Skipped (already exist): {skipped_count}")
    print(f"  Errors: {error_count}")

    logging.info(f"Download summary - Downloaded: {downloaded_count}, Skipped: {skipped_count}, Errors: {error_count}")

    return downloaded_count


def main():
    parser = argparse.ArgumentParser(description='Sync photos from iCloud to local directory')
    parser.add_argument('--config', default='config.ini', help='Path to config file')
    parser.add_argument('--favorites-only', action='store_true', help='Download only favorites')
    parser.add_argument('--album', help='Download from specific album name')
    parser.add_argument('--max-photos', type=int, default=50, help='Maximum photos to download (default: 50)')

    args = parser.parse_args()

    # Read configuration
    config = configparser.ConfigParser()
    if not os.path.exists(args.config):
        print(f"Error: Configuration file '{args.config}' not found")
        sys.exit(1)

    config.read(args.config)

    # Get iCloud credentials
    if not config.has_section('iCloud'):
        print("Error: [iCloud] section not found in config.ini")
        print("\nPlease add the following to your config.ini:")
        print("[iCloud]")
        print("username = your_email@icloud.com")
        print("password = your_password")
        sys.exit(1)

    try:
        username = config.get('iCloud', 'username')
        password = config.get('iCloud', 'password')
        photos_directory = config.get('Photos', 'photos_directory', fallback='./photos')
    except configparser.NoOptionError as e:
        print(f"Error: Missing configuration option: {e}")
        sys.exit(1)

    print("=" * 60)
    print("iCloud Photo Sync for Japanese Hiragana Watch")
    print("=" * 60)
    print(f"iCloud Account: {username}")
    print(f"Output Directory: {photos_directory}")
    print(f"Max Photos: {args.max_photos}")

    if args.favorites_only:
        print("Mode: Favorites only")
    elif args.album:
        print(f"Mode: Album '{args.album}'")
    else:
        print("Mode: All Photos")

    print("=" * 60)

    # Authenticate with iCloud
    print("\nAuthenticating with iCloud...")
    api = authenticate_icloud(username, password)

    if not api:
        print("Authentication failed. Exiting.")
        sys.exit(1)

    # Get photos to download
    photos = get_photos_to_download(
        api,
        favorites_only=args.favorites_only,
        album_name=args.album,
        max_photos=args.max_photos
    )

    if not photos:
        print("No photos found to download.")
        sys.exit(0)

    # Download photos
    download_photos(photos, photos_directory)

    print("\nSync complete!")
    logging.info("iCloud photo sync completed")


if __name__ == "__main__":
    main()
