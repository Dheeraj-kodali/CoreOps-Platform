import { SettingApi } from '../services/api/setting-api';

export class SettingsRepository {
  static async getSettings(): Promise<any> {
    return await SettingApi.getSettings();
  }

  static async updateSettings(payload: any): Promise<any> {
    return await SettingApi.updateSettings(payload);
  }
}
