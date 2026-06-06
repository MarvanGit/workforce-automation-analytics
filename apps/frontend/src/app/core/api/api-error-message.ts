import { HttpErrorResponse } from '@angular/common/http';

export function apiErrorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'Backend is not reachable. Start the backend and try again.';
    }

    const detail = error.error?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (hasMessage(detail)) {
      return detail.message;
    }

    return `Request failed with status ${error.status}.`;
  }

  if (error instanceof Error && error.message !== '') {
    return error.message;
  }

  return 'Request failed';
}

function hasMessage(value: unknown): value is { message: string } {
  return (
    typeof value === 'object' &&
    value !== null &&
    'message' in value &&
    typeof value.message === 'string'
  );
}
