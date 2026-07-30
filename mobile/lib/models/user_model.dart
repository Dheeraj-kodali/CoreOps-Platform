class UserModel {
  final String id;
  final String username;
  final String? email;
  final String fullName;
  final String? phoneNumber;

  UserModel({
    required this.id,
    required this.username,
    this.email,
    required this.fullName,
    this.phoneNumber,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String?,
      fullName: json['full_name'] as String,
      phoneNumber: json['phone_number'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'full_name': fullName,
      'phone_number': phoneNumber,
    };
  }
}
