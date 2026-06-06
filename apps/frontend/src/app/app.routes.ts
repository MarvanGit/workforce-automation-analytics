import { Routes } from '@angular/router';

import { AnalyticsPageComponent } from './features/analytics/analytics-page.component';
import { AvailabilityPageComponent } from './features/availability/availability-page.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ImportsPageComponent } from './features/imports/imports-page.component';
import { SchedulingPageComponent } from './features/scheduling/scheduling-page.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardComponent
  },
  {
    path: 'imports',
    component: ImportsPageComponent
  },
  {
    path: 'availability',
    component: AvailabilityPageComponent
  },
  {
    path: 'scheduling',
    component: SchedulingPageComponent
  },
  {
    path: 'analytics',
    component: AnalyticsPageComponent
  },
  {
    path: '**',
    redirectTo: ''
  }
];
