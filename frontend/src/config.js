// API Configuration
// Uses environment variables with fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export default {
  API_BASE_URL
};
