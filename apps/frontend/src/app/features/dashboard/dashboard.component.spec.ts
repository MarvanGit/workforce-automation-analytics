/// <reference types="jasmine" />

import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    spyOn(component, 'refreshDashboard').and.resolveTo();
    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });

  it('calculates availability totals for the overview', () => {
    component.availabilityDays = [
      {
        weekday: 'Monday',
        work_date: '2026-06-08',
        available_employee_count: 3,
        unavailable_employee_count: 1,
        available_hours: 24
      },
      {
        weekday: 'Tuesday',
        work_date: '2026-06-09',
        available_employee_count: 2,
        unavailable_employee_count: 2,
        available_hours: 16
      }
    ];

    expect(component.availableEmployeeTotal).toBe(5);
    expect(component.hasAvailabilityData).toBeTrue();
  });

  it('calculates demand totals for the overview', () => {
    component.shiftDemand = [
      {
        id: 'demand-1',
        demand_date: '2026-06-08',
        weekday: 'Monday',
        shift_template_id: 'template-1',
        shift_template_name: 'Morning',
        shift_start_time: '09:00',
        shift_end_time: '17:00',
        required_employee_count: 2
      },
      {
        id: 'demand-2',
        demand_date: '2026-06-09',
        weekday: 'Tuesday',
        shift_template_id: 'template-1',
        shift_template_name: 'Morning',
        shift_start_time: '09:00',
        shift_end_time: '17:00',
        required_employee_count: 3
      }
    ];

    expect(component.demandEmployeeTotal).toBe(5);
    expect(component.hasShiftDemand).toBeTrue();
  });
});
