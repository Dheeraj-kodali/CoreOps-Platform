/// AuditInterceptor defines an extensible contract for recording audit events
/// across repository data mutations without tight coupling.
abstract class AuditInterceptor {
  Future<void> onAuditEvent({
    required String action,
    required String entityType,
    required String entityId,
    Map<String, dynamic>? oldValue,
    Map<String, dynamic>? newValue,
    String? reason,
  });
}
