class CommunicationSettings {
  final String id;
  final String mode; // 'MANUAL_WHATSAPP', 'META_CLOUD_API', 'DISABLED'
  final String? accessToken;
  final String? phoneNumberId;
  final String? businessAccountId;
  final bool autoSend;
  final bool allowEdit;
  final bool saveHistory;
  final bool retryFailed;
  final String updatedAt;

  CommunicationSettings({
    required this.id,
    required this.mode,
    this.accessToken,
    this.phoneNumberId,
    this.businessAccountId,
    required this.autoSend,
    required this.allowEdit,
    required this.saveHistory,
    required this.retryFailed,
    required this.updatedAt,
  });

  factory CommunicationSettings.defaultSettings() {
    return CommunicationSettings(
      id: 'comm_settings_default',
      mode: 'DISABLED',
      accessToken: null,
      phoneNumberId: null,
      businessAccountId: null,
      autoSend: false,
      allowEdit: false,
      saveHistory: true,
      retryFailed: false,
      updatedAt: DateTime.now().toIso8601String(),
    );
  }

  factory CommunicationSettings.fromJson(Map<String, dynamic> json) {
    return CommunicationSettings(
      id: json['id']?.toString() ?? 'comm_settings_default',
      mode: json['mode']?.toString() ?? 'DISABLED',
      accessToken: json['access_token']?.toString(),
      phoneNumberId: json['phone_number_id']?.toString(),
      businessAccountId: json['business_account_id']?.toString(),
      autoSend: json['auto_send'] == 1 || json['auto_send'] == true,
      allowEdit: json['allow_edit'] == 1 || json['allow_edit'] == true,
      saveHistory: json['save_history'] == 1 || json['save_history'] == true,
      retryFailed: json['retry_failed'] == 1 || json['retry_failed'] == true,
      updatedAt: json['updated_at']?.toString() ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'mode': mode,
      'access_token': accessToken,
      'phone_number_id': phoneNumberId,
      'business_account_id': businessAccountId,
      'auto_send': autoSend ? 1 : 0,
      'allow_edit': allowEdit ? 1 : 0,
      'save_history': saveHistory ? 1 : 0,
      'retry_failed': retryFailed ? 1 : 0,
      'updated_at': updatedAt,
    };
  }

  CommunicationSettings copyWith({
    String? mode,
    String? accessToken,
    String? phoneNumberId,
    String? businessAccountId,
    bool? autoSend,
    bool? allowEdit,
    bool? saveHistory,
    bool? retryFailed,
  }) {
    return CommunicationSettings(
      id: id,
      mode: mode ?? this.mode,
      accessToken: accessToken ?? this.accessToken,
      phoneNumberId: phoneNumberId ?? this.phoneNumberId,
      businessAccountId: businessAccountId ?? this.businessAccountId,
      autoSend: autoSend ?? this.autoSend,
      allowEdit: allowEdit ?? this.allowEdit,
      saveHistory: saveHistory ?? this.saveHistory,
      retryFailed: retryFailed ?? this.retryFailed,
      updatedAt: DateTime.now().toIso8601String(),
    );
  }
}


class CommunicationTemplate {
  final String id;
  final String templateType; // 'ENTRY' or 'EXIT'
  final String title;
  final String message;
  final bool isEnabled;

  CommunicationTemplate({
    required this.id,
    required this.templateType,
    required this.title,
    required this.message,
    required this.isEnabled,
  });

  factory CommunicationTemplate.fromJson(Map<String, dynamic> json) {
    return CommunicationTemplate(
      id: json['id']?.toString() ?? '',
      templateType: json['template_type']?.toString() ?? 'ENTRY',
      title: json['title']?.toString() ?? '',
      message: json['message']?.toString() ?? '',
      isEnabled: json['is_enabled'] == 1 || json['is_enabled'] == true,
    );
  }
}


class CommunicationHistory {
  final String id;
  final String visitorId;
  final String phone;
  final String channel;
  final String templateType;
  final String renderedMessage;
  final String status; // 'PENDING', 'SENT', 'FAILED'
  final String? metaMessageId;
  final String? errorMessage;
  final String? failureReason;
  final String createdAt;

  CommunicationHistory({
    required this.id,
    required this.visitorId,
    required this.phone,
    required this.channel,
    required this.templateType,
    required this.renderedMessage,
    required this.status,
    this.metaMessageId,
    this.errorMessage,
    this.failureReason,
    required this.createdAt,
  });

  factory CommunicationHistory.fromJson(Map<String, dynamic> json) {
    return CommunicationHistory(
      id: json['id']?.toString() ?? '',
      visitorId: json['visitor_id']?.toString() ?? '',
      phone: json['phone']?.toString() ?? json['visitor_id']?.toString() ?? '',
      channel: json['channel']?.toString() ?? 'WHATSAPP',
      templateType: json['template_type']?.toString() ?? json['message_type']?.toString() ?? 'ENTRY',
      renderedMessage: json['rendered_message']?.toString() ?? json['message']?.toString() ?? '',
      status: json['status']?.toString() ?? 'PENDING',
      metaMessageId: json['meta_message_id']?.toString(),
      errorMessage: json['error_message']?.toString(),
      failureReason: json['failure_reason']?.toString(),
      createdAt: json['created_at']?.toString() ?? DateTime.now().toIso8601String(),
    );
  }
}


class TempleInfo {
  final String templeName;
  final String website;
  final String googleMapsLink;
  final String donationLink;
  final String facebook;
  final String instagram;
  final String youtube;
  final String templePhone;
  final String templeAddress;

  TempleInfo({
    required this.templeName,
    required this.website,
    required this.googleMapsLink,
    required this.donationLink,
    required this.facebook,
    required this.instagram,
    required this.youtube,
    required this.templePhone,
    required this.templeAddress,
  });

  factory TempleInfo.defaultInfo() {
    return TempleInfo(
      templeName: 'Sri Kalki Seva Alayam',
      website: 'https://kalkiseva.org',
      googleMapsLink: 'https://maps.google.com/?q=Kalki+Temple',
      donationLink: 'https://kalkiseva.org/donate',
      facebook: 'https://facebook.com/kalkiseva',
      instagram: 'https://instagram.com/kalkiseva',
      youtube: 'https://youtube.com/kalkiseva',
      templePhone: '+91 98765 43210',
      templeAddress: 'Sacred Complex, Kalki Nagaram, Chittoor, AP 517001',
    );
  }
}
