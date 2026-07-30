class VisitModel {
  final String visitId;
  final String personId;
  final String checkIn;
  final String? checkOut;
  final String purpose;
  final int groupMembers;
  final String? notes;
  final String status;
  final String createdAt;
  final String updatedAt;

  // Joined Person Details
  final String? personName;
  final String? personPhone;
  final String? personVillage;
  final int? totalVisits;

  VisitModel({
    required this.visitId,
    required this.personId,
    required this.checkIn,
    this.checkOut,
    required this.purpose,
    required this.groupMembers,
    this.notes,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.personName,
    this.personPhone,
    this.personVillage,
    this.totalVisits,
  });

  factory VisitModel.fromJson(Map<String, dynamic> json) {
    return VisitModel(
      visitId: (json['visit_id'] ?? json['id']) as String,
      personId: json['person_id'] as String,
      checkIn: (json['check_in'] ?? json['time_in']) as String,
      checkOut: (json['check_out'] ?? json['time_out']) as String?,
      purpose: json['purpose'] as String,
      groupMembers: (json['group_members'] ?? json['persons_count'] ?? 1) as int,
      notes: json['notes'] as String?,
      status: (json['status'] ?? 'CHECKED_IN') as String,
      createdAt: (json['created_at'] ?? '') as String,
      updatedAt: (json['updated_at'] ?? '') as String,
      personName: json['person_name'] ?? json['name'],
      personPhone: json['person_phone'] ?? json['phone'] ?? json['phone_number'],
      personVillage: json['person_village'] ?? json['village'],
      totalVisits: json['total_visits'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'visit_id': visitId,
      'person_id': personId,
      'check_in': checkIn,
      'check_out': checkOut,
      'purpose': purpose,
      'group_members': groupMembers,
      'notes': notes,
      'status': status,
      'created_at': createdAt,
      'updated_at': updatedAt,
      'person_name': personName,
      'person_phone': personPhone,
      'person_village': personVillage,
      'total_visits': totalVisits,
    };
  }
}
