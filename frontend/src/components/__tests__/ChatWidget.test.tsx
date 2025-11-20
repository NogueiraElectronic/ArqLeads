import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import ChatWidget from '../ChatWidget';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('ChatWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('should render chat button when closed', () => {
      render(<ChatWidget />);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should not show chat window initially', () => {
      render(<ChatWidget />);
      expect(screen.queryByText('ArqLeads Assistant')).not.toBeInTheDocument();
    });
  });

  describe('Opening and Closing', () => {
    it('should open chat window when button is clicked', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByText('ArqLeads Assistant')).toBeInTheDocument();
      expect(screen.getByText('Estudio de Arquitectura')).toBeInTheDocument();
    });

    it('should close chat window when X button is clicked', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      // Open chat
      const openButton = screen.getByRole('button');
      await user.click(openButton);

      // Close chat
      const closeButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg')
      );
      if (closeButton) await user.click(closeButton);

      expect(screen.queryByText('ArqLeads Assistant')).not.toBeInTheDocument();
    });

    it('should show initial assistant message when opened', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByText(/Buenos días/)).toBeInTheDocument();
      expect(screen.getByText(/¿En qué proyecto estás trabajando?/)).toBeInTheDocument();
    });
  });

  describe('Lead Score Display', () => {
    it('should display initial lead score of 0', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByText(/Puntuación:/)).toBeInTheDocument();
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('should display "Lead Frío" category initially', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByText('Lead Frío')).toBeInTheDocument();
    });

    it('should update lead score after API response', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Gracias por la información',
          timestamp: new Date().toISOString(),
          lead_score: 75,
          lead_category: 'hot',
        },
      });

      render(<ChatWidget />);

      // Open chat
      const button = screen.getByRole('button');
      await user.click(button);

      // Send message
      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Necesito reformar mi piso');

      const sendButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg') && !btn.querySelector('[data-lucide="x"]')
      );
      if (sendButton) await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('75')).toBeInTheDocument();
      });
    });

    it('should update category to "Lead Caliente" for hot leads', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Excelente',
          timestamp: new Date().toISOString(),
          lead_score: 85,
          lead_category: 'hot',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test message');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText('Lead Caliente')).toBeInTheDocument();
      });
    });
  });

  describe('Sending Messages', () => {
    it('should send message when form is submitted', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Respuesta del bot',
          timestamp: new Date().toISOString(),
          lead_score: 50,
          lead_category: 'warm',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Hola');

      const sendButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg') && !btn.querySelector('[data-lucide="x"]')
      );
      if (sendButton) await user.click(sendButton);

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          expect.stringContaining('/chat/message'),
          expect.objectContaining({
            message: 'Hola',
            language: 'es',
            channel: 'web',
          })
        );
      });
    });

    it('should display user message immediately', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Bot response',
          timestamp: new Date().toISOString(),
          lead_score: 0,
          lead_category: 'cold',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Mi mensaje de prueba');
      await user.keyboard('{Enter}');

      expect(screen.getByText('Mi mensaje de prueba')).toBeInTheDocument();
    });

    it('should clear input after sending message', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Response',
          timestamp: new Date().toISOString(),
          lead_score: 0,
          lead_category: 'cold',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/) as HTMLInputElement;
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('should not send empty messages', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, '   ');
      await user.keyboard('{Enter}');

      expect(mockedAxios.post).not.toHaveBeenCalled();
    });

    it('should disable input and button while loading', async () => {
      const user = userEvent.setup();

      // Simulate slow API response
      mockedAxios.post.mockImplementationOnce(
        () => new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              data: {
                message: 'Response',
                timestamp: new Date().toISOString(),
                lead_score: 0,
                lead_category: 'cold',
              },
            });
          }, 100);
        })
      );

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/) as HTMLInputElement;
      await user.type(input, 'Test');

      const sendButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg') && !btn.querySelector('[data-lucide="x"]')
      ) as HTMLButtonElement;

      if (sendButton) await user.click(sendButton);

      // Check that inputs are disabled during loading
      expect(input.disabled).toBe(true);
      expect(sendButton.disabled).toBe(true);

      // Wait for response
      await waitFor(() => {
        expect(input.disabled).toBe(false);
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading indicator when waiting for response', async () => {
      const user = userEvent.setup();

      mockedAxios.post.mockImplementationOnce(
        () => new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              data: {
                message: 'Response',
                timestamp: new Date().toISOString(),
                lead_score: 0,
                lead_category: 'cold',
              },
            });
          }, 100);
        })
      );

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      // Should show loading animation
      const loader = document.querySelector('.animate-spin');
      expect(loader).toBeInTheDocument();

      // Wait for response
      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when API fails', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText(/se ha producido un error de conexión/)).toBeInTheDocument();
      });
    });

    it('should allow sending another message after error', async () => {
      const user = userEvent.setup();

      // First call fails
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      // Second call succeeds
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Success',
          timestamp: new Date().toISOString(),
          lead_score: 0,
          lead_category: 'cold',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/) as HTMLInputElement;

      // First message (fails)
      await user.type(input, 'First message');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText(/error de conexión/)).toBeInTheDocument();
      });

      // Second message (succeeds)
      await user.type(input, 'Second message');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText('Success')).toBeInTheDocument();
      });
    });
  });

  describe('Category Helper Functions', () => {
    it('should apply correct color class for hot leads', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Response',
          timestamp: new Date().toISOString(),
          lead_score: 90,
          lead_category: 'hot',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        const categoryLabel = screen.getByText('Lead Caliente');
        expect(categoryLabel).toHaveClass('text-red-600');
      });
    });

    it('should apply correct color class for warm leads', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Response',
          timestamp: new Date().toISOString(),
          lead_score: 65,
          lead_category: 'warm',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        const categoryLabel = screen.getByText('Lead Tibio');
        expect(categoryLabel).toHaveClass('text-orange-600');
      });
    });

    it('should apply correct color class for cold leads', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const categoryLabel = screen.getByText('Lead Frío');
      expect(categoryLabel).toHaveClass('text-blue-600');
    });
  });

  describe('Message Timestamps', () => {
    it('should display timestamps for messages', async () => {
      const user = userEvent.setup();
      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      // Check initial message has timestamp
      const timestamps = document.querySelectorAll('.text-xs');
      expect(timestamps.length).toBeGreaterThan(0);
    });
  });

  describe('Session ID', () => {
    it('should include session ID in API calls', async () => {
      const user = userEvent.setup();
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          message: 'Response',
          timestamp: new Date().toISOString(),
          lead_score: 0,
          lead_category: 'cold',
        },
      });

      render(<ChatWidget />);

      const button = screen.getByRole('button');
      await user.click(button);

      const input = screen.getByPlaceholderText(/Escribe tu mensaje/);
      await user.type(input, 'Test');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            session_id: expect.stringMatching(/^session-\d+$/),
          })
        );
      });
    });
  });
});
