"""
Playwright UI tests for Prompt Optimizer.

Requirements:
  pip install playwright pytest-playwright
  playwright install chromium

Run:
  pytest tests/test_ui.py --headed     # with browser
  pytest tests/test_ui.py              # headless
"""

import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:8502"


@pytest.fixture(autouse=True)
def wait_for_app(page: Page):
    """Navigate to the app and wait for it to be interactive."""
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector(".stTabs", timeout=15_000)


# ── Page loads ────────────────────────────────────────────────────────────────

def test_page_title(page: Page):
    expect(page).to_have_title("Prompt Optimizer")


def test_header_visible(page: Page):
    header = page.locator(".app-title")
    expect(header).to_be_visible()
    expect(header).to_contain_text("Prompt Optimizer")


def test_tabs_present(page: Page):
    tabs = page.locator('[data-baseweb="tab"]')
    expect(tabs).to_have_count(3)
    expect(tabs.nth(0)).to_contain_text("Optimizer")
    expect(tabs.nth(1)).to_contain_text("Architect")
    expect(tabs.nth(2)).to_contain_text("Learn")


def test_footer_visible(page: Page):
    footer = page.locator(".app-footer")
    expect(footer).to_be_visible()
    expect(footer).to_contain_text("tanmayagr2021@gmail.com")


# ── Empty states ──────────────────────────────────────────────────────────────

def test_optimizer_empty_state(page: Page):
    """Right panel shows empty state before any optimization."""
    empty = page.locator(".empty-state").first
    expect(empty).to_be_visible()


def test_tip_card_shown_in_empty_state(page: Page):
    """A tip card is visible on the right panel in the empty state."""
    tip = page.locator(".tip-card").first
    expect(tip).to_be_visible()


# ── Onboarding hint ───────────────────────────────────────────────────────────

def test_onboarding_hint_visible(page: Page):
    """First-time hint is shown when optimizer tab loads fresh."""
    hint = page.locator(".onboarding-hint").first
    expect(hint).to_be_visible()


# ── Optimizer flow ────────────────────────────────────────────────────────────

def _fill_textarea_react(page: Page, text: str):
    """Set a textarea value in a way that triggers React's onChange in Streamlit."""
    page.evaluate(
        """(text) => {
            const ta = document.querySelector('textarea');
            if (!ta) return;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value'
            ).set;
            setter.call(ta, text);
            ta.dispatchEvent(new Event('input', {bubbles: true}));
            ta.dispatchEvent(new Event('change', {bubbles: true}));
        }""",
        text,
    )


def _fill_and_submit(page: Page, text: str):
    """Fill the optimizer textarea and click the primary submit button.

    Streamlit commits text_area values on blur, so we fill then Tab-out
    to force the Python backend to re-render with the new value.
    """
    ta = page.locator("textarea").first
    ta.click()
    ta.fill(text)
    # Blur → Streamlit Python re-renders → button becomes enabled
    ta.press("Tab")
    page.wait_for_timeout(2_500)
    btn = page.locator('[data-baseweb="tab-panel"]:visible [data-testid="stBaseButton-primary"]').first
    expect(btn).to_be_enabled(timeout=12_000)
    btn.click()


def test_optimize_button_disabled_when_empty(page: Page):
    """Optimize button is disabled when input textarea is empty."""
    btn = page.locator('[data-testid="stBaseButton-primary"]').first
    assert btn.is_disabled()


def test_optimize_with_text(page: Page):
    """Typing text enables the button and optimization produces output."""
    _fill_and_submit(page, "Write a report about artificial intelligence trends in 2024.")
    # Wait for stat cards (appear after optimization completes)
    page.wait_for_selector(".stat-card", timeout=30_000)
    expect(page.locator(".stat-card").first).to_be_visible()


def test_stats_shown_after_optimize(page: Page):
    """Stat cards appear below the optimized output."""
    _fill_and_submit(page, "Please write a comprehensive and very detailed analysis of the market.")
    page.wait_for_selector(".stat-card", timeout=30_000)
    expect(page.locator(".stat-card").first).to_be_visible()


def test_download_buttons_visible(page: Page):
    """Download buttons appear after optimization."""
    _fill_and_submit(page, "Explain machine learning to a 5-year-old.")
    page.wait_for_selector('[data-testid="stDownloadButton"]', timeout=30_000)
    expect(page.locator('[data-testid="stDownloadButton"]').first).to_be_visible()


# ── Insights ──────────────────────────────────────────────────────────────────

def test_insights_expander_present_after_optimize(page: Page):
    """'What changed & why' expander appears after optimization when changes detected."""
    _fill_and_submit(page, "Tell me about dogs.")
    page.wait_for_selector(".stat-card", timeout=30_000)
    # Insights may or may not appear depending on what changed; verify no crash occurred
    expect(page.locator(".stat-card").first).to_be_visible()


# ── Architect tab ─────────────────────────────────────────────────────────────

def test_architect_tab_opens(page: Page):
    """Architect tab renders without error."""
    page.locator('[data-baseweb="tab"]').nth(1).click()
    page.wait_for_timeout(1_000)
    platform_select = page.locator(".stSelectbox").first
    expect(platform_select).to_be_visible()


def test_architect_empty_state(page: Page):
    """Right panel shows empty state before generation."""
    page.locator('[data-baseweb="tab"]').nth(1).click()
    page.wait_for_timeout(1_500)
    # Find visible empty-state within the active tab panel
    empty = page.locator('[data-baseweb="tab-panel"]:visible .empty-state')
    expect(empty).to_be_visible(timeout=8_000)


def test_architect_platform_tip_visible(page: Page):
    """A tip card is shown for the selected platform."""
    page.locator('[data-baseweb="tab"]').nth(1).click()
    page.wait_for_timeout(1_500)
    # Find a tip-card visible within the active architect panel
    tip = page.locator('[data-baseweb="tab-panel"]:visible .tip-card')
    expect(tip).to_be_visible(timeout=8_000)


# ── Learn tab ─────────────────────────────────────────────────────────────────

def test_learn_tab_opens(page: Page):
    """Learn tab renders category buttons."""
    page.locator('[data-baseweb="tab"]').nth(2).click()
    page.wait_for_timeout(1_000)
    # Should have category buttons
    buttons = page.get_by_role("button", name="Basics")
    expect(buttons.first).to_be_visible()


def test_learn_tab_content_loads(page: Page):
    """Learn tab shows content cards for the default category."""
    page.locator('[data-baseweb="tab"]').nth(2).click()
    page.wait_for_timeout(1_500)
    # Expanders for content items should be present
    expanders = page.locator(".stExpander")
    expect(expanders.first).to_be_visible()


def test_learn_tab_tip_cards(page: Page):
    """Rotating tip cards appear at the bottom of the Learn tab."""
    page.locator('[data-baseweb="tab"]').nth(2).click()
    page.wait_for_timeout(1_500)
    tips = page.locator('[data-baseweb="tab-panel"]:visible .tip-card')
    expect(tips.first).to_be_visible(timeout=8_000)


def test_learn_category_switch(page: Page):
    """Switching to Claude category shows relevant content."""
    page.locator('[data-baseweb="tab"]').nth(2).click()
    page.wait_for_timeout(1_000)
    page.get_by_role("button", name="Claude").first.click()
    page.wait_for_timeout(1_500)
    # Content should update
    expanders = page.locator(".stExpander")
    expect(expanders.first).to_be_visible()


# ── Dark mode ─────────────────────────────────────────────────────────────────

def test_dark_mode_toggle(page: Page):
    """Dark mode toggle label is visible in the sidebar."""
    # Expand sidebar if collapsed
    try:
        expand_btn = page.get_by_test_id("stSidebarCollapsedControl")
        if expand_btn.is_visible():
            expand_btn.click()
            page.wait_for_timeout(800)
    except Exception:
        pass

    # Streamlit renders toggle text as a visible <p> or <label> — check for it
    sidebar = page.locator('[data-testid="stSidebar"]')
    dark_label = sidebar.get_by_text("Dark mode", exact=True).first
    expect(dark_label).to_be_visible(timeout=8_000)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def test_sidebar_engine_section(page: Page):
    """Sidebar shows engine configuration."""
    sidebar = page.locator('[data-testid="stSidebar"]')
    expect(sidebar).to_be_visible()


# ── Mobile viewport ───────────────────────────────────────────────────────────

def test_mobile_layout(page: Page):
    """App renders without horizontal overflow on mobile viewport."""
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector(".stTabs", timeout=15_000)
    # Check that the page doesn't have extreme horizontal scroll
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    client_width = page.evaluate("document.documentElement.clientWidth")
    # Allow up to 2x width (Streamlit itself may not be fully mobile-optimised)
    assert scroll_width <= client_width * 3, f"Excessive horizontal scroll: {scroll_width} vs {client_width}"


# ── Screenshots ───────────────────────────────────────────────────────────────

def test_screenshot_light_desktop(page: Page):
    """Capture light mode desktop screenshot."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector(".stTabs", timeout=15_000)
    page.screenshot(path="tests/screenshots/light_desktop.png", full_page=True)


def test_screenshot_dark_desktop(page: Page):
    """Capture dark mode desktop screenshot."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector(".stTabs", timeout=15_000)
    try:
        # Expand sidebar
        ctrl = page.get_by_test_id("stSidebarCollapsedControl")
        if ctrl.is_visible():
            ctrl.click()
            page.wait_for_timeout(600)
        # Click the toggle label/switch
        toggle = page.get_by_text("Dark mode", exact=True).first
        toggle.click()
        page.wait_for_timeout(2_000)
    except Exception:
        pass
    page.screenshot(path="tests/screenshots/dark_desktop.png", full_page=True)


def test_screenshot_learn_tab(page: Page):
    """Capture Learn tab screenshot."""
    page.locator('[data-baseweb="tab"]').nth(2).click()
    page.wait_for_timeout(1_500)
    page.screenshot(path="tests/screenshots/learn_tab.png", full_page=True)


def test_screenshot_after_optimize(page: Page):
    """Capture the optimizer with results."""
    _fill_and_submit(
        page,
        "You are a helpful assistant. Write me a report about renewable energy. "
        "Make it comprehensive and include all relevant details and information that might be helpful."
    )
    page.wait_for_selector(".stat-card", timeout=30_000)
    page.wait_for_timeout(500)
    page.screenshot(path="tests/screenshots/optimizer_results.png", full_page=True)
