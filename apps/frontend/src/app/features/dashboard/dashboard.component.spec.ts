/// <reference types="jasmine" />

import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    spyOn(component, 'refreshDashboard').and.resolveTo();
    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });

  it('groups preview shifts by day', () => {
    component.schedulePreview = {
      shifts: [
        {
          demand_id: 'demand-1',
          demand_date: '2026-06-08',
          weekday: 'Monday',
          shift_template_name: 'Morning',
          shift_start_time: '09:00',
          shift_end_time: '17:00',
          required_employee_count: 2,
          assigned_employees: [
            {
              employee_id: 'employee-1',
              employee_code: 'E001',
              employee_name: 'John Doe'
            }
          ],
          missing_employee_count: 1
        }
      ],
      shift_count: 1,
      assignment_count: 1,
      warnings: []
    };

    expect(component.previewBoardDays[0].shifts.length).toBe(1);
    expect(component.previewBoardDays[1].shifts.length).toBe(0);
  });

  it('groups saved shifts by day and shift time', () => {
    component.selectedRun = {
      id: 'run-1',
      start_date: '2026-06-08',
      end_date: '2026-06-13',
      status: 'saved',
      scheduled_shift_count: 2,
      warnings: [],
      scheduled_shifts: [
        {
          id: 'saved-shift-1',
          employee_code: 'E001',
          employee_name: 'John Doe',
          shift_date: '2026-06-08',
          shift_template_name: 'Morning',
          start_datetime: '2026-06-08T09:00:00',
          end_datetime: '2026-06-08T17:00:00'
        },
        {
          id: 'saved-shift-2',
          employee_code: 'E002',
          employee_name: 'Jane Doe',
          shift_date: '2026-06-08',
          shift_template_name: 'Morning',
          start_datetime: '2026-06-08T09:00:00',
          end_datetime: '2026-06-08T17:00:00'
        }
      ]
    };

    expect(component.savedRunBoardDays[0].shifts.length).toBe(1);
    expect(component.savedRunBoardDays[0].shifts[0].employeeCodes).toEqual([
      'E001',
      'E002'
    ]);
  });
});
