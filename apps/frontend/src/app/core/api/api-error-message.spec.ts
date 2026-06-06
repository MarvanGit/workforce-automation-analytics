/// <reference types="jasmine" />

import { HttpErrorResponse } from '@angular/common/http';

import { apiErrorMessage } from './api-error-message';

describe('apiErrorMessage', () => {
  it('uses backend detail text when it exists', () => {
    const error = new HttpErrorResponse({
      status: 400,
      error: {
        detail: 'Week start is required'
      }
    });

    expect(apiErrorMessage(error)).toBe('Week start is required');
  });

  it('uses a clear message when the backend is not reachable', () => {
    const error = new HttpErrorResponse({
      status: 0
    });

    expect(apiErrorMessage(error)).toBe(
      'Backend is not reachable. Start the backend and try again.'
    );
  });
});
