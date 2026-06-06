import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { apiErrorMessage } from '../../core/api/api-error-message';
import {
  AvailabilityDaySummary,
  EmployeeResponse,
  ScheduleRunSummaryResponse,
  SchedulingApiService,
  ShiftDemandResponse,
  ShiftTemplateResponse
} from '../../core/api/scheduling-api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly schedulingApi = inject(SchedulingApiService);

  weekStart = '2026-06-08';
  employees: EmployeeResponse[] = [];
  availabilityDays: AvailabilityDaySummary[] = [];
  shiftTemplates: ShiftTemplateResponse[] = [];
  shiftDemand: ShiftDemandResponse[] = [];
  scheduleRuns: ScheduleRunSummaryResponse[] = [];

  isLoading = false;
  message = 'Ready';
  errorMessage = '';
  backendOnline = false;
  backendStatus = 'Backend not checked';

  get statusText(): string {
    if (this.isLoading) {
      return 'Loading overview...';
    }

    return this.errorMessage || this.message;
  }

  get refreshButtonText(): string {
    return this.isLoading ? 'Loading' : 'Refresh';
  }

  get availableEmployeeTotal(): number {
    let total = 0;

    for (const day of this.availabilityDays) {
      total += day.available_employee_count;
    }

    return total;
  }

  get demandEmployeeTotal(): number {
    let total = 0;

    for (const demand of this.shiftDemand) {
      total += demand.required_employee_count;
    }

    return total;
  }

  get hasAvailabilityData(): boolean {
    return this.availableEmployeeTotal > 0;
  }

  get hasShiftDemand(): boolean {
    return this.shiftDemand.length > 0;
  }

  get hasSavedRuns(): boolean {
    return this.scheduleRuns.length > 0;
  }

  get latestRun(): ScheduleRunSummaryResponse | null {
    if (this.scheduleRuns.length === 0) {
      return null;
    }

    return this.scheduleRuns[0];
  }

  async ngOnInit(): Promise<void> {
    await this.refreshDashboard();
  }

  async refreshDashboard(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      await this.checkBackendHealth();
      this.employees = await this.schedulingApi.loadEmployees();
      this.availabilityDays = await this.schedulingApi.loadAvailabilitySummary(
        this.weekStart
      );
      this.shiftTemplates = await this.schedulingApi.loadShiftTemplates();
      this.shiftDemand = await this.schedulingApi.loadShiftDemand(this.weekStart);
      this.scheduleRuns = await this.schedulingApi.loadScheduleRuns();
      this.message = 'Overview loaded';
    } catch (error) {
      this.backendOnline = false;
      this.backendStatus = 'Backend is not reachable';
      this.errorMessage = apiErrorMessage(error);
    } finally {
      this.isLoading = false;
    }
  }

  async changeWeekStart(value: string): Promise<void> {
    this.weekStart = value;
    await this.refreshDashboard();
  }

  private async checkBackendHealth(): Promise<void> {
    const health = await this.schedulingApi.checkHealth();

    this.backendOnline = health.status === 'ok';
    this.backendStatus = this.backendOnline ? 'Backend connected' : 'Backend issue';
  }
}
