/// <reference types="jasmine" />

import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AppComponent } from './app.component';
import { routes } from './app.routes';
import { AnalyticsPageComponent } from './features/analytics/analytics-page.component';
import { AvailabilityPageComponent } from './features/availability/availability-page.component';
import { ImportsPageComponent } from './features/imports/imports-page.component';
import { SchedulingPageComponent } from './features/scheduling/scheduling-page.component';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([])]
    }).compileComponents();
  });

  it('creates the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;

    expect(app).toBeTruthy();
  });

  it('routes navbar pages to their own components', () => {
    expect(routeComponent('imports')).toBe(ImportsPageComponent);
    expect(routeComponent('availability')).toBe(AvailabilityPageComponent);
    expect(routeComponent('scheduling')).toBe(SchedulingPageComponent);
    expect(routeComponent('analytics')).toBe(AnalyticsPageComponent);
  });
});

function routeComponent(path: string): unknown {
  return routes.find((route) => route.path === path)?.component;
}
