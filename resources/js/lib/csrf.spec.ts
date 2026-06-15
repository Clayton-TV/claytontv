import { afterEach, describe, expect, it } from 'vitest';
import { getCsrfToken } from '~/lib/csrf';

function setCookie(value: string) {
    document.cookie = `XSRF-TOKEN=${value}`;
}

afterEach(() => {
    // expire the cookie between tests
    document.cookie = 'XSRF-TOKEN=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
});

describe('getCsrfToken', () => {
    it('reads the XSRF-TOKEN cookie', () => {
        setCookie('tok-123');
        expect(getCsrfToken()).toBe('tok-123');
    });

    it('URL-decodes the value', () => {
        setCookie('a%2Bb');
        expect(getCsrfToken()).toBe('a+b');
    });

    it('returns empty string when the cookie is absent', () => {
        expect(getCsrfToken()).toBe('');
    });
});
