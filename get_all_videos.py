#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取完整频道数据示例 - 支持多频道批量处理
从Google Sheets读取YouTube频道ID列表，批量处理所有频道

This script now serves as the main entry point for the application.
The core logic has been refactored into classes within other modules.
"""

# Standard library imports (keep only if genuinely needed at this top level)
# import os
# import requests
# import json
# import time
# import gspread

# Third-party imports (keep only if genuinely needed at this top level)
# from google.oauth2.service_account import Credentials # Likely not needed here anymore

# Local application imports
# These might have been here before, but are now mostly used within the App class or other classes.
# from youtube_video_fetcher import YouTubeVideoFetcher
# from config_manager import ConfigManager
# from google_sheets_reader import GoogleSheetsReader
# from srt_service import SrtService
# from channel_processor import ChannelProcessor

# The App class encapsulates all the application logic and service initializations.
from app import App

if __name__ == "__main__":
    # Instantiate the main application class
    main_app = App()
    # Run the application
    main_app.run()
    # Final message after the application has completed its run
    print("\n🎉 程序结束!")
