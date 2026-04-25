import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import Library from './Library';
import { ToastProvider } from './Toast';

const handlers = [
  http.get('http://localhost:8000/api/stories/', () => {
    return HttpResponse.json([
      { uuid: '123', name: 'Test Story 1', updated_at: new Date().toISOString() },
      { uuid: '456', name: 'Processing Story', updated_at: new Date().toISOString(), progress: { status: 'processing', current: 2, total: 10 } }
    ]);
  }),
  http.post('http://localhost:8000/api/stories/import_url', async ({ request }) => {
    const data = await request.json();
    if (data.url === 'fail') {
      return HttpResponse.json({ status: 'error', detail: 'Invalid URL' }, { status: 400 });
    }
    return HttpResponse.json({ status: 'success', story_uuid: '789' });
  })
];

const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  vi.clearAllMocks();
});
afterAll(() => server.close());

const renderWithProviders = (ui) => {
  return render(
    <BrowserRouter>
      <ToastProvider>
        {ui}
      </ToastProvider>
    </BrowserRouter>
  );
};

describe('Library Component', () => {
  it('renders loading state initially', () => {
    renderWithProviders(<Library />);
    expect(screen.getByText(/Loading novels.../i)).toBeInTheDocument();
  });

  it('fetches and displays stories', async () => {
    renderWithProviders(<Library />);
    await waitFor(() => {
      expect(screen.getByText('Test Story 1')).toBeInTheDocument();
    });
    expect(screen.getByText('Processing Story')).toBeInTheDocument();
    expect(screen.getByText('Processing Ingestion...')).toBeInTheDocument();
    expect(screen.getByText('2 / 10')).toBeInTheDocument();
  });

  it('handles import start successfully', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Library />);
    
    const input = await screen.findByPlaceholderText(/Paste a RoyalRoad Fiction URL here/i);
    const button = screen.getByRole('button', { name: /Import Book/i });

    await user.type(input, 'http://royalroad.com/fiction/123');
    await user.click(button);

    // Should show success toast
    await waitFor(() => {
      expect(screen.getByText(/Import started!/i)).toBeInTheDocument();
    });
  });

  it('handles import failure', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Library />);
    
    // We mock server response to error if URL brings 'fail'. The post handler above is written for 'fail' URL
    const input = await screen.findByPlaceholderText(/Paste a RoyalRoad Fiction URL here/i);
    const button = screen.getByRole('button', { name: /Import Book/i });

    await user.type(input, 'fail');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Failed to import:/i)).toBeInTheDocument();
    });
  });
});
