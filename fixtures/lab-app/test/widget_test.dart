import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_harness_lab/main.dart';

void main() {
  testWidgets('shows the initial tasks', (tester) async {
    await tester.pumpWidget(const HarnessLabApp());
    expect(find.text('Harness Lab'), findsOneWidget);
    expect(find.text('Inspect harness'), findsOneWidget);
    expect(find.text('Run verification'), findsOneWidget);
  });

  testWidgets('adds a task from the dialog', (tester) async {
    await tester.pumpWidget(const HarnessLabApp());
    await tester.tap(find.byTooltip('Add task'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('task-title')), 'Write a smoke test');
    await tester.tap(find.text('Save'));
    await tester.pumpAndSettle();
    expect(find.text('Write a smoke test'), findsOneWidget);
  });

  testWidgets('marks a task as done', (tester) async {
    await tester.pumpWidget(const HarnessLabApp());
    final checkbox = find.byKey(const Key('task-toggle-1'));
    expect(tester.widget<Checkbox>(checkbox).value, isFalse);
    await tester.tap(checkbox);
    await tester.pumpAndSettle();
    expect(tester.widget<Checkbox>(checkbox).value, isTrue);
  });
}
