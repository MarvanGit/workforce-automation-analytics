import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { apiErrorMessage } from '../../core/api/api-error-message';
import {
  AvailabilityDaySummary,
  SchedulingApiService
} from '../../core/api/scheduling-api.service';

@Component({
  selector: 'app-availability-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './availability-page.component.html'
})
export class AvailabilityPageComponent implements OnInit {
  private readonly schedulingApi = inject(SchedulingApiService);

  weekStart = '2026-06-08';
  days: AvailabilityDaySummary[] = [];
  isLoading = false;
  message = 'Ready';
  errorMessage = '';

  get statusText(): string {
    if (this.isLoading) {
      return 'Loading availability...';
    }

    return this.errorMessage || this.message;
  }

  get loadButtonText(): string {
    return this.isLoading ? 'Loading' : 'Load';
  }

  get availableTotal(): number {
    let total = 0;

    for (const day of this.days) {
      total += day.available_employee_count;
    }

    return total;
  }

  get unavailableTotal(): number {
    let total = 0;

    for (const day of this.days) {
      total += day.unavailable_employee_count;
    }

    return total;
  }

  get availableHours(): number {
    let total = 0;

    for (const day of this.days) {
      total += day.available_hours;
    }

    return total;
  }

  async ngOnInit(): Promise<void> {
    await this.loadAvailability();
  }

  async loadAvailability(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      this.days = await this.schedulingApi.loadAvailabilitySummary(this.weekStart);
      this.message = 'Availability loaded';
    } catch (error) {
      this.errorMessage = apiErrorMessage(error);
    } finally {
      this.isLoading = false;
    }
  }
}
