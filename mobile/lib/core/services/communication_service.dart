import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:uuid/uuid.dart';
import 'package:temple_visitor_app/core/database/sqlite_database.dart';
import 'package:temple_visitor_app/models/visitor_model.dart';
import 'package:temple_visitor_app/models/communication_models.dart';
import 'package:temple_visitor_app/core/services/app_logger.dart';

class MetaDispatchResult {
  final bool success;
  final String? metaMessageId;
  final String? errorMessage;
  final int? statusCode;

  MetaDispatchResult({
    required this.success,
    this.metaMessageId,
    this.errorMessage,
    this.statusCode,
  });
}

abstract class ChannelProvider {
  String get channelName;
  Future<MetaDispatchResult> sendMessage(String recipientPhone, String renderedMessage);
}

class ManualWhatsAppProvider implements ChannelProvider {
  @override
  String get channelName => 'MANUAL_WHATSAPP';

  @override
  Future<MetaDispatchResult> sendMessage(String recipientPhone, String renderedMessage) async {
    try {
      final cleanPhone = recipientPhone.replaceAll(RegExp(r'[^\d+]'), '');
      final encodedMessage = Uri.encodeComponent(renderedMessage);
      final url = Uri.parse('whatsapp://send?phone=$cleanPhone&text=$encodedMessage');
      
      bool launched = false;
      if (await canLaunchUrl(url)) {
        launched = await launchUrl(url);
      } else {
        final webUrl = Uri.parse('https://wa.me/$cleanPhone?text=$encodedMessage');
        launched = await launchUrl(webUrl, mode: LaunchMode.externalApplication);
      }
      return MetaDispatchResult(
        success: launched,
        errorMessage: launched ? null : 'WhatsApp application is not installed on device',
      );
    } catch (e) {
      AppLogger.error('ManualWhatsAppProvider launch failed', err: e);
      return MetaDispatchResult(success: false, errorMessage: 'Manual WhatsApp launch error: $e');
    }
  }
}

class MetaWhatsAppProvider implements ChannelProvider {
  final CommunicationSettings settings;

  MetaWhatsAppProvider(this.settings);

  @override
  String get channelName => 'META_CLOUD_API';

  @override
  Future<MetaDispatchResult> sendMessage(String recipientPhone, String renderedMessage) async {
    final token = settings.accessToken?.trim();
    final phoneId = settings.phoneNumberId?.trim();

    if (token == null || token.isEmpty) {
      const err = 'Meta Access Token is missing or empty in Communication Settings';
      AppLogger.error('MetaWhatsAppProvider validation error: $err');
      return MetaDispatchResult(success: false, errorMessage: err, statusCode: 400);
    }

    if (phoneId == null || phoneId.isEmpty) {
      const err = 'Meta Phone Number ID is missing or empty in Communication Settings';
      AppLogger.error('MetaWhatsAppProvider validation error: $err');
      return MetaDispatchResult(success: false, errorMessage: err, statusCode: 400);
    }

    final url = 'https://graph.facebook.com/v23.0/$phoneId/messages';
    
    var cleanPhone = recipientPhone.replaceAll(RegExp(r'[^\d]'), '');
    if (cleanPhone.startsWith('+')) {
      cleanPhone = cleanPhone.substring(1);
    }

    final payload = {
      'messaging_product': 'whatsapp',
      'to': cleanPhone,
      'type': 'text',
      'text': {
        'preview_url': false,
        'body': renderedMessage,
      },
    };

    final redactedToken = token.length > 10 ? '${token.substring(0, 10)}...' : token;

    debugPrint('\n==================================================');
    debugPrint('[META WHATSAPP DISPATCH EXECUTION]');
    debugPrint('1. Exact Request URL: $url');
    debugPrint('2. HTTP Method: POST');
    debugPrint('3. Request Headers: {Authorization: Bearer $redactedToken, Content-Type: application/json}');
    debugPrint('4. JSON Payload: $payload');
    debugPrint('==================================================\n');

    try {
      final dio = Dio(
        BaseOptions(
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 15),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
        ),
      );

      final response = await dio.post(
        url,
        data: payload,
        options: Options(validateStatus: (status) => status != null && status < 600),
      );

      final status = response.statusCode ?? 500;
      final data = response.data;

      debugPrint('\n==================================================');
      debugPrint('[META WHATSAPP RESPONSE RECEIVED]');
      debugPrint('5. HTTP Status Code: $status');
      debugPrint('6. Full Response Body: $data');

      if (status == 200 || status == 201) {
        String? msgId;
        if (data is Map && data['messages'] is List && (data['messages'] as List).isNotEmpty) {
          msgId = data['messages'][0]['id']?.toString();
        }
        debugPrint('7. Parsed Meta Error: NONE (Success)');
        debugPrint('8. Meta Message ID (wamid): $msgId');
        debugPrint('==================================================\n');

        return MetaDispatchResult(
          success: true,
          metaMessageId: msgId,
          statusCode: status,
        );
      } else {
        String fullErr = 'HTTP $status: ${response.data}';
        int? errCode;
        int? errSubcode;
        String? errMsg;
        String? fbTraceId;

        if (data is Map && data.containsKey('error')) {
          final errObj = data['error'];
          if (errObj is Map) {
            errMsg = errObj['message']?.toString() ?? response.statusMessage;
            errCode = errObj['code'] is int ? errObj['code'] : int.tryParse(errObj['code']?.toString() ?? '');
            errSubcode = errObj['error_subcode'] is int ? errObj['error_subcode'] : int.tryParse(errObj['error_subcode']?.toString() ?? '');
            fbTraceId = errObj['fbtrace_id']?.toString();
            fullErr = 'Meta API Error (Code: $errCode, Subcode: $errSubcode, FBTrace: $fbTraceId): $errMsg';
          }
        }

        debugPrint('7. Parsed Meta Error Details:');
        debugPrint('   - code: $errCode');
        debugPrint('   - error_subcode: $errSubcode');
        debugPrint('   - message: $errMsg');
        debugPrint('   - fbtrace_id: $fbTraceId');
        debugPrint('8. Meta Message ID (wamid): NONE (Dispatch Failed)');
        debugPrint('==================================================\n');

        return MetaDispatchResult(
          success: false,
          errorMessage: fullErr,
          statusCode: status,
        );
      }
    } on DioException catch (de, st) {
      debugPrint('\n==================================================');
      debugPrint('[META WHATSAPP HTTP EXCEPTION]');
      debugPrint('Exception Type: ${de.type}');
      debugPrint('Exception Error: ${de.error}');
      debugPrint('Exception Message: ${de.message}');
      debugPrint('Stack Trace:\n$st');
      debugPrint('==================================================\n');

      String errStr = de.message ?? 'Network connection error';
      if (de.response != null && de.response?.data != null) {
        errStr = 'HTTP ${de.response?.statusCode}: ${de.response?.data}';
      }
      return MetaDispatchResult(success: false, errorMessage: errStr, statusCode: de.response?.statusCode ?? 500);
    } catch (e, st) {
      debugPrint('\n==================================================');
      debugPrint('[META WHATSAPP UNHANDLED EXCEPTION]');
      return MetaDispatchResult(success: false, errorMessage: 'Unhandled exception: $e');
    }
  }
}

class N8NWhatsAppProvider implements ChannelProvider {
  final CommunicationSettings settings;

  N8NWhatsAppProvider(this.settings);

  @override
  String get channelName => 'N8N_AUTOMATION';

  @override
  Future<MetaDispatchResult> sendMessage(String recipientPhone, String renderedMessage) async {
    final webhookUrl = (settings.accessToken != null && settings.accessToken!.startsWith('http'))
        ? settings.accessToken!
        : 'https://n8n.kalkiseva.org/webhook/whatsapp-send';

    var cleanPhone = recipientPhone.replaceAll(RegExp(r'[^\d+]'), '');

    final payload = {
      'event': 'WHATSAPP_SEND_MESSAGE',
      'recipient_phone': cleanPhone,
      'message_text': renderedMessage,
      'message_type': 'MOBILE_DISPATCH',
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    };

    try {
      final dio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 10), receiveTimeout: const Duration(seconds: 10)));
      final res = await dio.post(webhookUrl, data: payload);
      if (res.statusCode == 200 || res.statusCode == 201) {
        return MetaDispatchResult(
          success: true,
          metaMessageId: res.data?['execution_id']?.toString() ?? 'n8n-mobile-ok',
          statusCode: res.statusCode,
        );
      } else {
        return MetaDispatchResult(
          success: false,
          errorMessage: 'HTTP ${res.statusCode}: ${res.statusMessage}',
          statusCode: res.statusCode,
        );
      }
    } catch (e) {
      return MetaDispatchResult(
        success: false,
        errorMessage: 'n8n Webhook connection error: $e',
      );
    }
  }
}

class TemplateEngine {
  static String render({
    required String templateText,
    required VisitorModel visitor,
    required TempleInfo templeInfo,
    String? volunteerName,
  }) {
    String output = templateText;

    // Spec Placeholders
    output = output.replaceAll('{name}', visitor.name);
    output = output.replaceAll('{phone}', visitor.phoneNumber);
    output = output.replaceAll('{village}', visitor.village);
    output = output.replaceAll('{persons}', visitor.personsCount.toString());
    output = output.replaceAll('{purpose}', visitor.purpose);
    output = output.replaceAll('{date}', visitor.visitorDate);
    output = output.replaceAll('{time}', visitor.timeIn);
    output = output.replaceAll('{duration}', visitor.visitDuration ?? 'N/A');
    output = output.replaceAll('{visitor_id}', visitor.visitorUuid.isNotEmpty ? visitor.visitorUuid : visitor.id);
    output = output.replaceAll('{temple}', templeInfo.templeName);
    output = output.replaceAll('{volunteer}', volunteerName ?? 'Temple Volunteer');

    // Backward Compatibility Double-Brace Placeholders
    output = output.replaceAll('{{name}}', visitor.name);
    output = output.replaceAll('{{phone}}', visitor.phoneNumber);
    output = output.replaceAll('{{date}}', visitor.visitorDate);
    output = output.replaceAll('{{time}}', visitor.timeIn);
    output = output.replaceAll('{{duration}}', visitor.visitDuration ?? 'N/A');
    output = output.replaceAll('{{visitor_id}}', visitor.visitorUuid.isNotEmpty ? visitor.visitorUuid : visitor.id);
    output = output.replaceAll('{{temple}}', templeInfo.templeName);
    output = output.replaceAll('{{temple_name}}', templeInfo.templeName);
    output = output.replaceAll('{{volunteer}}', volunteerName ?? 'Temple Volunteer');
    output = output.replaceAll('{{village}}', visitor.village);
    output = output.replaceAll('{{purpose}}', visitor.purpose);
    output = output.replaceAll('{{members}}', visitor.personsCount.toString());

    return output;
  }
}

class CommunicationService {
  Future<CommunicationSettings> getSettings() async {
    final map = await SQLiteDatabase.getCommunicationSettings();
    return CommunicationSettings.fromJson(map);
  }

  Future<void> saveSettings(CommunicationSettings settings) async {
    await SQLiteDatabase.saveCommunicationSettings(settings.toJson());
  }

  Future<MetaDispatchResult?> sendVisitorEntryMessage(VisitorModel visitor, {String? volunteerName}) async {
    return await _processMessage(visitor: visitor, templateType: 'ENTRY', volunteerName: volunteerName);
  }

  Future<MetaDispatchResult?> sendVisitorExitMessage(VisitorModel visitor, {String? volunteerName}) async {
    return await _processMessage(visitor: visitor, templateType: 'EXIT', volunteerName: volunteerName);
  }

  Future<MetaDispatchResult?> sendCheckInMessage(VisitorModel visitor) async {
    return await sendVisitorEntryMessage(visitor);
  }

  Future<MetaDispatchResult?> sendCheckOutMessage(VisitorModel visitor) async {
    return await sendVisitorExitMessage(visitor);
  }

  Future<MetaDispatchResult> dispatchDirectMessage({
    required VisitorModel visitor,
    required String templateType,
    required String customMessage,
  }) async {
    final settings = await getSettings();
    if (settings.mode == 'DISABLED') {
      return MetaDispatchResult(success: false, errorMessage: 'Communication gateway is DISABLED in settings');
    }

    ChannelProvider provider;
    if (settings.mode == 'META_CLOUD_API') {
      provider = MetaWhatsAppProvider(settings);
    } else {
      provider = ManualWhatsAppProvider();
    }

    final result = await provider.sendMessage(visitor.phoneNumber, customMessage);

    if (settings.saveHistory) {
      await SQLiteDatabase.insertCommunicationHistory({
        'id': const Uuid().v4(),
        'visitor_id': visitor.id,
        'phone': visitor.phoneNumber,
        'channel': provider.channelName,
        'template_type': templateType,
        'rendered_message': customMessage,
        'status': result.success ? 'SENT' : 'FAILED',
        'meta_message_id': result.metaMessageId,
        'error_message': result.errorMessage,
        'failure_reason': result.success ? null : result.errorMessage,
        'created_at': DateTime.now().toIso8601String(),
      });
    }

    return result;
  }

  Future<MetaDispatchResult?> _processMessage({
    required VisitorModel visitor,
    required String templateType,
    String? volunteerName,
  }) async {
    final settings = await getSettings();

    if (settings.mode == 'DISABLED') {
      AppLogger.info('Communication disabled. Skipping message.');
      return MetaDispatchResult(success: false, errorMessage: 'Communication is DISABLED in settings');
    }

    final nowStr = DateTime.now().toIso8601String();
    final historyId = const Uuid().v4();

    try {
      final templateData = await SQLiteDatabase.getTemplate(templateType);
      if (templateData == null || (templateData['is_enabled'] != 1 && templateData['is_enabled'] != true)) {
        return MetaDispatchResult(success: false, errorMessage: 'Template $templateType is disabled or missing');
      }

      final rawTemple = await SQLiteDatabase.getTempleInfo();
      final templeInfo = TempleInfo(
        templeName: rawTemple['temple_name'] ?? 'Sri Kalki Seva Alayam',
        website: rawTemple['website'] ?? 'https://kalkiseva.org',
        googleMapsLink: rawTemple['google_maps_link'] ?? '',
        donationLink: rawTemple['donation_link'] ?? '',
        facebook: rawTemple['facebook'] ?? '',
        instagram: rawTemple['instagram'] ?? '',
        youtube: rawTemple['youtube'] ?? '',
        templePhone: rawTemple['temple_phone'] ?? '',
        templeAddress: rawTemple['temple_address'] ?? '',
      );

      final renderedMessage = TemplateEngine.render(
        templateText: templateData['message'].toString(),
        visitor: visitor,
        templeInfo: templeInfo,
        volunteerName: volunteerName,
      );

      ChannelProvider provider;
      if (settings.mode == 'N8N_AUTOMATION') {
        provider = N8NWhatsAppProvider(settings);
      } else if (settings.mode == 'META_CLOUD_API') {
        provider = MetaWhatsAppProvider(settings);
      } else {
        provider = ManualWhatsAppProvider();
      }

      MetaDispatchResult result = MetaDispatchResult(success: false, errorMessage: 'Auto send disabled');

      if (settings.autoSend) {
        result = await provider.sendMessage(visitor.phoneNumber, renderedMessage);
      }

      if (settings.saveHistory) {
        final historyRow = {
          'id': historyId,
          'visitor_id': visitor.id,
          'phone': visitor.phoneNumber,
          'channel': provider.channelName,
          'template_type': templateType,
          'rendered_message': renderedMessage,
          'status': settings.autoSend ? (result.success ? 'SENT' : 'FAILED') : 'PENDING',
          'meta_message_id': result.metaMessageId,
          'error_message': result.errorMessage,
          'failure_reason': result.success ? null : (settings.autoSend ? result.errorMessage : 'Pending manual send'),
          'created_at': nowStr,
        };
        await SQLiteDatabase.insertCommunicationHistory(historyRow);
        debugPrint('\n==================================================');
        debugPrint('[COMMUNICATION HISTORY ROW INSERTED]');
        debugPrint('9. Communication History Row: $historyRow');
        debugPrint('==================================================\n');
      }

      return result;
    } catch (e, st) {
      AppLogger.error('Error processing communication message', err: e, st: st);
      return MetaDispatchResult(success: false, errorMessage: 'System error: $e');
    }
  }

  Future<List<CommunicationHistory>> getHistoryForVisitor(String visitorId) async {
    final rows = await SQLiteDatabase.getCommunicationHistoryByVisitor(visitorId);
    return rows.map((r) => CommunicationHistory.fromJson(r)).toList();
  }
}
