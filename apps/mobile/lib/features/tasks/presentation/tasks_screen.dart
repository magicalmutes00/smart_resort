import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class TasksScreen extends ConsumerWidget {
  const TasksScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Tasks')),
      body: ListView.builder(
        itemCount: 5,
        itemBuilder: (context, index) => Card(
          margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          child: ListTile(
            title: Text('Task #${index + 1}'),
            subtitle: Text('Room Service — Room 204'),
            trailing: Chip(
              label: Text(
                index == 0 ? 'PENDING' : index == 1 ? 'ACCEPTED' : 'COMPLETED',
                style: const TextStyle(fontSize: 10),
              ),
              backgroundColor: index == 0
                  ? Colors.orange
                  : index == 1
                      ? Colors.blue
                      : Colors.green,
            ),
            onTap: () {},
          ),
        ),
      ),
    );
  }
}
