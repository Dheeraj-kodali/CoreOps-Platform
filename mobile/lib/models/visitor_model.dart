class VisitorModel {
  final String id;
  final String visitorUuid;
  final String name;
  final String phoneNumber;
  final String village;
  final String purpose;
  final int personsCount;
  final String? notes;
  final String visitorDate;
  final String timeIn;
  final String? timeOut;
  final String? visitDuration;
  final String status; // 'CHECKED_IN' or 'CHECKED_OUT'
  final String syncStatus;

  VisitorModel({
    required this.id,
    required this.visitorUuid,
    required this.name,
    required this.phoneNumber,
    required this.village,
    required this.purpose,
    required this.personsCount,
    this.notes,
    required this.visitorDate,
    required this.timeIn,
    this.timeOut,
    this.visitDuration,
    required this.status,
    required this.syncStatus,
  });

  factory VisitorModel.fromJson(Map<String, dynamic> json) {
    final rawName = json['name'] ?? json['person_name'];
    final nameStr = (rawName != null && rawName.toString().trim().isNotEmpty)
        ? rawName.toString().trim()
        : 'Unknown Visitor';

    final rawMembers = json['persons_count'] ?? json['group_members'];

    return VisitorModel(
      id: json['id']?.toString() ?? json['visit_id']?.toString() ?? '',
      visitorUuid: json['visitor_uuid']?.toString() ?? json['visit_id']?.toString() ?? json['id']?.toString() ?? '',
      name: nameStr,
      phoneNumber: json['phone_number']?.toString() ?? json['person_phone']?.toString() ?? json['phone']?.toString() ?? '',
      village: json['village']?.toString() ?? json['person_village']?.toString() ?? json['village_name_custom']?.toString() ?? '',
      purpose: json['purpose']?.toString() ?? json['purpose_id']?.toString() ?? 'General Darshan',
      personsCount: (rawMembers is int)
          ? rawMembers
          : int.tryParse(rawMembers?.toString() ?? '1') ?? 1,
      notes: json['notes']?.toString(),
      visitorDate: json['visitor_date']?.toString() ?? json['check_in']?.toString().split(' ')[0] ?? DateTime.now().toString().split(' ')[0],
      timeIn: json['time_in']?.toString() ?? json['check_in']?.toString().split(' ').last ?? json['visitor_time']?.toString() ?? '00:00',
      timeOut: json['time_out']?.toString() ?? json['check_out']?.toString(),
      visitDuration: json['visit_duration']?.toString(),
      status: json['status']?.toString() ?? 'CHECKED_IN',
      syncStatus: json['sync_status']?.toString() ?? 'PENDING',
    );
  }

  String get displayStatus {
    if (status == 'CHECKED_OUT') return 'Completed';
    return 'Inside Temple';
  }

  String get formattedDuration {
    if (visitDuration != null && visitDuration!.isNotEmpty && visitDuration != 'null') {
      return visitDuration!;
    }
    if (status == 'CHECKED_IN') return 'Inside Temple';
    return 'N/A';
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'visitor_uuid': visitorUuid,
      'name': name,
      'phone_number': phoneNumber,
      'village': village,
      'purpose': purpose,
      'persons_count': personsCount,
      'notes': notes,
      'visitor_date': visitorDate,
      'time_in': timeIn,
      'time_out': timeOut,
      'visit_duration': visitDuration,
      'status': status,
      'sync_status': syncStatus,
      'created_at': DateTime.now().toIso8601String(),
      'updated_at': DateTime.now().toIso8601String(),
    };
  }
}
