"""Headless-browser checks of the real pages at phone, tablet and laptop widths,
including live updates arriving on an open page."""

import json
import re
import threading
import urllib.request

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import expect, sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from conftest import (ADMIN, API_KEY, CARER, SAMPLE_FILE, add_users, ago, fall, gait, load,  # noqa: E402
                      make_app, patient, payload, seed_events)
from sage_dashboard import queries  # noqa: E402

WIDTHS = {"phone": 360, "tablet": 768, "laptop": 1440}
FAST_LIVE = {"LIVE_CHECK_SECONDS": 0.3, "LIVE_RETRY_MS": 300, "LIVE_POLL_MS": 500}


class LiveServer:
    def __init__(self, db_path, seed=None, setup=True, **overrides):
        if setup:
            queries.create_database(db_path)
            add_users(db_path)
            conn = queries.connect(db_path)
            for raw in seed or []:
                load(conn, raw)
            conn.close()
        app = make_app(db_path, TESTING=False, **{**FAST_LIVE, **overrides})
        self.server = make_server("127.0.0.1", 0, app, threaded=True)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def post_event(self, body):
        req = urllib.request.Request(self.url + "/api/events", data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status

    def stop(self):
        self.server.shutdown()
        self.thread.join(5)


def standard_seed():
    return [payload(seed_events(), patients=[patient("P001", "Amina Rahman"),
                                             patient("P002", "Yusuf Rahman", 84, "Upstairs bedroom")])]


def one_person_no_events():
    return [payload([], patients=[patient("P001", "Amina Rahman")])]


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        yield b
        b.close()


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    s = LiveServer(tmp_path_factory.mktemp("ui") / "ui.sqlite3", standard_seed())
    yield s
    s.stop()


@pytest.fixture
def fresh_server(tmp_path):
    servers = []

    def make(seed=None, **overrides):
        s = LiveServer(tmp_path / f"fresh{len(servers)}.sqlite3", seed, **overrides)
        servers.append(s)
        return s
    yield make
    for s in servers:
        s.stop()


@pytest.fixture(params=list(WIDTHS), ids=list(WIDTHS))
def width(request):
    return WIDTHS[request.param]


def sign_in(page, base, user=ADMIN):
    page.goto(base + "/login")
    page.fill("#username", user["username"])
    page.fill("#password", user["password"])
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator(".user-name")).to_contain_text(user["name"])


@pytest.fixture
def page_at(browser):
    contexts, external = [], []

    def make(width, base=None, user=ADMIN, height=900, init_script=None):
        context = browser.new_context(viewport={"width": width, "height": height})
        if init_script:
            context.add_init_script(init_script)
        page = context.new_page()
        page.on("request", lambda req: external.append(req.url)
                if not req.url.startswith("http://127.0.0.1:") else None)
        contexts.append(context)
        if base and user:
            sign_in(page, base, user)
        return page
    yield make
    for ctx in contexts:
        ctx.close()
    assert external == [], f"requests left this device: {external}"


OVERFLOW_JS = """() => {
  const w = document.documentElement.clientWidth;
  const bad = [];
  if (document.documentElement.scrollWidth > w) bad.push('page scrollWidth ' + document.documentElement.scrollWidth + ' > ' + w);
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (el.closest('.visually-hidden, .skip-link, thead')) continue;
    if (r.right > w + 1 || r.left < -1) bad.push(el.tagName + '.' + el.className + ' [' + Math.round(r.left) + ', ' + Math.round(r.right) + ']');
  }
  return bad;
}"""

SMALL_TARGETS_JS = """() => [...document.querySelectorAll('a, button, select, input:not([type=hidden]), summary, label.checkbox, label.radio')]
  .filter(el => !el.classList.contains('skip-link'))
  .map(el => [el, el.getBoundingClientRect()])
  .filter(([el, r]) => (r.width || r.height) && (r.height < 44 || r.width < 44))
  .filter(([el]) => !(el.tagName === 'INPUT' && ['checkbox', 'radio'].includes(el.type) && el.closest('label')))
  .map(([el, r]) => el.tagName + ' "' + el.textContent.trim().slice(0, 30) + '" ' + Math.round(r.width) + 'x' + Math.round(r.height))"""

TEXT_SIZE_JS = """() => {
  const bad = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.textContent.trim()) continue;
    const el = node.parentElement;
    if (el.closest('.visually-hidden, script, style, noscript, option, [hidden]')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const size = parseFloat(getComputedStyle(el).fontSize);
    if (size < 16) bad.push(el.tagName + ' ' + size + 'px "' + node.textContent.trim().slice(0, 30) + '"');
  }
  return bad;
}"""

CONTRAST_JS = """() => {
  const parse = c => { const m = c.match(/[\\d.]+/g).map(Number); return {r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
                     return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const background = el => { for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c.a > 0.5) return c; } return {r: 255, g: 255, b: 255, a: 1}; };
  const bad = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.textContent.trim()) continue;
    const el = node.parentElement;
    if (el.closest('.visually-hidden, script, style, noscript, option, [hidden], .skip-link')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const s = getComputedStyle(el);
    const fg = parse(s.color), bg = background(el);
    const [hi, lo] = [lum(fg), lum(bg)].sort((a, b) => b - a);
    const ratio = (hi + 0.05) / (lo + 0.05);
    const size = parseFloat(s.fontSize), bold = parseInt(s.fontWeight, 10) >= 700;
    const needed = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
    if (ratio < needed) bad.push('"' + node.textContent.trim().slice(0, 30) + '" ' + ratio.toFixed(2));
  }
  return bad;
}"""


def check_page_quality(page):
    assert page.evaluate(OVERFLOW_JS) == []
    assert page.evaluate(SMALL_TARGETS_JS) == []
    assert page.evaluate(TEXT_SIZE_JS) == []
    assert page.evaluate(CONTRAST_JS) == []


PAGES = {
    "home": "/",
    "overview": "/patients/1",
    "overview-empty": "/patients/2",
    "events": "/patients/1/events",
    "events-no-match": "/patients/1/events?from=2001-01-01&to=2001-01-02",
    "events-bad-filter": "/patients/1/events?type=trip",
    "import": "/import",
    "users": "/users",
    "help": "/help",
    "not-found": "/nothing-here",
}


@pytest.mark.parametrize("path", list(PAGES.values()), ids=list(PAGES))
def test_layout_fits_readable_and_touch_friendly(server, page_at, width, path):
    page = page_at(width, server.url)
    page.goto(server.url + path)
    check_page_quality(page)


def test_login_page_layout(server, page_at, width):
    page = page_at(width, user=None)
    page.goto(server.url + "/login")
    expect(page.get_by_role("heading", name="Sign in")).to_be_visible()
    check_page_quality(page)
    page.fill("#username", "anna")
    page.fill("#password", "wrong")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("alert")).to_contain_text("couldn’t sign you in")
    check_page_quality(page)


def test_setup_page_layout(tmp_path, page_at, width):
    s = LiveServer(tmp_path / "missing.sqlite3", setup=False)
    try:
        page = page_at(width, user=None)
        page.goto(s.url + "/")
        expect(page.get_by_role("heading", name="This dashboard is not ready yet")).to_be_visible()
        check_page_quality(page)
    finally:
        s.stop()


def test_open_panels_still_fit(server, page_at, width):
    page = page_at(width, server.url)
    page.goto(server.url + "/patients/1?range=all")
    page.get_by_text("Show this as a list").click()
    expect(page.locator(".trend-numbers table")).to_be_visible()
    check_page_quality(page)
    page.goto(server.url + "/help")
    for summary in page.locator(".faq summary").all():
        summary.click()
    check_page_quality(page)


def test_text_is_not_tiny_on_wide_screens(server, page_at):
    page = page_at(1440, server.url)
    page.goto(server.url + "/patients/1")
    assert float(page.evaluate("getComputedStyle(document.body).fontSize").rstrip("px")) >= 17
    assert page.evaluate(TEXT_SIZE_JS) == []


def test_glance_answers_the_two_questions(server, page_at, width):
    page = page_at(width, server.url)
    page.goto(server.url + "/patients/1")
    box = page.locator("#live-summary")
    expect(box).to_contain_text("Needs your attention")
    expect(box.locator(".glance-headline")).to_have_text("Amina may need you now.")
    expect(box.locator(".steps li")).to_have_count(3)
    # it is the first thing on the page
    assert box.bounding_box()["y"] < 400


def test_legend_and_not_available_cards(server, page_at, width):
    page = page_at(width, server.url)
    page.goto(server.url + "/patients/1")
    legend = page.locator(".legend")
    for label in ("Urgent", "Worth a look", "For information"):
        expect(legend).to_contain_text(label)
    expect(legend).to_contain_text("Check on them straight away.")
    for feature, heading in (("sleep", "Sleep"), ("medication", "Medicines")):
        card = page.locator(f'[data-feature="{feature}"]')
        expect(card.locator("h2")).to_have_text(heading)
        expect(card).to_contain_text("Not available yet")


def test_trend_chart_renders(server, page_at, width):
    page = page_at(width, server.url)
    page.goto(server.url + "/patients/1?range=all")
    svg = page.locator("svg.trend-svg")
    expect(svg).to_be_visible()
    assert page.locator(".trend-dot").count() == 4
    box = svg.bounding_box()
    assert box["width"] > 150 and box["height"] > 100


def test_table_becomes_cards_on_phone(server, page_at):
    phone = page_at(360, server.url)
    phone.goto(server.url + "/patients/1/events")
    row = phone.locator("tr.event-row").first
    assert row.evaluate("el => getComputedStyle(el).display") == "flex"
    assert phone.locator("thead").bounding_box()["height"] <= 1
    laptop = page_at(1440, server.url)
    laptop.goto(server.url + "/patients/1/events")
    assert laptop.locator("tr.event-row").first.evaluate("el => getComputedStyle(el).display") == "table-row"


@pytest.mark.parametrize("w", [360, 1440])
def test_filters(server, page_at, w):
    page = page_at(w, server.url)
    page.goto(server.url + "/patients/1/events")
    rows = page.locator("tr.event-row")
    expect(rows).to_have_count(6)
    page.select_option("#f-type", "fall")
    page.get_by_role("button", name="Show", exact=True).click()
    expect(rows).to_have_count(2)
    assert {rows.nth(i).get_attribute("data-type") for i in range(2)} == {"fall"}
    expect(page.locator(".results-count")).to_have_text("2 things match your choices")
    page.select_option("#f-type", "")
    page.select_option("#f-severity", "high")
    page.get_by_role("button", name="Show", exact=True).click()
    expect(rows).to_have_count(2)
    page.get_by_role("link", name="Show everything").click()
    expect(rows).to_have_count(6)


def test_date_filter_and_empty_state(server, page_at):
    page = page_at(768, server.url)
    page.goto(server.url + "/patients/1/events")
    page.fill("#f-from", "2001-01-01")
    page.fill("#f-to", "2001-01-31")
    page.get_by_role("button", name="Show", exact=True).click()
    expect(page.get_by_text("Nothing matches these choices")).to_be_visible()
    page.fill("#f-from", "2001-02-01")
    page.get_by_role("button", name="Show", exact=True).click()
    expect(page.get_by_role("alert")).to_contain_text("is after the")


def test_empty_states(server, fresh_server, page_at):
    page = page_at(360, server.url)
    page.goto(server.url + "/patients/2")
    expect(page.locator("#live-summary")).to_contain_text("No news about Yusuf yet.")
    expect(page.get_by_text("Yusuf has not been seen walking in this time.")).to_be_visible()
    empty = fresh_server()
    page2 = page_at(360, empty.url)
    expect(page2.get_by_role("heading", name="Welcome to S.A.G.E.")).to_be_visible()


def test_navigation(server, page_at, width):
    page = page_at(width, server.url)
    page.goto(server.url + "/")
    expect(page.get_by_role("heading", level=2, name="The people you look after")).to_be_visible()
    page.get_by_role("link", name="Amina Rahman").click()
    expect(page).to_have_url(server.url + "/patients/1")
    page.get_by_role("link", name="Everything so far").click()
    expect(page.get_by_role("link", name="Everything so far")).to_have_attribute("aria-current", "page")
    nav = page.get_by_role("navigation", name="Main")
    nav.get_by_role("link", name="Help").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("How to use this page")
    nav.get_by_role("link", name="Add results").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Add results")
    nav.get_by_role("link", name="Who can sign in").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Who can sign in")
    nav.get_by_role("link", name="Home").click()
    expect(page).to_have_url(server.url + "/")
    page.get_by_role("button", name="Sign out").click()
    expect(page.get_by_role("heading", name="Sign in")).to_be_visible()
    expect(page.get_by_text("You have signed out.")).to_be_visible()


def test_caregiver_sees_no_manager_pages(server, page_at):
    page = page_at(768, server.url, user=CARER)
    nav = page.get_by_role("navigation", name="Main")
    expect(nav.get_by_role("link", name="Add results")).to_have_count(0)
    page.goto(server.url + "/import")
    expect(page.get_by_role("heading", level=1)).to_have_text("Only the manager can do this")


def test_keyboard_focus_is_visible(server, page_at):
    page = page_at(1440, server.url)
    page.goto(server.url + "/patients/1")
    page.keyboard.press("Tab")
    expect(page.locator(".skip-link")).to_be_focused()
    page.keyboard.press("Tab")
    style = page.evaluate("() => { const s = getComputedStyle(document.activeElement); return [s.outlineStyle, s.outlineWidth]; }")
    assert style[0] != "none" and style[1] != "0px"


def test_check_and_undo_with_keyboard_only(fresh_server, page_at):
    s = fresh_server(standard_seed())
    page = page_at(360, s.url)
    page.goto(s.url + "/patients/1")
    buttons = page.get_by_role("button", name=re.compile("I’ve checked on Amina"))
    expect(buttons).to_have_count(4)
    for _ in range(60):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.id").startswith("check-"):
            break
    else:
        pytest.fail("could not reach a check button with the keyboard")
    page.keyboard.press("Enter")
    expect(page.locator(".notice-success")).to_contain_text("marked as checked on Amina")
    expect(buttons).to_have_count(3)
    page.locator(".notice-success").get_by_role("button", name="Undo").focus()
    page.keyboard.press("Enter")
    expect(page.locator(".notice-success")).to_contain_text("back on the list")
    expect(buttons).to_have_count(4)


def test_checking_everything_shows_all_is_well(fresh_server, page_at):
    s = fresh_server(standard_seed())
    page = page_at(768, s.url)
    page.goto(s.url + "/patients/1")
    buttons = page.get_by_role("button", name=re.compile("I’ve checked on Amina"))
    for remaining in (3, 2, 1, 0):
        buttons.first.click()
        expect(buttons).to_have_count(remaining)
    expect(page.locator("#live-summary")).to_contain_text("All is well")
    expect(page.locator(".glance-headline")).to_have_text("All is well with Amina.")


def test_import_flow(fresh_server, page_at, tmp_path):
    s = fresh_server()
    page = page_at(768, s.url)
    page.goto(s.url + "/import")
    page.set_input_files("#file", str(SAMPLE_FILE))
    page.get_by_role("button", name="Add these results").click()
    expect(page.get_by_role("heading", name="Done, the results have been added")).to_be_visible()
    expect(page.locator(".result-counts")).to_contain_text("10 new things added")
    bad = tmp_path / "broken.json"
    bad.write_text("{not json", encoding="utf-8")
    page.set_input_files("#file", str(bad))
    page.get_by_role("button", name="Add these results").click()
    expect(page.get_by_role("heading", name="Nothing was added")).to_be_visible()
    expect(page.locator(".result")).to_contain_text("This file can't be read")


def test_add_user_in_browser(fresh_server, page_at):
    s = fresh_server()
    page = page_at(360, s.url)
    page.goto(s.url + "/users")
    page.fill("#display_name", "Sara")
    page.fill("#new-username", "sara")
    page.fill("#new-password", "sara-password")
    page.fill("#new-password-again", "sara-password")
    page.get_by_role("button", name="Add this person").click()
    expect(page.locator(".notice-success")).to_contain_text("Sara can now sign in")
    other = page_at(360, s.url, user={"username": "sara", "password": "sara-password", "name": "Sara"})
    expect(other.locator(".user-name")).to_contain_text("Sara")


def test_show_password_toggle(server, page_at):
    page = page_at(360, user=None)
    page.goto(server.url + "/login")
    page.fill("#password", "secret")
    page.get_by_label("Show the password as I type").check()
    assert page.get_attribute("#password", "type") == "text"


# --- live updates ------------------------------------------------------------------

def test_new_event_appears_without_refresh(fresh_server, page_at, width):
    s = fresh_server(one_person_no_events())
    page = page_at(width, s.url)
    page.goto(s.url + "/patients/1")
    expect(page.locator(".glance-headline")).to_have_text("No news about Amina yet.")
    indicator = page.locator("#live-indicator")
    expect(indicator).to_have_text("Live")
    page.evaluate("window.__noReload = true")

    assert s.post_event(fall(1, ago(minutes=1))) == 201
    expect(page.locator(".glance-headline")).to_have_text("Amina may need you now.", timeout=10000)
    expect(page.locator("#live-summary")).to_contain_text("Needs your attention")
    expect(page.locator("#live-alerts .alert-card")).to_have_count(1)
    expect(page.locator("#live-recent")).to_contain_text("Possible fall")
    expect(page.locator("#live-announcer")).to_contain_text("Amina may need you now.")

    assert s.post_event(gait(1, ago(minutes=1), 0.3)) == 201
    expect(page.locator(".trend-dot")).to_have_count(1, timeout=10000)
    expect(page.locator("#live-updated")).to_contain_text("Updated")
    assert page.evaluate("window.__noReload") is True, "the page must not have reloaded"
    check_page_quality(page)


def test_status_returns_to_all_is_well_when_checked_elsewhere(fresh_server, page_at):
    s = fresh_server(one_person_no_events())
    s.post_event(fall(1, ago(minutes=1)))
    watcher = page_at(1440, s.url)
    watcher.goto(s.url + "/patients/1")
    expect(watcher.locator("#live-summary")).to_contain_text("Needs your attention")
    expect(watcher.locator("#live-indicator")).to_have_text("Live")
    other = page_at(360, s.url, user=CARER)
    other.goto(s.url + "/patients/1")
    other.get_by_role("button", name=re.compile("I’ve checked on Amina")).click()
    expect(watcher.locator("#live-summary")).to_contain_text("All is well", timeout=10000)


def test_events_page_updates_live(fresh_server, page_at):
    s = fresh_server(one_person_no_events())
    page = page_at(768, s.url)
    page.goto(s.url + "/patients/1/events")
    expect(page.locator("#live-indicator")).to_have_text("Live")
    s.post_event(fall(1, ago(minutes=1)))
    expect(page.locator("tr.event-row")).to_have_count(1, timeout=10000)


def test_reconnecting_then_recovers(fresh_server, page_at):
    s = fresh_server(one_person_no_events(), LIVE_STREAM_SECONDS=1)
    page = page_at(768, s.url)
    page.goto(s.url + "/patients/1")
    indicator = page.locator("#live-indicator")
    expect(indicator).to_have_text("Live")

    page.context.route("**/live/**", lambda route: route.abort())
    expect(indicator).to_have_text("Reconnecting…", timeout=15000)
    # the page is never blank or broken while disconnected
    expect(page.locator(".glance-headline")).to_have_text("No news about Amina yet.")
    expect(page.locator("#signed-out-notice")).to_be_hidden()

    page.context.unroute("**/live/**")
    expect(indicator).to_have_text("Live", timeout=15000)
    s.post_event(fall(1, ago(minutes=1)))
    expect(page.locator(".glance-headline")).to_have_text("Amina may need you now.", timeout=15000)


def test_polling_fallback_without_server_sent_events(fresh_server, page_at):
    s = fresh_server(one_person_no_events())
    page = page_at(360, s.url, init_script="delete window.EventSource;")
    page.goto(s.url + "/patients/1")
    assert page.evaluate("'EventSource' in window") is False
    expect(page.locator("#live-indicator")).to_have_text("Live", timeout=10000)
    s.post_event(fall(1, ago(minutes=1)))
    expect(page.locator(".glance-headline")).to_have_text("Amina may need you now.", timeout=10000)


def test_signed_out_while_page_is_open(fresh_server, page_at):
    s = fresh_server(one_person_no_events(), SESSION_IDLE_MINUTES=0.04)  # about 2.4 seconds
    page = page_at(768, s.url)
    expect(page.locator("#live-indicator")).to_have_text("Live")
    page.wait_for_timeout(3000)
    s.post_event(fall(1, ago(minutes=1)))
    notice = page.locator("#signed-out-notice")
    expect(notice).to_be_visible(timeout=10000)
    expect(notice).to_contain_text("signed out")
    expect(page.locator("#live-indicator")).to_have_text("Signed out")
    # what was on screen stays readable
    expect(page.locator(".glance-headline")).to_have_text("No news about Amina yet.")
    notice.get_by_role("link", name="Sign in again").click()
    expect(page.get_by_role("heading", name="Sign in")).to_be_visible()
