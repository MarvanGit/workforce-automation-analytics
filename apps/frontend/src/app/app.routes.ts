import { Routes } from '@angular/router';

import { DashboardComponent } from './features/dashboard/dashboard.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardComponent
  },
  {
    path: 'imports',
    component: DashboardComponent
  },
  {
    path: 'availability',
    component: DashboardComponent
  },
  {
    path: 'scheduling',
    component: DashboardComponent
  },
  {
    path: 'analytics',
    component: DashboardComponent
  },
  {
    path: '**',
    redirectTo: ''
  }
];

