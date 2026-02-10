// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock fetch
global.fetch = jest.fn();

// Reset mocks before each test
beforeEach(() => {
  if (localStorage.getItem && localStorage.getItem.mockClear) {
    localStorage.getItem.mockClear();
  }
  if (localStorage.setItem && localStorage.setItem.mockClear) {
    localStorage.setItem.mockClear();
  }
  if (localStorage.removeItem && localStorage.removeItem.mockClear) {
    localStorage.removeItem.mockClear();
  }
  if (localStorage.clear && localStorage.clear.mockClear) {
    localStorage.clear.mockClear();
  }
  if (sessionStorage.getItem && sessionStorage.getItem.mockClear) {
    sessionStorage.getItem.mockClear();
  }
  if (sessionStorage.setItem && sessionStorage.setItem.mockClear) {
    sessionStorage.setItem.mockClear();
  }
  if (sessionStorage.removeItem && sessionStorage.removeItem.mockClear) {
    sessionStorage.removeItem.mockClear();
  }
  if (sessionStorage.clear && sessionStorage.clear.mockClear) {
    sessionStorage.clear.mockClear();
  }
  if (fetch && fetch.mockClear) {
    fetch.mockClear();
  }
});
