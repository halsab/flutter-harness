import 'package:flutter/material.dart';

void main() {
  runApp(const HarnessLabApp());
}

class LabTask {
  LabTask(this.id, this.title, {this.done = false});

  final int id;
  final String title;
  bool done;
}

class HarnessLabApp extends StatefulWidget {
  const HarnessLabApp({super.key});

  @override
  State<HarnessLabApp> createState() => _HarnessLabAppState();
}

class _HarnessLabAppState extends State<HarnessLabApp> {
  final List<LabTask> tasks = [
    LabTask(1, 'Inspect harness'),
    LabTask(2, 'Run verification'),
  ];

  int nextId = 3;
  bool darkMode = false;
  final navigatorKey = GlobalKey<NavigatorState>();

  Future<void> addTask() async {
    var draftTitle = '';
    final title = await showDialog<String>(
      context: navigatorKey.currentContext!,
      builder: (dialogContext) => AlertDialog(
        title: const Text('New task'),
        content: TextField(
          key: const Key('task-title'),
          onChanged: (value) => draftTitle = value,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Task title'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () =>
                Navigator.of(dialogContext).pop(draftTitle.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (!mounted || title == null || title.isEmpty) return;
    setState(() => tasks.add(LabTask(nextId++, title)));
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: navigatorKey,
      title: 'Harness Lab',
      theme: ThemeData(colorSchemeSeed: Colors.teal, useMaterial3: true),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.teal,
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      themeMode: darkMode ? ThemeMode.dark : ThemeMode.light,
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Harness Lab'),
          actions: [
            IconButton(
              tooltip: 'Settings',
              icon: const Icon(Icons.settings),
              onPressed: () {
                navigatorKey.currentState!.push(
                  MaterialPageRoute<void>(
                    builder: (_) => _SettingsPage(
                      darkMode: darkMode,
                      onThemeChanged: (value) {
                        setState(() => darkMode = value);
                      },
                    ),
                  ),
                );
              },
            ),
          ],
        ),
        body: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: ListView.builder(
              itemCount: tasks.length,
              itemBuilder: (context, index) {
                final task = tasks[index];
                return ListTile(
                  leading: Semantics(
                    identifier: 'task-toggle-${task.id}',
                    child: Checkbox(
                      key: Key('task-toggle-${task.id}'),
                      value: task.done,
                      onChanged: (value) {
                        setState(() => task.done = value ?? false);
                      },
                    ),
                  ),
                  title: Text(
                    task.title,
                    style: TextStyle(
                      decoration:
                          task.done ? TextDecoration.lineThrough : null,
                    ),
                  ),
                  trailing: IconButton(
                    tooltip: 'Delete ${task.title}',
                    icon: const Icon(Icons.delete_outline),
                    onPressed: () {
                      setState(() => tasks.removeWhere((t) => t.id == task.id));
                    },
                  ),
                );
              },
            ),
          ),
        ),
        floatingActionButton: Semantics(
          identifier: 'add-task',
          child: FloatingActionButton(
            key: const Key('add-task'),
            tooltip: 'Add task',
            onPressed: addTask,
            child: const Icon(Icons.add),
          ),
        ),
      ),
    );
  }
}

class _SettingsPage extends StatelessWidget {
  const _SettingsPage({
    required this.darkMode,
    required this.onThemeChanged,
  });

  final bool darkMode;
  final ValueChanged<bool> onThemeChanged;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: SwitchListTile(
        title: const Text('Dark mode'),
        value: darkMode,
        onChanged: onThemeChanged,
      ),
    );
  }
}
