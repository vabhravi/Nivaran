/**
 * NIVARAN — Socket.IO Client Utility
 * Connects to the Flask-SocketIO backend for real-time progress updates.
 */

import { io } from 'socket.io-client';

// Use Vite's environment variable or undefined to auto-detect current origin (uses Vite's proxy)
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || undefined;

let socket = null;

/**
 * Get or create the Socket.IO connection.
 * Returns the socket instance and manages lifecycle.
 */
export function getSocket() {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socket.on('connect', () => {
      console.log('[NIVARAN] Socket.IO connected:', socket.id);
    });

    socket.on('disconnect', (reason) => {
      console.log('[NIVARAN] Socket.IO disconnected:', reason);
    });

    socket.on('connect_error', (err) => {
      console.warn('[NIVARAN] Socket.IO connection error:', err.message);
    });
  }

  return socket;
}

/**
 * Get the current Socket.IO session ID (for sending with HTTP requests).
 */
export function getSocketId() {
  if (socket && socket.connected) {
    return socket.id;
  }
  return null;
}

/**
 * Disconnect and cleanup the socket.
 */
export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}
