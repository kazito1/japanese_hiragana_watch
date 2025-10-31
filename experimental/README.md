# Experimental Features

This directory contains experimental features that are not yet stable or have known limitations.

## iCloud Photo Sync (`icloud_photo_sync.py`)

**Status:** Experimental - Limited Compatibility

A companion script that attempts to sync photos from iCloud Photos directly to the watch's photo directory on Linux systems (Fedora/Raspberry Pi OS).

### Known Issues

- **Does not work with all Apple account types**, particularly:
  - Apple IDs using third-party email addresses (Hotmail, Gmail, Yahoo, etc.)
  - Certain account security configurations
  - Newly created @icloud.com email aliases

- **Authentication failures** are common due to:
  - Apple's changing authentication requirements
  - Incompatibility between `pyicloud` library and certain account setups
  - Two-factor authentication complexities

### When It Might Work

This script may work for users with:
- Native @icloud.com Apple IDs that have been active for a long time
- Standard two-factor authentication enabled
- No special security restrictions

### Alternative Approaches

If this script doesn't work for you (which is likely), consider:

1. **Manual Export** - Download photos from https://www.icloud.com/photos and copy to `./photos` directory
2. **iCloud Drive Sync** - Set up iCloud Drive and sync a photos folder
3. **Third-party Tools** - Use tools like `icloudpd` or similar alternatives
4. **Mac-based Sync** - If you have a Mac, use `osxphotos` to export and sync to Linux device

### Usage

See the main README.md for detailed usage instructions.

### Support

This is experimental code provided as-is. For a reliable experience, manual photo management is recommended.
