import { api } from '@/services/api';import type { TodayData } from '@/types/today';export const todayService={get:()=>api.get<TodayData>('/today').then(r=>r.data)}
