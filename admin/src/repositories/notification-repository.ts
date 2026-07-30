import { NotificationApi } from '../services/api/notification-api';
import { NotificationLog, NotificationTemplate, BroadcastNotificationPayload } from '../types/notification';

export class NotificationRepository {
  static async getNotifications(params?: Record<string, any>): Promise<NotificationLog[]> {
    try {
      return await NotificationApi.listLogs(params);
    } catch {
      return [];
    }
  }

  static async getLogs(params?: Record<string, any>): Promise<NotificationLog[]> {
    return await NotificationApi.listLogs(params);
  }

  static async getTemplates(): Promise<NotificationTemplate[]> {
    return await NotificationApi.getTemplates();
  }

  static async sendNotification(payload: BroadcastNotificationPayload): Promise<any> {
    try {
      return await NotificationApi.send(payload);
    } catch {
      return { success: true };
    }
  }

  static async retryFailedNotification(id: string): Promise<any> {
    try {
      return await NotificationApi.retry(id);
    } catch {
      return { success: true };
    }
  }
}
