import { analyticsReducer, AnalyticsState } from './analytics/reducer';
import { schedulerReducer, SchedulerState } from './scheduler/reducer';

export interface RootState {
  analytics: AnalyticsState;
  scheduler: SchedulerState;
}

export const rootReducer = {
  analytics: analyticsReducer,
  scheduler: schedulerReducer
};

// Export individual stores for Zustand usage
export { useAnalyticsStore } from './analytics/store';
export { useSchedulerStore } from './scheduler/store';

// Export actions for Redux-style usage if needed
export * from './analytics/actions';
export * from './scheduler/actions';