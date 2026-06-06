import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  AvailabilityDaySummary,
  EmployeeResponse,
  ScheduleRunSummaryResponse,
  SchedulingApiService,
  ShiftDemandResponse
} from '../../core/api/scheduling-api.service';

@Component({
  selector: 'app-analytics-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './analytics-page.component.html'
})
export class AnalyticsPageComponent implements OnInit {
  private readonly schedulingApi = inject(SchedulingApiService);

  weekStart = '2026-06-08';
  employees: EmployeeResponse[] = [];
  availabilityDays: AvailabilityDaySummary[] = [];
  shiftDemand: ShiftDemandResponse[] = [];
  scheduleRuns: ScheduleRunSummaryResponse[] = [];
  isLoading = false;
  message = 'Ready';
  errorMessage = '';

  get availableTotal(): number {
    let total = 0;

    for (const day of this.availabilityDays) {
      total += day.available_employee_count;
    }

    return total;
  }

  get demandTotal(): number {
    let total = 0;

    for (const demand of this.shiftDemand) {
      total += demand.required_employee_count;
    }

    return total;
  }

  get availableHours(): number {
    let total = 0;

    for (const day of this.availabilityDays) {
      total += day.available_hours;
    }

    return total;
  }

  get demandGap(): number {
    return this.demandTotal - this.availableTotal;
  }

  async ngOnInit(): Promise<void> {
    await this.loadAnalytics();
  }

  async loadAnalytics(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      this.employees = await this.schedulingApi.loadEmployees();
      this.availabilityDays = await this.schedulingApi.loadAvailabilitySummary(
        this.weekStart
      );
      this.shiftDemand = await this.schedulingApi.loadShiftDemand(this.weekStart);
      this.scheduleRuns = await this.schedulingApi.loadScheduleRuns();
      this.message = 'Analytics loaded';
    } catch (error) {
      this.errorMessage = this.errorText(error);
    } finally {
      this.isLoading = false;
    }
  }

  private errorText(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (typeof error.error?.detail === 'string') {
        return error.error.detail;
      }

      return `Request failed with status ${error.status}.`;
    }

    return 'Request failed';
  }
}
