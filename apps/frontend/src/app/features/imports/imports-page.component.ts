import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  AvailabilityDaySummary,
  EmployeeResponse,
  SchedulingApiService
} from '../../core/api/scheduling-api.service';

@Component({
  selector: 'app-imports-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './imports-page.component.html'
})
export class ImportsPageComponent implements OnInit {
  private readonly schedulingApi = inject(SchedulingApiService);

  weekStart = '2026-06-08';
  employees: EmployeeResponse[] = [];
  availabilityDays: AvailabilityDaySummary[] = [];
  isLoading = false;
  message = 'Ready';
  errorMessage = '';

  get totalAvailableEmployees(): number {
    let total = 0;

    for (const day of this.availabilityDays) {
      total += day.available_employee_count;
    }

    return total;
  }

  async ngOnInit(): Promise<void> {
    await this.refreshPage();
  }

  async refreshPage(): Promise<void> {
    await this.runAction('Import page loaded', async () => {
      await this.loadPageData();
    });
  }

  async importAvailability(): Promise<void> {
    await this.runAction('Availability imported', async () => {
      await this.schedulingApi.importAvailability(this.weekStart);
      await this.loadPageData();
    });
  }

  private async loadPageData(): Promise<void> {
    this.employees = await this.schedulingApi.loadEmployees();
    this.availabilityDays = await this.schedulingApi.loadAvailabilitySummary(
      this.weekStart
    );
  }

  private async runAction(
    successMessage: string,
    action: () => Promise<void>
  ): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      await action();
      this.message = successMessage;
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
