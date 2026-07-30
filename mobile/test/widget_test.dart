import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:temple_visitor_app/main.dart';

void main() {
  testWidgets('TempleVisitorApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: TempleVisitorApp(),
      ),
    );
    expect(find.byType(TempleVisitorApp), findsOneWidget);
  });
}
