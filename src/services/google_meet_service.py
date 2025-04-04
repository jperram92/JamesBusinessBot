import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import os
import json
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, ElementHandle
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleMeetService:
    """Google Meet meeting service implementation."""
    
    def __init__(self, config: Dict):
        """Initialize the Google Meet service with configuration."""
        self.config = config
        self.credentials_path = config['meetings']['google_meet'].get('credentials_path')
        self.google_account = config['meetings']['google_meet'].get('google_account', {})
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/meetings.space.created'
        ]
        self.service = None
        self.current_meeting = None
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.recording = False
        
        # Initialize the Google Calendar API service
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.scopes
            )
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar API service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar API: {str(e)}")
            raise
    
    async def _try_find_button_by_text(self, page) -> Optional[ElementHandle]:
        """Strategy 1: Direct text content match"""
        logger.info("Trying strategy 1: Direct text content match")
        elements = await page.query_selector_all('button, span')
        for element in elements:
            try:
                text = await element.text_content()
                if text and "Ask to join" in text:
                    logger.info("Found button by text content")
                    return element
            except Exception as e:
                continue
        return None

    async def _try_find_button_by_selectors(self, page) -> Optional[ElementHandle]:
        """Strategy 2: Class and attribute combinations"""
        logger.info("Trying strategy 2: Class and attribute combinations")
        selectors = [
            'button[class*="mUlrbf-LgbsSe"][class*="OWXEXe"]',
            'button[jsname="V67aGc"]',
            'span[jsname="V67aGc"]',
            'button[class*="UywwFc-vQzf8d"]'
        ]
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    logger.info(f"Found button using selector: {selector}")
                    return element
            except Exception:
                continue
        return None

    async def _try_find_button_by_javascript(self, page) -> Optional[ElementHandle]:
        """Strategy 3: JavaScript click attempt"""
        logger.info("Trying strategy 3: JavaScript click")
        try:
            js_selectors = [
                'button:has-text("Ask to join")',
                'button[jsname="V67aGc"]',
                'span[jsname="V67aGc"]',
                'button.mUlrbf-LgbsSe'
            ]
            
            for selector in js_selectors:
                try:
                    element = await page.evaluate(f'''
                        () => {{
                            const el = document.querySelector('{selector}');
                            if (el) {{
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {{
                                    return el;
                                }}
                            }}
                            return null;
                        }}
                    ''')
                    if element:
                        logger.info(f"Found button using JavaScript selector: {selector}")
                        return await page.query_selector(selector)
                except Exception as e:
                    logger.debug(f"JS selector {selector} failed: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"JavaScript strategy failed: {str(e)}")
            return None

    async def _try_direct_click(self, button) -> bool:
        """Try direct click with retry."""
        max_retries = 3
        for i in range(max_retries):
            try:
                await button.click()
                return True
            except Exception as e:
                if i < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                logger.debug(f"Direct click failed: {str(e)}")
        return False

    async def _try_force_click(self, button) -> bool:
        """Try force click with position."""
        try:
            await button.click(force=True, position={'x': 0, 'y': 0})
            return True
        except Exception as e:
            logger.debug(f"Force click failed: {str(e)}")
            return False

    async def _try_js_click(self, button) -> bool:
        """Try JavaScript click."""
        try:
            await self.page.evaluate('''
                (element) => {
                    element.click();
                    element.dispatchEvent(new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    }));
                }
            ''', button)
            return True
        except Exception as e:
            logger.debug(f"JavaScript click failed: {str(e)}")
            return False

    async def _try_coordinate_click(self, button) -> bool:
        """Try click by coordinates."""
        try:
            box = await button.bounding_box()
            if box:
                x = box['x'] + box['width'] / 2
                y = box['y'] + box['height'] / 2
                await self.page.mouse.click(x, y)
                return True
        except Exception as e:
            logger.debug(f"Coordinate click failed: {str(e)}")
            return False

    async def _try_click_button(self, button) -> bool:
        """Try multiple methods to click the button."""
        click_methods = [
            self._try_direct_click,
            self._try_force_click,
            self._try_js_click,
            self._try_coordinate_click
        ]

        for i, method in enumerate(click_methods, 1):
            try:
                # Verify button is still attached
                if await self.page.evaluate('(element) => document.contains(element)', button):
                    if await method(button):
                        logger.info(f"Successfully clicked button using method {i}")
                        # Wait and verify the click worked
                        await asyncio.sleep(2)
                        post_click_check = await self._verify_join_click()
                        if post_click_check:
                            return True
                else:
                    logger.warning("Button is no longer attached to DOM, refreshing...")
                    # Try to find the button again
                    new_button = await self._try_find_button_by_selectors(self.page)
                    if new_button:
                        button = new_button
                        continue
            except Exception as e:
                logger.warning(f"Click method {i} failed: {str(e)}")
                continue

        return False

    async def _verify_join_click(self) -> bool:
        """Verify that the join click was successful."""
        try:
            # Check for elements that indicate we're in the meeting
            indicators = [
                'button[aria-label*="leave"]',
                'button[aria-label*="Leave"]',
                'button[aria-label*="camera"]',
                'button[aria-label*="microphone"]'
            ]
            
            for indicator in indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=5000)
                    if element:
                        logger.info(f"Found post-join indicator: {indicator}")
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.warning(f"Failed to verify join click: {str(e)}")
            return False

    async def join_meeting(self, meeting_code: str) -> bool:
        """Join a Google Meet meeting using the meeting code."""
        try:
            # Find the meeting in calendar events
            meeting = await self._find_meeting_by_code(meeting_code)
            if not meeting:
                logger.error(f"Meeting not found with code: {meeting_code}")
                return False
            
            # Initialize Playwright
            logger.info("Initializing Playwright...")
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False,  # Set to True in production
                args=['--use-fake-ui-for-media-stream']  # Auto-allow camera/mic
            )
            self.context = await self.browser.new_context(
                permissions=['camera', 'microphone']
            )
            self.page = await self.context.new_page()
            
            # First, sign in to Google
            logger.info("Navigating to Google sign-in page...")
            await self.page.goto('https://accounts.google.com/signin')
            
            # Enter email
            logger.info("Entering email...")
            await self.page.fill('input[type="email"]', self.google_account.get('email', ''))
            await self.page.click('button:has-text("Next")')
            
            # Wait for password field and enter password
            logger.info("Waiting for password field...")
            await self.page.wait_for_selector('input[type="password"]', timeout=30000)
            logger.info("Entering password...")
            await self.page.fill('input[type="password"]', self.google_account.get('password', ''))
            await self.page.click('button:has-text("Next")')
            
            # Wait for sign-in to complete
            logger.info("Waiting for sign-in to complete...")
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # Additional wait after sign-in
            
            # Now join the meeting
            logger.info(f"Navigating to meeting: {meeting_code}")
            await self.page.goto(f'https://meet.google.com/{meeting_code}')
            
            # Wait for the page to load completely
            logger.info("Waiting for page to load...")
            await self.page.wait_for_load_state('domcontentloaded')
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)  # Additional wait to ensure page is fully loaded
            
            # Take multiple screenshots for debugging
            await self.page.screenshot(path="meet_page_initial.png")
            logger.info("Saved initial page screenshot to meet_page_initial.png")
            
            # Advanced debugging: Get page content and log it
            page_content = await self.page.content()
            with open('page_content.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            logger.info("Saved page content to page_content.html")
            
            # Try each strategy to find the join button
            join_button = None
            strategies = [
                self._try_find_button_by_text,
                self._try_find_button_by_selectors,
                self._try_find_button_by_javascript
            ]
            
            for i, strategy in enumerate(strategies, 1):
                try:
                    join_button = await strategy(self.page)
                    if join_button:
                        logger.info(f"Successfully found button using strategy {i}")
                        break
                except Exception as e:
                    logger.warning(f"Strategy {i} failed: {str(e)}")
            
            if not join_button:
                # Final attempt: Try to find any clickable element that might be the join button
                logger.info("Trying final fallback strategy...")
                elements = await self.page.query_selector_all('button, span, div[role="button"]')
                for element in elements:
                    try:
                        properties = {
                            'text': await element.text_content(),
                            'aria-label': await element.get_attribute('aria-label'),
                            'class': await element.get_attribute('class'),
                            'jsname': await element.get_attribute('jsname'),
                            'role': await element.get_attribute('role')
                        }
                        logger.info(f"Found element with properties: {properties}")
                        
                        # Check if this element matches our criteria
                        text = properties['text'].lower() if properties['text'] else ''
                        if ('ask' in text and 'join' in text) or properties['jsname'] == 'V67aGc':
                            join_button = element
                            logger.info("Found potential join button in final fallback")
                            break
                    except Exception:
                        continue
            
            # Take another screenshot after finding (or not finding) the button
            await self.page.screenshot(path="meet_page_before_click.png")
            logger.info("Saved pre-click screenshot to meet_page_before_click.png")
            
            if join_button:
                logger.info("Attempting to click the join button...")
                if await self._try_click_button(join_button):
                    logger.info("Successfully clicked join button")
                else:
                    logger.error("Failed to click join button after all attempts")
                    return False
            else:
                logger.error("Could not find join button using any strategy")
                return False
            
            # Wait for the meeting interface to load after clicking join
            logger.info("Waiting for meeting interface to load after joining...")
            await asyncio.sleep(5)  # Wait for initial load
            
            # Try to find any of these elements that indicate we're in the meeting
            meeting_selectors = [
                'div[role="main"]',
                'button[aria-label*="camera"]',
                'button[aria-label*="microphone"]',
                'button[aria-label*="leave"]',
                'button[aria-label*="Leave"]'
            ]
            
            meeting_loaded = False
            for selector in meeting_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=30000)
                    logger.info(f"Found meeting element: {selector}")
                    meeting_loaded = True
                    break
                except Exception:
                    continue
            
            if not meeting_loaded:
                logger.warning("Could not confirm meeting interface loaded, but continuing...")
            
            # Now try to turn off camera and microphone
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Look for camera button with multiple selectors
                    camera_selectors = [
                        'button[aria-label*="camera"]',
                        'button[aria-label*="Camera"]',
                        'button[jscontroller="VXdfxd"]',
                        'button[jscontroller="soHxf"]'
                    ]
                    
                    camera_button = None
                    for selector in camera_selectors:
                        try:
                            camera_button = await self.page.wait_for_selector(selector, timeout=10000)
                            if camera_button:
                                break
                        except Exception:
                            continue
                    
                    if camera_button:
                        camera_label = await camera_button.get_attribute('aria-label')
                        if 'on' in camera_label.lower():
                            logger.info("Turning off camera...")
                            await camera_button.click()
                            await asyncio.sleep(1)
                    
                    # Look for microphone button with multiple selectors
                    mic_selectors = [
                        'button[aria-label*="microphone"]',
                        'button[aria-label*="Microphone"]',
                        'button[jscontroller="VXdfxd"]',
                        'button[jscontroller="soHxf"]'
                    ]
                    
                    mic_button = None
                    for selector in mic_selectors:
                        try:
                            mic_button = await self.page.wait_for_selector(selector, timeout=10000)
                            if mic_button:
                                break
                        except Exception:
                            continue
                    
                    if mic_button:
                        mic_label = await mic_button.get_attribute('aria-label')
                        if 'on' in mic_label.lower():
                            logger.info("Turning off microphone...")
                            await mic_button.click()
                            await asyncio.sleep(1)
                    
                    break  # If successful, break the retry loop
                    
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Attempt {retry_count} failed to turn off camera/mic: {str(e)}")
                    if retry_count == max_retries:
                        logger.warning("Failed to turn off camera/microphone, but continuing with join process")
                        break
                    await asyncio.sleep(2)
            
            # Update the meeting to indicate bot's presence
            logger.info("Updating meeting description...")
            await self._join_meeting_session(meeting)
            
            # Store the current meeting
            self.current_meeting = meeting
            
            # Take a final screenshot
            await self.page.screenshot(path="meet_page_after_join.png")
            logger.info("Saved post-join screenshot to meet_page_after_join.png")
            
            logger.info(f"Successfully joined Google Meet with code: {meeting_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join Google Meet: {str(e)}")
            await self._cleanup()
            return False
    
    async def leave_meeting(self) -> bool:
        """Leave the current Google Meet meeting."""
        try:
            if self.page and self.current_meeting:
                # Click leave button
                leave_button = await self.page.wait_for_selector('button[aria-label*="leave"]')
                await leave_button.click()
                
                # Update the meeting to indicate bot's departure
                await self._leave_meeting_session()
                
                await self._cleanup()
                self.current_meeting = None
                logger.info("Successfully left Google Meet")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to leave Google Meet: {str(e)}")
            await self._cleanup()
            return False
    
    async def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def _find_meeting_by_code(self, meeting_code: str) -> Optional[Dict]:
        """Find a meeting in calendar events by its meeting code."""
        try:
            # Get events from 24 hours ago to 24 hours from now
            now = datetime.utcnow()
            time_min = now - timedelta(days=1)
            time_max = now + timedelta(days=1)
            
            # List calendar events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Find the event with matching meet code
            for event in events:
                conference_data = event.get('conferenceData', {})
                if conference_data:
                    entry_points = conference_data.get('entryPoints', [])
                    for entry in entry_points:
                        if entry.get('uri', '').endswith(meeting_code):
                            logger.info(f"Found meeting: {event['summary']}")
                            return event
            
            return None
        except Exception as e:
            logger.error(f"Failed to find meeting: {str(e)}")
            raise
    
    async def _join_meeting_session(self, meeting: Dict) -> Dict:
        """Join a meeting session."""
        try:
            # Update the meeting to indicate bot's presence
            event = self.service.events().patch(
                calendarId='primary',
                eventId=meeting['id'],
                body={
                    'description': f"{meeting.get('description', '')} \n\nBot has joined the meeting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ).execute()
            return event
        except HttpError as e:
            logger.error(f"Failed to join meeting session: {str(e)}")
            raise
    
    async def _leave_meeting_session(self) -> None:
        """Leave a meeting session."""
        try:
            if self.current_meeting:
                # Update the meeting to indicate bot's departure
                self.service.events().patch(
                    calendarId='primary',
                    eventId=self.current_meeting['id'],
                    body={
                        'description': f"{self.current_meeting.get('description', '')} \n\nBot has left the meeting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ).execute()
        except HttpError as e:
            logger.error(f"Failed to leave meeting session: {str(e)}")
            raise
    
    @property
    def meeting_id(self) -> Optional[str]:
        """Get the current meeting ID."""
        return self.current_meeting['id'] if self.current_meeting else None 