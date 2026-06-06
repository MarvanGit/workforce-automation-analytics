import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  AvailabilityDaySummary,
  EmployeeResponse,
  SavedScheduleRunResponse,
  SchedulePreviewResponse,
  ScheduleRunSummaryResponse,
  SchedulingApiService,
  ShiftDemandResponse,
  ShiftTemplateResponse
} from '../../core/api/scheduling-api.service';

interface WeeklyDemandDay {
  name: string;
  date: string;
  enabled: boolean;
  requiredEmployeeCount: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly schedulingApi = inject(SchedulingApiService);
  private readonly weekdayNames = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
  ];

  weekStart = '2026-06-08';
  shiftName = 'Morning';
  shiftStart = '09:00';
  shiftEnd = '17:00';
  selectedTemplateId = '';
  weeklyDemandDays = this.buildWeeklyDemandDays(this.weekStart);

  employees: EmployeeResponse[] = [];
  availabilityDays: AvailabilityDaySummary[] = [];
  shiftTemplates: ShiftTemplateResponse[] = [];
  shiftDemand: ShiftDemandResponse[] = [];
  schedulePreview: SchedulePreviewResponse | null = null;
  scheduleRuns: ScheduleRunSummaryResponse[] = [];
  selectedRun: SavedScheduleRunResponse | null = null;

  isLoading = false;
  activeAction = '';
  message = 'Ready';
  errorMessage = '';

  readonly quickShifts = [
    { name: 'Opening', start: '09:00', end: '17:00' },
    { name: 'Core', start: '10:00', end: '18:00' },
    { name: 'Late', start: '15:00', end: '20:00' }
  ];

  get totalAvailableEmployees(): number {
    return this.availabilityDays.reduce(
      (total, day) => total + day.available_employee_count,
      0
    );
  }

  get warningCount(): number {
    return this.schedulePreview?.warnings.length ?? 0;
  }

  get statusText(): string {
    if (this.isLoading) {
      return `Working on ${this.activeAction}...`;
    }

    return this.errorMessage || this.message;
  }

  get canCreateTemplate(): boolean {
    return (
      !this.isLoading &&
      this.shiftName.trim() !== '' &&
      this.shiftStart !== '' &&
      this.shiftEnd !== '' &&
      this.shiftStart !== this.shiftEnd
    );
  }

  get canCreateWeeklyDemand(): boolean {
    return (
      !this.isLoading &&
      this.weekStart !== '' &&
      this.selectedTemplateId !== '' &&
      this.hasSelectedDemandDay()
    );
  }

  get canUseScheduleActions(): boolean {
    return !this.isLoading && this.weekStart !== '';
  }

  get canSaveScheduleRun(): boolean {
    return this.canUseScheduleActions && this.schedulePreview !== null;
  }

  async ngOnInit(): Promise<void> {
    await this.refreshDashboard();
  }

  async refreshDashboard(): Promise<void> {
    await this.runAction('loading dashboard data', 'Dashboard data loaded', async () => {
      this.employees = await this.schedulingApi.loadEmployees();
      this.shiftTemplates = await this.schedulingApi.loadShiftTemplates();
      this.shiftDemand = await this.schedulingApi.loadShiftDemand(this.weekStart);

      if (this.shiftTemplates.length > 0 && this.selectedTemplateId === '') {
        this.selectedTemplateId = this.shiftTemplates[0].id;
      }

      await this.loadAvailabilitySummary();
      await this.loadScheduleRuns();
    });
  }

  async importAvailability(): Promise<void> {
    await this.runAction('importing availability', 'Availability imported', async () => {
      await this.schedulingApi.importAvailability(this.weekStart);
      await this.loadAvailabilitySummary();
    });
  }

  async createShiftTemplate(): Promise<void> {
    await this.runAction('creating shift template', 'Shift template created', async () => {
      const template = await this.schedulingApi.createShiftTemplate(
        this.shiftName,
        this.shiftStart,
        this.shiftEnd
      );

      this.selectedTemplateId = template.id;
      await this.loadShiftTemplates();
    });
  }

  async createShiftDemand(): Promise<void> {
    await this.runAction('creating weekly demand', 'Weekly demand created', async () => {
      for (const day of this.weeklyDemandDays) {
        if (day.enabled && day.requiredEmployeeCount > 0) {
          await this.schedulingApi.createShiftDemand(
            day.date,
            this.selectedTemplateId,
            day.requiredEmployeeCount
          );
        }
      }

      await this.loadShiftDemand();
      this.schedulePreview = null;
    });
  }

  async deleteShiftDemand(demand: ShiftDemandResponse): Promise<void> {
    await this.runAction('deleting shift demand', 'Shift demand deleted', async () => {
      await this.schedulingApi.deleteShiftDemand(demand.id);
      await this.loadShiftDemand();
      this.schedulePreview = null;
    });
  }

  async previewSchedule(): Promise<void> {
    await this.runAction('previewing schedule', 'Schedule preview generated', async () => {
      this.schedulePreview = await this.schedulingApi.previewSchedule(this.weekStart);
    });
  }

  async saveScheduleRun(): Promise<void> {
    await this.runAction('saving schedule run', 'Schedule run saved', async () => {
      this.selectedRun = await this.schedulingApi.saveScheduleRun(this.weekStart);
      await this.loadScheduleRuns();
    });
  }

  async openScheduleRun(runId: string): Promise<void> {
    await this.runAction('opening schedule run', 'Schedule run opened', async () => {
      this.selectedRun = await this.schedulingApi.loadScheduleRun(runId);
    });
  }

  useQuickShift(shift: { name: string; start: string; end: string }): void {
    this.shiftName = shift.name;
    this.shiftStart = shift.start;
    this.shiftEnd = shift.end;
  }

  changeWeekStart(value: string): void {
    this.weekStart = value;
    this.weeklyDemandDays = this.buildWeeklyDemandDays(value);
    this.schedulePreview = null;
    this.selectedRun = null;
  }

  private async loadAvailabilitySummary(): Promise<void> {
    this.availabilityDays = await this.schedulingApi.loadAvailabilitySummary(
      this.weekStart
    );
  }

  private async loadShiftTemplates(): Promise<void> {
    this.shiftTemplates = await this.schedulingApi.loadShiftTemplates();
  }

  private async loadShiftDemand(): Promise<void> {
    this.shiftDemand = await this.schedulingApi.loadShiftDemand(this.weekStart);
  }

  private async loadScheduleRuns(): Promise<void> {
    this.scheduleRuns = await this.schedulingApi.loadScheduleRuns();
  }

  private async runAction(
    activeAction: string,
    message: string,
    action: () => Promise<void>
  ): Promise<void> {
    this.isLoading = true;
    this.activeAction = activeAction;
    this.errorMessage = '';

    try {
      await action();
      this.message = message;
    } catch (error) {
      this.errorMessage = this.errorText(error);
    } finally {
      this.isLoading = false;
      this.activeAction = '';
    }
  }

  private errorText(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (error.status === 0) {
        return 'Backend is not reachable. Start the FastAPI backend and try again.';
      }

      if (error.status === 404) {
        return 'API route was not found. Rebuild the backend container if it is running an old image.';
      }

      const detail = this.detailText(error.error?.detail);
      if (detail !== '') {
        return detail;
      }

      return `Request failed with status ${error.status}.`;
    }

    if (error instanceof Error && error.message !== '') {
      return error.message;
    }

    return 'Request failed';
  }

  private detailText(detail: unknown): string {
    if (typeof detail === 'string') {
      return detail;
    }

    if (this.hasMessage(detail)) {
      return detail.message;
    }

    return '';
  }

  private hasMessage(value: unknown): value is { message: string } {
    return (
      typeof value === 'object' &&
      value !== null &&
      'message' in value &&
      typeof value.message === 'string'
    );
  }

  private hasSelectedDemandDay(): boolean {
    for (const day of this.weeklyDemandDays) {
      if (day.enabled && day.requiredEmployeeCount > 0) {
        return true;
      }
    }

    return false;
  }

  private buildWeeklyDemandDays(weekStart: string): WeeklyDemandDay[] {
    const days: WeeklyDemandDay[] = [];

    if (weekStart === '') {
      return days;
    }

    for (let index = 0; index < this.weekdayNames.length; index++) {
      days.push({
        name: this.weekdayNames[index],
        date: this.addDays(weekStart, index),
        enabled: true,
        requiredEmployeeCount: 1
      });
    }

    return days;
  }

  private addDays(dateText: string, daysToAdd: number): string {
    const parts = dateText.split('-');
    const year = Number(parts[0]);
    const month = Number(parts[1]) - 1;
    const day = Number(parts[2]);
    const date = new Date(year, month, day);

    date.setDate(date.getDate() + daysToAdd);

    return this.dateText(date);
  }

  private dateText(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }
}
