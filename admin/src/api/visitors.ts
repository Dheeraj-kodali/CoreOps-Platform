import { apiClient } from './client';

export interface Visitor {
  id: string;
  visitor_uuid: string;
  name: string;
  phone_number: string;
  gender: string;
  age: number;
  persons_count: number;
  village_name_custom?: string;
  purpose_id: string;
  purpose?: { name_en: string; name_te: string };
  temple_service?: string;
  visitor_date: string;
  visitor_time: string;
  volunteer_id: string;
  notes?: string;
  sync_status: string;
  created_at: string;
}

export interface VisitorListResponse {
  items: Visitor[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface VisitorQueryParams {
  search?: string;
  purpose_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
}

export const fetchVisitors = async (params: VisitorQueryParams): Promise<VisitorListResponse> => {
  const response = await apiClient.get<VisitorListResponse>('/visitors/', { params });
  return response.data;
};

export const deleteVisitor = async (id: string): Promise<void> => {
  await apiClient.delete(`/visitors/${id}`);
};

export const updateVisitor = async (id: string, data: Partial<Visitor>): Promise<Visitor> => {
  const response = await apiClient.put<Visitor>(`/visitors/${id}`, data);
  return response.data;
};
