/**
 * API Client for LDPlayer Management System
 * Handles authentication and API requests
 */

// В dev режиме используем proxy Vite, поэтому базовый URL пустой
const API_BASE = '';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  async request(url, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Token expired, redirect to login
        this.clearToken();
        window.location.href = '/login';
        throw new Error('Authentication required');
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentication
  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  async logout() {
    this.clearToken();
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Emulators
  async getEmulators() {
    return this.request('/api/emulators');
  }

  async createEmulator(workstation_id, name, config = {}) {
    return this.request('/api/emulators', {
      method: 'POST',
      body: JSON.stringify({
        workstation_id,
        name,
        config
      })
    });
  }

  async startEmulator(workstation_id, name) {
    return this.request('/api/emulators/start', {
      method: 'POST',
      body: JSON.stringify({ workstation_id, name })
    });
  }

  async stopEmulator(workstation_id, name) {
    return this.request('/api/emulators/stop', {
      method: 'POST',
      body: JSON.stringify({ workstation_id, name })
    });
  }

  async deleteEmulator(workstation_id, name) {
    return this.request('/api/emulators', {
      method: 'DELETE',
      body: JSON.stringify({ workstation_id, name })
    });
  }

  // Workstations
  async getWorkstations() {
    return this.request('/api/workstations');
  }

  async addWorkstation(data) {
    return this.request('/api/workstations', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async removeWorkstation(workstation_id) {
    return this.request(`/api/workstations/${workstation_id}`, {
      method: 'DELETE'
    });
  }

  async testConnection(workstation_id) {
    return this.request(`/api/workstations/${workstation_id}/test-connection`, {
      method: 'POST'
    });
  }

  // Operations
  async getOperations() {
    return this.request('/api/operations');
  }

  async getOperation(operation_id) {
    return this.request(`/api/operations/${operation_id}`);
  }

  async cancelOperation(operation_id) {
    return this.request(`/api/operations/${operation_id}/cancel`, {
      method: 'POST'
    });
  }

  // System
  async getSystemStatus() {
    return this.request('/api/status');
  }

  async getHealth() {
    return this.request('/api/health');
  }
}

export const api = new ApiClient();
