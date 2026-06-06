import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { API_BASE_URL } from './api.config';

export interface EmployeeResponse {
  id: string;
  employee_code: string;
  full_name: string;
}

export interface AvailabilityDaySummary {
  weekday: string;
  work_date: string;
  available_employee_count: number;
  unavailable_employee_count: number;
  available_hours: number;
}

export interface ShiftTemplateResponse {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
}

export interface ShiftDemandResponse {
  id: string;
  demand_date: string;
  weekday: string;
  shift_template_id: string;
  shift_template_name: string;
  shift_start_time: string;
  shift_end_time: string;
  required_employee_count: number;
}

export interface ScheduledEmployeeResponse {
  employee_id: string;
  employee_code: string;
  employee_name: string;
}

export interface ScheduleShiftPreviewResponse {
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

export interface SchedulePreviewResponse {
  shifts: ScheduleShiftPreviewResponse[];
  shift_count: number;
  assignment_count: number;
  warnings: string[];
}

export interface ScheduleRunSummaryResponse {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface SavedScheduledShiftResponse {
  id: string;
  employee_code: string;
  employee_name: string;
  shift_date: string;
  shift_template_name: string;
  start_datetime: string;
  end_datetime: string;
}

export interface SavedScheduleRunResponse {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
  scheduled_shifts: SavedScheduledShiftResponse[];
  scheduled_shift_count: number;
  warnings: string[];
}

interface EmployeesResponse {
  rows: EmployeeResponse[];
}

interface AvailabilitySummaryResponse {
  days: AvailabilityDaySummary[];
}

interface ShiftTemplatesResponse {
  rows: ShiftTemplateResponse[];
}

interface ShiftDemandWeekResponse {
  rows: ShiftDemandResponse[];
}

interface ScheduleRunsResponse {
  rows: ScheduleRunSummaryResponse[];
}

@Injectable({
  providedIn: 'root'
})
export class SchedulingApiService {
  private readonly http = inject(HttpClient);

  async loadEmployees(): Promise<EmployeeResponse[]> {
    const response = await this.get<EmployeesResponse>('/employees');
    return response.rows;
  }

  async loadAvailabilitySummary(weekStart: string): Promise<AvailabilityDaySummary[]> {
    const response = await this.get<AvailabilitySummaryResponse>(
      `/availability/summary?week_start=${weekStart}`
    );
    return response.days;
  }

  async loadShiftTemplates(): Promise<ShiftTemplateResponse[]> {
    const response = await this.get<ShiftTemplatesResponse>('/shift-templates');
    return response.rows;
  }

  async createShiftTemplate(
    name: string,
    startTime: string,
    endTime: string
  ): Promise<ShiftTemplateResponse> {
    return this.post<ShiftTemplateResponse>('/shift-templates', {
      name,
      start_time: startTime,
      end_time: endTime,
      active: true
    });
  }

  async loadShiftDemand(weekStart: string): Promise<ShiftDemandResponse[]> {
    const response = await this.get<ShiftDemandWeekResponse>(
      `/shift-demand?week_start=${weekStart}`
    );
    return response.rows;
  }

  async createShiftDemand(
    weekStart: string,
    shiftTemplateId: string,
    requiredEmployeeCount: number
  ): Promise<void> {
    await this.post('/shift-demand', {
      demand_date: weekStart,
      shift_template_id: shiftTemplateId,
      required_employee_count: requiredEmployeeCount,
      notes: null
    });
  }

  async importAvailability(weekStart: string): Promise<void> {
    await this.post(`/google-sheets/availability/import?week_start=${weekStart}`, {});
  }

  async previewSchedule(weekStart: string): Promise<SchedulePreviewResponse> {
    return this.get<SchedulePreviewResponse>(
      `/scheduling/preview?week_start=${weekStart}`
    );
  }

  async saveScheduleRun(weekStart: string): Promise<SavedScheduleRunResponse> {
    return this.post<SavedScheduleRunResponse>(
      `/scheduling/runs?week_start=${weekStart}`,
      {}
    );
  }

  async loadScheduleRuns(): Promise<ScheduleRunSummaryResponse[]> {
    const response = await this.get<ScheduleRunsResponse>('/scheduling/runs');
    return response.rows;
  }

  async loadScheduleRun(runId: string): Promise<SavedScheduleRunResponse> {
    return this.get<SavedScheduleRunResponse>(`/scheduling/runs/${runId}`);
  }

  private async get<T>(path: string): Promise<T> {
    return firstValueFrom(this.http.get<T>(`${API_BASE_URL}${path}`));
  }

  private async post<T>(path: string, body: object): Promise<T> {
    return firstValueFrom(this.http.post<T>(`${API_BASE_URL}${path}`, body));
  }
}
