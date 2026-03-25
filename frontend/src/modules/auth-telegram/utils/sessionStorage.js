const STORAGE_KEY = "telegram_auth_pending";
const MOBILE_RESET_KEY = "telegram_mobile_reset_pending";

export function savePendingTelegramAuth(payload) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

export function loadPendingTelegramAuth() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearPendingTelegramAuth() {
  sessionStorage.removeItem(STORAGE_KEY);
}

export function savePendingMobileReset(payload) {
  sessionStorage.setItem(MOBILE_RESET_KEY, JSON.stringify(payload));
}

export function loadPendingMobileReset() {
  try {
    const raw = sessionStorage.getItem(MOBILE_RESET_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearPendingMobileReset() {
  sessionStorage.removeItem(MOBILE_RESET_KEY);
}
