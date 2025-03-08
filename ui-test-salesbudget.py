import pytest
from playwright.async_api import async_playwright, expect
import asyncio
import logging
import os
import datetime


class EmojiFormatter(logging.Formatter):
    """Кастомный форматтер для добавления эмодзи в зависимости от уровня логов."""
    LEVEL_EMOJIS = {
        logging.DEBUG: "ℹ️",
        logging.INFO: "✅",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }

    def format(self, record):
        emoji = self.LEVEL_EMOJIS.get(record.levelno, "")
        record.msg = f"{emoji} {record.msg}"
        return super().format(record)

# Настроим логгер
logger = logging.getLogger("emoji_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(EmojiFormatter("%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S"))
logger.addHandler(console_handler)


# чтобы папка (для видео) создавалась автоматически при запуске тестов
@pytest.fixture(scope="session", autouse=True)
def create_video_folder():
    os.makedirs("videos", exist_ok=True)



@pytest.mark.asyncio
async def login_to_site(page):
    """Метод для авторизации на сайте."""
    try:
        await page.goto("https://url/")
        
        login = page.locator('//*[@id="username"]')
        await login.click()
        await login.fill("Admin1")
        await login.press("Enter")
        print("\n") # новая строка (для абзаца)
        logger.info("Логин введен.")

        password = page.locator('//*[@id="password"]')
        await password.click()
        await password.fill("password")
        await password.press("Enter")
        logger.info("Пароль введен.")

    except Exception as e:
        logger.error(f"Логин или Пароль не введены: {e}")
        pytest.fail(f"Логин или Пароль не введены: {e}")

    await asyncio.sleep(2)

    try:
        #button_login = page.locator('//span[text()="Login"]')
        button_login = page.get_by_role("button", name="Login")
        #await button_login.wait_for(timeout=4000)
        await button_login.wait_for(state="visible", timeout=4000)  # Ожидание появления кнопки      
        await button_login.click()
        logger.info("Кнопка Login нажата.")
    except Exception as e:
        logger.error(f"Кнопка Login НЕ нажата: {e}")

@pytest.mark.asyncio
async def test_table_row_values():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Генерация названия файла
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        video_path = f"videos/test_run_{timestamp}"        
        
        # Создаем контекст с записью видео
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, # Разрешение экрана
            record_video_dir=video_path, # Папка для видео
            record_video_size={"width": 1920, "height": 1080} # Разрешение видео
        )
        
        page = await context.new_page()

        await login_to_site(page)

        try:
            await page.goto("https://url")
            logger.info("URL открыт.")
        except Exception as e:
            logger.error(f"URL НЕ открыт: {e}")
            pytest.fail(f"URL НЕ открыт: {e}")

       try:
            await asyncio.sleep(1)
            button = page.get_by_alt_text("EyeIcon")
            await expect(button).to_be_visible(timeout=4000)
            await button.click()
            logger.info("Список View кликнут.")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Список View НЕ кликнут: {e}")
            pytest.fail(f"Список View НЕ кликнут: {e}")

        try:
            await asyncio.sleep(1)
            checkbox = page.get_by_label("Show/Hide Existing")
            await checkbox.wait_for(timeout=4000)
            await checkbox.uncheck()
            await asyncio.sleep(1)
            logger.info("Галочка 'Show/Hide Existing' снята успешно.")
        except Exception as e:
            logger.error(f"Галочка 'Show/Hide Existing' не снята: {e}")
            pytest.fail(f"Галочка 'Show/Hide Existing' не снята: {e}")

        try:
            button_view = page.get_by_alt_text("EyeIcon")
            await button_view.wait_for(timeout=3000)
            await button_view.click()
            await asyncio.sleep(1)
            
            checkbox = page.get_by_label("Show/Hide Existing")            
            await expect(checkbox).not_to_be_visible(timeout=3000)

            logger.info("Список View кликнут и закрыт.")
        except Exception as e:
            logger.error(f"Список View не закрыт: {e}")
            pytest.fail(f"Список View не закрыт: {e}")

        await browser.close()
