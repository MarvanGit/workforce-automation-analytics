import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  SavedScheduleRunResponse,
  SchedulePreviewResponse,
  ScheduleRunSummaryResponse,
  ScheduleShiftPreviewResponse,
  SchedulingApiService,
  ShiftDemandResponse,
  ShiftTemplateResponse
} from '../../core/api/scheduling-api.service';

interface WeekDay {
  name: string;
  date: string;
}

interface ScheduleBoardDay {
  name: string;
  date: string;
  shifts: ScheduleShiftPreviewResponse[];
}

@Component({
  selector: 'app-scheduling-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './scheduling-page.component.html'
})
export class SchedulingPageComponent implements OnInit {
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
  weekDays = this.buildWeekDays(this.weekStart);
  shiftName = 'Morning';
  shiftStart = '09:00';
  shiftEnd = '17:00';
  selectedTemplateId = '';
  selectedDemandDate = this.weekStart;
  requiredEmployeeCount = 1;

  shiftTemplates: ShiftTemplateResponse[] = [];
  shiftDemand: ShiftDemandResponse[] = [];
  schedulePreview: SchedulePreviewResponse | null = null;
  scheduleRuns: ScheduleRunSummaryResponse[] = [];
  selectedRun: SavedScheduleRunResponse | null = null;

  isLoading = false;
  message = 'Ready';
  errorMessage = '';

  get canCreateTemplate(): boolean {
    return (
      !this.isLoading &&
      this.shiftName.trim() !== '' &&
      this.shiftStart !== '' &&
      this.shiftEnd !== '' &&
      this.shiftStart !== this.shiftEnd
    );
  }

  get canCreateDemand(): boolean {
    return (
      !this.isLoading &&
      this.selectedTemplateId !== '' &&
      this.selectedDemandDate !== '' &&
      this.requiredEmployeeCount > 0 &&
      !this.demandExists(this.selectedDemandDate, this.selectedTemplateId)
    );
  }

  get canPreviewSchedule(): boolean {
    return !this.isLoading && this.weekStart !== '' && this.shiftDemand.length > 0;
  }

  get canSaveScheduleRun(): boolean {
    return !this.isLoading && this.schedulePreview !== null;
  }

  get previewBoardDays(): ScheduleBoardDay[] {
    const boardDays: ScheduleBoardDay[] = [];

    for (const day of this.weekDays) {
      boardDays.push({
        name: day.name,
        date: day.date,
        shifts: this.previewShiftsForDate(day.date)
      });
    }

    return boardDays;
  }

  async ngOnInit(): Promise<void> {
    await this.refreshPage();
  }

  async refreshPage(): Promise<void> {
    await this.runAction('Scheduling data loaded', async () => {
      await this.loadPageData();
    });
  }

  async createShiftTemplate(): Promise<void> {
    await this.runAction('Template created', async () => {
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
    await this.runAction('Demand created', async () => {
      await this.schedulingApi.createShiftDemand(
        this.selectedDemandDate,
        this.selectedTemplateId,
        this.requiredEmployeeCount
      );

      await this.loadShiftDemand();
      this.schedulePreview = null;
    });
  }

  async deleteShiftDemand(demand: ShiftDemandResponse): Promise<void> {
    await this.runAction('Demand removed', async () => {
      await this.schedulingApi.deleteShiftDemand(demand.id);
      await this.loadShiftDemand();
      this.schedulePreview = null;
    });
  }

  async previewSchedule(): Promise<void> {
    await this.runAction('Schedule preview created', async () => {
      this.schedulePreview = await this.schedulingApi.previewSchedule(this.weekStart);
    });
  }

  async saveScheduleRun(): Promise<void> {
    await this.runAction('Schedule run saved', async () => {
      this.selectedRun = await this.schedulingApi.saveScheduleRun(this.weekStart);
      await this.loadScheduleRuns();
    });
  }

  async openScheduleRun(runId: string): Promise<void> {
    await this.runAction('Schedule run opened', async () => {
      this.selectedRun = await this.schedulingApi.loadScheduleRun(runId);
    });
  }

  changeWeekStart(value: string): void {
    this.weekStart = value;
    this.weekDays = this.buildWeekDays(value);
    this.selectedDemandDate = this.weekDays[0]?.date || '';
    this.schedulePreview = null;
    this.selectedRun = null;
  }

  private async loadPageData(): Promise<void> {
    await this.loadShiftTemplates();
    await this.loadShiftDemand();
    await this.loadScheduleRuns();

    if (this.shiftTemplates.length > 0 && this.selectedTemplateId === '') {
      this.selectedTemplateId = this.shiftTemplates[0].id;
    }
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

  private demandExists(demandDate: string, shiftTemplateId: string): boolean {
    for (const demand of this.shiftDemand) {
      if (
        demand.demand_date === demandDate &&
        demand.shift_template_id === shiftTemplateId
      ) {
        return true;
      }
    }

    return false;
  }

  private previewShiftsForDate(demandDate: string): ScheduleShiftPreviewResponse[] {
    const shifts: ScheduleShiftPreviewResponse[] = [];

    if (this.schedulePreview === null) {
      return shifts;
    }

    for (const shift of this.schedulePreview.shifts) {
      if (shift.demand_date === demandDate) {
        shifts.push(shift);
      }
    }

    return shifts;
  }

  private buildWeekDays(weekStart: string): WeekDay[] {
    const days: WeekDay[] = [];

    if (weekStart === '') {
      return days;
    }

    for (let index = 0; index < this.weekdayNames.length; index++) {
      days.push({
        name: this.weekdayNames[index],
        date: this.addDays(weekStart, index)
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
