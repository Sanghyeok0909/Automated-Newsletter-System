import os
import sys
import re
from bs4 import BeautifulSoup

def test_html_file(filepath):
    print(f"--- Testing {filepath} ---")
    assert os.path.exists(filepath), f"File {filepath} does not exist!"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Removal checks
    # The five redundant circular icons in the rail:
    # Check that .global-rail does NOT contain the 5 publisher buttons
    soup = BeautifulSoup(content, "html.parser")
    rail = soup.find("nav", class_="global-rail")
    assert rail is not None, "nav.global-rail not found!"
    rail_buttons = rail.find_all("button")
    print(f"Rail buttons count: {len(rail_buttons)}")
    assert len(rail_buttons) == 1, f"Expected exactly 1 button in global-rail, found {len(rail_buttons)}"
    assert "⚡" in rail_buttons[0].text, "Home button does not contain ⚡"
    assert "resetAllFilters" in rail_buttons[0].get("onclick", ""), "Home button missing resetAllFilters"
    assert soup.find("div", class_="rail-divider") is None, "rail-divider should be removed"

    # 2. Publisher channels preservation
    sidebar = soup.find("aside", class_="context-sidebar")
    assert sidebar is not None, "aside.context-sidebar not found!"
    channels = sidebar.find_all("button", class_="channel-item")
    print(f"Channel items count: {len(channels)}")
    # 1 '오늘의 브리핑' + 5 publishers = 6 channel items
    assert len(channels) == 6, f"Expected 6 channel items (1 briefing + 5 publishers), found {len(channels)}"
    expected_publishers = ["The Verge", "TechCrunch", "Ars Technica", "MIT Tech Review", "The Information"]
    for pub in expected_publishers:
        assert any(pub in ch.text for ch in channels), f"Publisher channel '{pub}' not found in sidebar!"

    # 3. Article cards integrity
    cards = soup.find_all("article", class_="toss-card")
    print(f"Article cards count: {len(cards)}")
    assert len(cards) == 10, f"Expected 10 article cards, found {len(cards)}"

    # Check each card has headline, summary, insight, link, media avatar
    for idx, card in enumerate(cards):
        headline = card.find("h2", class_="card-headline")
        assert headline and len(headline.text.strip()) > 0, f"Card {idx+1} missing headline"
        summary_bullets = card.find_all("li", class_="summary-bullet")
        assert len(summary_bullets) >= 1, f"Card {idx+1} missing summary bullets"
        insight = card.find("p", class_="insight-description")
        assert insight and len(insight.text.strip()) > 0, f"Card {idx+1} missing insight"
        link_btn = card.find("a", class_="toss-pill-link")
        assert link_btn and link_btn.get("href", "").startswith("http"), f"Card {idx+1} missing valid link"
        assert link_btn.get("target") == "_blank", f"Card {idx+1} link missing target=_blank"
        assert "noopener" in link_btn.get("rel", []), f"Card {idx+1} link missing rel=noopener"
        avatar = card.find("span", class_="media-avatar")
        assert avatar and len(avatar.text.strip()) > 0, f"Card {idx+1} avatar missing meaningful letter/mark"

    # 4. Search and empty state
    search_input = soup.find("input", id="searchInput")
    assert search_input is not None, "Search input #searchInput not found!"
    empty_state = soup.find("div", id="noResultsCard")
    assert empty_state is not None, "Empty state #noResultsCard not found!"

    # 5. Metadata panel
    metadata = soup.find("aside", class_="metadata-panel")
    assert metadata is not None, "Metadata panel not found!"
    assert "매체별 기사 현황" in metadata.text, "Metadata section title should be '매체별 기사 현황'"
    assert "Zero-Capital" in metadata.text, "Zero-Capital design target label should be present"

    # 6. Toast & Mobile elements
    toast = soup.find("div", id="tossToast")
    assert toast is not None, "Toast #tossToast not found!"
    mobile_btn = soup.find("button", id="mobileMenuBtn")
    assert mobile_btn is not None, "Mobile menu button #mobileMenuBtn not found!"
    backdrop = soup.find("div", id="drawerBackdrop")
    assert backdrop is not None, "Drawer backdrop #drawerBackdrop not found!"

    print(f"PASS: {filepath} meets all strict requirements!")

if __name__ == "__main__":
    test_html_file("dist/index.html")
    test_html_file("dist/newsletter-2026-09-18.html")
    print("\nALL TESTS PASSED SUCCESSFULLY!")
