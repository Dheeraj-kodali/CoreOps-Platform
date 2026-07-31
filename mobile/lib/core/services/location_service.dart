import 'package:geolocator/geolocator.dart';

class LocationResult {
  final double? latitude;
  final double? longitude;
  final bool isSuccess;
  final String? errorMessage;
  final bool isPermanentlyDenied;

  LocationResult({
    this.latitude,
    this.longitude,
    required this.isSuccess,
    this.errorMessage,
    this.isPermanentlyDenied = false,
  });

  String get formattedCoordinates {
    if (latitude != null && longitude != null) {
      return '${latitude!.toStringAsFixed(6)}, ${longitude!.toStringAsFixed(6)}';
    }
    return 'Location Unavailable';
  }
}

class LocationService {
  static Future<LocationResult> getCurrentLocation() async {
    try {
      // 1. Check if location services (GPS) are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return LocationResult(
          isSuccess: false,
          errorMessage: 'GPS is disabled. Please enable location services.',
        );
      }

      // 2. Check location permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return LocationResult(
            isSuccess: false,
            errorMessage: 'Location permission denied. GPS coordinates are needed for visitor registration.',
          );
        }
      }

      if (permission == LocationPermission.deniedForever) {
        return LocationResult(
          isSuccess: false,
          isPermanentlyDenied: true,
          errorMessage: 'Location permission permanently denied. Please enable location in App Settings.',
        );
      }

      // 3. Acquire position with fallback & timeout
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      ).catchError((_) async {
        // Fallback to last known position if high accuracy timeout occurs
        final lastKnown = await Geolocator.getLastKnownPosition();
        if (lastKnown != null) return lastKnown;
        throw Exception('Location acquisition timed out');
      });

      return LocationResult(
        latitude: position.latitude,
        longitude: position.longitude,
        isSuccess: true,
      );
    } catch (e) {
      return LocationResult(
        isSuccess: false,
        errorMessage: 'Failed to acquire GPS location: ${e.toString()}',
      );
    }
  }

  static Future<void> openSettings() async {
    await Geolocator.openAppSettings();
  }
}
