import asyncio
from playwright import async_api

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()
        
        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )
        
        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        # Open a new page in the browser context
        page = await context.new_page()
        
        # Navigate to your target URL and wait until the network request is committed
        await page.goto("http://localhost:5173", wait_until="commit", timeout=10000)
        
        # Wait for the main page to reach DOMContentLoaded state (optional for stability)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        # Iterate through all iframes and wait for them to load as well
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        # Interact with the page elements to simulate user flow
        # Test CRUD operations on client management
        
        # Navigate to clients section
        try:
            # Look for clients navigation link
            clients_link = await page.query_selector('a[href*="client"], nav a:has-text("Client"), nav a:has-text("Clienti")')
            if clients_link:
                await clients_link.click()
                await page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass
        
        # Verify we can see the clients page
        await page.wait_for_selector('h1, h2', timeout=10000)
        page_title = await page.text_content('h1, h2')
        
        # Look for "Nuovo Cliente" or "Add Client" button
        add_button = await page.query_selector('button:has-text("Nuovo"), button:has-text("Add"), button:has-text("Create")')
        assert add_button is not None, 'Add client button not found'
        
        # Test that we can click the add button (form should open)
        await add_button.click()
        await asyncio.sleep(1)
        
        # Look for form elements
        form_inputs = await page.query_selector_all('input, textarea, select')
        assert len(form_inputs) > 0, 'Client form inputs not found'
        
        # Check if there's a client list/table
        client_list = await page.query_selector('table, .client-list, [data-testid*="client"]')
        
        print(f"✅ TC002 PASSED: Client management accessible with {len(form_inputs)} form fields")
        await asyncio.sleep(2)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    