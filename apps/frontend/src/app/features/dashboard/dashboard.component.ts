import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  readonly metrics = [
    { label: 'Employees', value: '0', note: 'Core model pending' },
    { label: 'Availability Rows', value: '0', note: 'Google Sheets sync pending' },
    { label: 'Open Conflicts', value: '0', note: 'Scheduler pending' },
    { label: 'Coverage Rate', value: '--', note: 'No active schedule' }
  ];

  readonly pipeline = [
    { title: 'Import availability', status: 'Phase 3' },
    { title: 'Validate planning data', status: 'Phase 3' },
    { title: 'Run optimization', status: 'Phase 4' },
    { title: 'Review analytics', status: 'Phase 5' }
  ];

  readonly signals = [
    { label: 'Backend API', value: '/api/v1/health', status: 'Ready' },
    { label: 'PostgreSQL', value: 'Docker service', status: 'Configured' },
    { label: 'Redis', value: 'Docker service', status: 'Configured' },
    { label: 'Worker', value: 'Celery service', status: 'Configured' }
  ];
}

