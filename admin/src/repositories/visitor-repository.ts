import { VisitorApi } from '../services/api/visitor-api';
import { Visitor, VisitorListResponse } from '../types/visitor';

export class VisitorRepository {
  static async getVisitors(params?: Record<string, any>): Promise<VisitorListResponse> {
    return await VisitorApi.list(params);
  }

  static async getVisitorById(id: string): Promise<Visitor> {
    return await VisitorApi.getById(id);
  }

  static async checkDuplicate(name: string, phoneNumber: string, date: string): Promise<{ is_duplicate: boolean; existing_record?: Visitor }> {
    return await VisitorApi.checkDuplicate({
      name,
      phone_number: phoneNumber,
      visitor_date: date,
    });
  }

  static async registerVisitor(payload: Partial<Visitor>): Promise<Visitor> {
    return await VisitorApi.create(payload);
  }

  static async updateVisitor(id: string, payload: Partial<Visitor>): Promise<Visitor> {
    return await VisitorApi.update(id, payload);
  }

  static async deleteVisitor(id: string): Promise<void> {
    await VisitorApi.delete(id);
  }
}
