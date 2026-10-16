import 'package:flutter/material.dart';

class TaskDetailScreen extends StatelessWidget {
  final String taskId;
  const TaskDetailScreen({super.key, required this.taskId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Task #$taskId')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _DetailRow(label: 'Type', value: 'Room Service'),
            const Divider(),
            _DetailRow(label: 'Location', value: 'Room 204'),
            const Divider(),
            _DetailRow(label: 'Priority', value: 'NORMAL'),
            const Divider(),
            _DetailRow(label: 'Status', value: 'PENDING'),
            const SizedBox(height: 32),
            FilledButton(
              onPressed: () {},
              child: const Text('Accept'),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey,
                  ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(value, style: Theme.of(context).textTheme.bodyLarge),
          ),
        ],
      ),
    );
  }
}
