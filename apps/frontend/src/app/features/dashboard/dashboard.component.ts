import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { API_BASE_URL } from '../../core/api/api.config';

interface EmployeeResponse {
  id: string;
  employee_code: string;
  full_name: string;
}

interface EmployeesResponse {
  rows: EmployeeResponse[];
  row_count: number;
}

interface AvailabilityDaySummary {
  weekday: string;
  work_date: string;
  available_employee_count: number;
  unavailable_employee_count: number;
  available_hours: number;
}

interface AvailabilitySummaryResponse {
  days: AvailabilityDaySummary[];
  employee_count: number;
}

interface ShiftTemplateResponse {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
}

interface ShiftTemplatesResponse {
  rows: ShiftTemplateResponse[];
  row_count: number;
}

interface ShiftDemandResponse {
  id: string;
  demand_date: string;
  weekday: string;
  shift_template_id: string;
  shift_template_name: string;
  shift_start_time: string;
  shift_end_time: string;
  required_employee_count: number;
}

interface ShiftDemandWeekResponse {
  rows: ShiftDemandResponse[];
  row_count: number;
}

interface ScheduledEmployeeResponse {
  employee_id: string;
  employee_code: string;
  employee_name: string;
}

interface ScheduleShiftPreviewResponse {
  demand_id: string;
  demand_date: string;
  weekday: string;
  shift_template_name: string;
  shift_start_time: string;
  shift_end_time: string;
  required_employee_count: number;
  assigned_employees: ScheduledEmployeeResponse[];
  missing_employee_count: number;
}

interface SchedulePreviewResponse {
  shifts: ScheduleShiftPreviewResponse[];
  shift_count: number;
  assignment_count: number;
  warnings: string[];
}

interface ScheduleRunSummaryResponse {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
}

interface ScheduleRunsResponse {
  rows: ScheduleRunSummaryResponse[];
  row_count: number;
}

interface SavedScheduledShiftResponse {
  id: string;
  employee_code: string;
  employee_name: string;
  shift_date: string;
  shift_template_name: string;
  start_datetime: string;
  end_datetime: string;
}

interface SavedScheduleRunResponse {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
  scheduled_shifts: SavedScheduledShiftResponse[];
  scheduled_shift_count: number;
  warnings: string[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  private readonly http = inject(HttpClient);

  weekStart = '2026-06-08';
  shiftName = 'Morning';
  shiftStart = '09:00';
  shiftEnd = '17:00';
  requiredEmployeeCount = 1;
  selectedTemplateId = '';

  employees: EmployeeResponse[] = [];
  availabilityDays: AvailabilityDaySummary[] = [];
  shiftTemplates: ShiftTemplateResponse[] = [];
  shiftDemand: ShiftDemandResponse[] = [];
  schedulePreview: SchedulePreviewResponse | null = null;
  scheduleRuns: ScheduleRunSummaryResponse[] = [];
  selectedRun: SavedScheduleRunResponse | null = null;

  isLoading = false;
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

  async ngOnInit(): Promise<void> {
    await this.refreshDashboard();
  }

  async refreshDashboard(): Promise<void> {
    await this.runAction('Dashboard data loaded', async () => {
      const employees = await this.get<EmployeesResponse>('/employees');
      const templates = await this.get<ShiftTemplatesResponse>('/shift-templates');
      const demand = await this.get<ShiftDemandWeekResponse>(
        `/shift-demand?week_start=${this.weekStart}`
      );

      this.employees = employees.rows;
      this.shiftTemplates = templates.rows;
      this.shiftDemand = demand.rows;

      if (this.shiftTemplates.length > 0 && this.selectedTemplateId === '') {
        this.selectedTemplateId = this.shiftTemplates[0].id;
      }

      await this.loadAvailabilitySummary();
      await this.loadScheduleRuns();
    });
  }

  async importAvailability(): Promise<void> {
    await this.runAction('Availability imported', async () => {
      await this.post(`/google-sheets/availability/import?week_start=${this.weekStart}`, {});
      await this.loadAvailabilitySummary();
    });
  }

  async createShiftTemplate(): Promise<void> {
    await this.runAction('Shift template created', async () => {
      const template = await this.post<ShiftTemplateResponse>('/shift-templates', {
        name: this.shiftName,
        start_time: this.shiftStart,
        end_time: this.shiftEnd,
        active: true
      });

      this.selectedTemplateId = template.id;
      await this.loadShiftTemplates();
    });
  }

  async createShiftDemand(): Promise<void> {
    await this.runAction('Shift demand created', async () => {
      await this.post('/shift-demand', {
        demand_date: this.weekStart,
        shift_template_id: this.selectedTemplateId,
        required_employee_count: this.requiredEmployeeCount,
        notes: null
      });

      await this.loadShiftDemand();
    });
  }

  async previewSchedule(): Promise<void> {
    await this.runAction('Schedule preview generated', async () => {
      this.schedulePreview = await this.get<SchedulePreviewResponse>(
        `/scheduling/preview?week_start=${this.weekStart}`
      );
    });
  }

  async saveScheduleRun(): Promise<void> {
    await this.runAction('Schedule run saved', async () => {
      this.selectedRun = await this.post<SavedScheduleRunResponse>(
        `/scheduling/runs?week_start=${this.weekStart}`,
        {}
      );
      await this.loadScheduleRuns();
    });
  }

  async openScheduleRun(runId: string): Promise<void> {
    await this.runAction('Schedule run opened', async () => {
      this.selectedRun = await this.get<SavedScheduleRunResponse>(
        `/scheduling/runs/${runId}`
      );
    });
  }

  useQuickShift(shift: { name: string; start: string; end: string }): void {
    this.shiftName = shift.name;
    this.shiftStart = shift.start;
    this.shiftEnd = shift.end;
  }

  private async loadAvailabilitySummary(): Promise<void> {
    const summary = await this.get<AvailabilitySummaryResponse>(
      `/availability/summary?week_start=${this.weekStart}`
    );
    this.availabilityDays = summary.days;
  }

  private async loadShiftTemplates(): Promise<void> {
    const templates = await this.get<ShiftTemplatesResponse>('/shift-templates');
    this.shiftTemplates = templates.rows;
  }

  private async loadShiftDemand(): Promise<void> {
    const demand = await this.get<ShiftDemandWeekResponse>(
      `/shift-demand?week_start=${this.weekStart}`
    );
    this.shiftDemand = demand.rows;
  }

  private async loadScheduleRuns(): Promise<void> {
    const runs = await this.get<ScheduleRunsResponse>('/scheduling/runs');
    this.scheduleRuns = runs.rows;
  }

  private async runAction(message: string, action: () => Promise<void>): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      await action();
      this.message = message;
    } catch (error) {
      this.errorMessage = this.errorText(error);
    } finally {
      this.isLoading = false;
    }
  }

  private async get<T>(path: string): Promise<T> {
    return firstValueFrom(this.http.get<T>(`${API_BASE_URL}${path}`));
  }

  private async post<T>(path: string, body: object): Promise<T> {
    return firstValueFrom(this.http.post<T>(`${API_BASE_URL}${path}`, body));
  }

  private errorText(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }

    return 'Request failed';
  }
}
