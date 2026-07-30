class PersonModel {
  final String personId;
  final String name;
  final String phone;
  final String village;
  final String? address;
  final String firstVisit;
  final String lastVisit;
  final int totalVisits;
  final String createdAt;
  final String updatedAt;

  PersonModel({
    required this.personId,
    required this.name,
    required this.phone,
    required this.village,
    this.address,
    required this.firstVisit,
    required this.lastVisit,
    required this.totalVisits,
    required this.createdAt,
    required this.updatedAt,
  });

  factory PersonModel.fromJson(Map<String, dynamic> json) {
    return PersonModel(
      personId: json['person_id'] as String,
      name: json['name'] as String,
      phone: json['phone'] as String,
      village: json['village'] as String,
      address: json['address'] as String?,
      firstVisit: json['first_visit'] as String,
      lastVisit: json['last_visit'] as String,
      totalVisits: json['total_visits'] as int? ?? 1,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'person_id': personId,
      'name': name,
      'phone': phone,
      'village': village,
      'address': address,
      'first_visit': firstVisit,
      'last_visit': lastVisit,
      'total_visits': totalVisits,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }
}
