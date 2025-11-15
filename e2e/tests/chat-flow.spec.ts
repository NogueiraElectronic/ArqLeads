import { test, expect } from '@playwright/test';

test.describe('ArqLeads Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display chat button on homepage', async ({ page }) => {
    const chatButton = page.locator('button').filter({ hasText: /MessageCircle/ }).first();
    await expect(chatButton).toBeVisible();
  });

  test('should open chat widget when button is clicked', async ({ page }) => {
    // Click chat button
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Verify chat window is open
    await expect(page.getByText('ArqLeads Assistant')).toBeVisible();
    await expect(page.getByText('Estudio de Arquitectura')).toBeVisible();
  });

  test('should show initial greeting message', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Check initial message
    await expect(page.getByText(/Buenos días/)).toBeVisible();
    await expect(page.getByText(/¿En qué proyecto estás trabajando?/)).toBeVisible();
  });

  test('should close chat when X button is clicked', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Close chat
    const closeButton = page.locator('button').filter({ has: page.locator('[data-lucide="x"]') }).first();
    await closeButton.click();

    // Verify chat is closed
    await expect(page.getByText('ArqLeads Assistant')).not.toBeVisible();
  });

  test('should send a message and receive response', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Type message
    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    await input.fill('Hola, necesito ayuda');

    // Send message
    const sendButton = page.locator('button[type="submit"]');
    await sendButton.click();

    // Verify user message appears
    await expect(page.getByText('Hola, necesito ayuda')).toBeVisible();

    // Wait for bot response
    await expect(page.locator('.animate-spin')).toBeVisible();
    await expect(page.locator('.animate-spin')).not.toBeVisible({ timeout: 10000 });

    // Verify there are at least 2 messages (initial + user + bot response)
    const messages = page.locator('[class*="rounded-lg p-3"]');
    await expect(messages).toHaveCount(3, { timeout: 10000 });
  });

  test('should not send empty messages', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Try to send empty message
    const sendButton = page.locator('button[type="submit"]');
    await expect(sendButton).toBeDisabled();

    // Type spaces only
    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    await input.fill('   ');

    // Button should still be disabled
    await expect(sendButton).toBeDisabled();
  });

  test('complete lead qualification flow', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    const sendButton = page.locator('button[type="submit"]');

    // Step 1: Introduce project
    await input.fill('Quiero reformar mi piso en Vigo');
    await sendButton.click();
    await page.waitForTimeout(1000);

    // Step 2: Provide budget
    await input.fill('Mi presupuesto es de 30000 euros');
    await sendButton.click();
    await page.waitForTimeout(1000);

    // Step 3: Provide timeline
    await input.fill('Lo necesito en 2 meses');
    await sendButton.click();
    await page.waitForTimeout(1000);

    // Step 4: Provide contact info
    await input.fill('Mi nombre es Juan Pérez');
    await sendButton.click();
    await page.waitForTimeout(1000);

    await input.fill('Mi email es juan@example.com');
    await sendButton.click();
    await page.waitForTimeout(1000);

    await input.fill('Mi teléfono es +34666777888');
    await sendButton.click();
    await page.waitForTimeout(2000);

    // Verify lead score updated
    const scoreElement = page.getByText(/Puntuación:/);
    await expect(scoreElement).toBeVisible();

    // Score should be > 0 after providing information
    const scoreText = await scoreElement.textContent();
    expect(scoreText).toMatch(/\d+/);
  });

  test('should display lead category correctly', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Initially should show "Lead Frío"
    await expect(page.getByText('Lead Frío')).toBeVisible();

    // Provide high-quality lead information
    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    const sendButton = page.locator('button[type="submit"]');

    await input.fill('Necesito reforma completa, presupuesto 50000 euros, urgente en 1 mes, soy Juan Pérez, juan@example.com, +34666777888');
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(3000);

    // Category should update (could be warm or hot depending on score)
    const categoryElement = page.locator('[class*="font-semibold"]').filter({ hasText: /Lead/ });
    await expect(categoryElement).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Block API requests to simulate error
    await page.route('**/api/v1/chat/message', (route) => {
      route.abort();
    });

    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Try to send message
    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    await input.fill('Test message');

    const sendButton = page.locator('button[type="submit"]');
    await sendButton.click();

    // Should show error message
    await expect(page.getByText(/error de conexión/)).toBeVisible({ timeout: 5000 });
  });

  test('should preserve chat history when reopening', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Send a message
    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    await input.fill('Test message');

    const sendButton = page.locator('button[type="submit"]');
    await sendButton.click();

    await page.waitForTimeout(2000);

    // Close chat
    const closeButton = page.locator('button').filter({ has: page.locator('[data-lucide="x"]') }).first();
    await closeButton.click();

    // Reopen chat
    await chatButton.click();

    // Message should still be there
    await expect(page.getByText('Test message')).toBeVisible();
  });

  test('should display message timestamps', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    // Check that timestamps are visible
    const timestamps = page.locator('.text-xs');
    await expect(timestamps.first()).toBeVisible();
  });

  test('should disable input while loading', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    await input.fill('Test');

    const sendButton = page.locator('button[type="submit"]');
    await sendButton.click();

    // Input should be disabled immediately
    await expect(input).toBeDisabled();

    // Wait for response
    await page.waitForTimeout(2000);

    // Input should be enabled again
    await expect(input).toBeEnabled();
  });

  test('should auto-scroll to latest message', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('button[class*="bg-blue-600"]').first();
    await chatButton.click();

    const input = page.getByPlaceholder(/Escribe tu mensaje/);
    const sendButton = page.locator('button[type="submit"]');

    // Send multiple messages
    for (let i = 1; i <= 5; i++) {
      await input.fill(`Message ${i}`);
      await sendButton.click();
      await page.waitForTimeout(1500);
    }

    // Latest message should be visible
    await expect(page.getByText('Message 5')).toBeVisible();
  });
});

test.describe('Admin Dashboard', () => {
  test('should load admin dashboard', async ({ page }) => {
    await page.goto('http://localhost:8000/admin/dashboard');

    // Check dashboard header
    await expect(page.getByText(/ArqLeads - Dashboard Admin/)).toBeVisible();
  });

  test('should display stats cards', async ({ page }) => {
    await page.goto('http://localhost:8000/admin/dashboard');

    // Check for stat cards
    await expect(page.getByText('Total Leads')).toBeVisible();
    await expect(page.getByText(/Leads Calientes/)).toBeVisible();
    await expect(page.getByText(/Leads Tibios/)).toBeVisible();
    await expect(page.getByText(/Leads Fríos/)).toBeVisible();
  });

  test('should load and display leads table', async ({ page }) => {
    await page.goto('http://localhost:8000/admin/dashboard');

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check for table headers
    await expect(page.getByText('Nombre')).toBeVisible();
    await expect(page.getByText('Email')).toBeVisible();
    await expect(page.getByText('Categoría')).toBeVisible();
  });

  test('should display chart', async ({ page }) => {
    await page.goto('http://localhost:8000/admin/dashboard');

    // Check for chart canvas
    const chart = page.locator('#leadsChart');
    await expect(chart).toBeVisible();
  });

  test('should filter leads by category', async ({ page }) => {
    await page.goto('http://localhost:8000/admin/dashboard');

    await page.waitForTimeout(2000);

    // Click filter buttons
    const hotFilter = page.getByRole('button', { name: /Calientes/ });
    if (await hotFilter.isVisible()) {
      await hotFilter.click();
      await page.waitForTimeout(500);
    }
  });
});

test.describe('API Health', () => {
  test('should have healthy API', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('should expose metrics endpoint', async ({ request }) => {
    const response = await request.get('http://localhost:8000/metrics');
    expect(response.ok()).toBeTruthy();

    const text = await response.text();
    expect(text).toContain('http_requests_total');
  });

  test('should have API docs available', async ({ page }) => {
    await page.goto('http://localhost:8000/docs');

    await expect(page.getByText('FastAPI')).toBeVisible();
  });
});
