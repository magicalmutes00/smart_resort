import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../features/menu/data/menu_repository.dart';
import '../../../core/network/api_client.dart';

class MenuItemFormScreen extends ConsumerStatefulWidget {
  const MenuItemFormScreen({super.key});

  @override
  ConsumerState<MenuItemFormScreen> createState() => _MenuItemFormScreenState();
}

class _MenuItemFormScreenState extends ConsumerState<MenuItemFormScreen> {
  final _name = TextEditingController();
  final _desc = TextEditingController();
  final _price = TextEditingController();
  final _prep = TextEditingController();
  String? _categoryId;
  List<Map<String, dynamic>> _categories = [];
  bool _saving = false;
  String? _result;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    final repo = MenuRepository(ApiClient());
    final list = await repo.getCategories();
    setState(() {
      _categories = list;
      if (list.isNotEmpty) _categoryId = list.first['id']?.toString();
    });
  }

  Future<void> _submit() async {
    setState(() { _saving = true; _result = null; });
    final repo = MenuRepository(ApiClient());
    final ok = await repo.addItem(
      name: _name.text.trim(),
      description: _desc.text.trim().isNotEmpty ? _desc.text.trim() : null,
      price: double.tryParse(_price.text.trim()) ?? 0,
      prepTime: int.tryParse(_prep.text.trim()) ?? 0,
      categoryId: _categoryId ?? '',
    );
    setState(() { _saving = false; _result = ok ? 'Item added!' : 'Failed'; });
    if (ok && mounted) {
      _name.clear();
      _desc.clear();
      _price.clear();
      _prep.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Menu Item')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(controller: _name, decoration: const InputDecoration(labelText: 'Name')),
            TextField(controller: _desc, decoration: const InputDecoration(labelText: 'Description (optional)')),
            Row(children: [
              Expanded(child: TextField(controller: _price, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Price'))),
              const SizedBox(width: 8),
              Expanded(child: TextField(controller: _prep, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Prep time (min)'))),
            ]),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _categoryId,
              hint: const Text('Category'),
              items: _categories.map((c) => DropdownMenuItem(value: c['id']?.toString(), child: Text(c['name']?.toString() ?? ''))).toList(),
              onChanged: (v) => setState(() => _categoryId = v),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _saving ? null : _submit,
              child: _saving ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Save'),
            ),
            if (_result != null) ...[
              const SizedBox(height: 12),
              Text(_result!, textAlign: TextAlign.center, style: TextStyle(color: _result == 'Item added!' ? Colors.green : Colors.red)),
            ],
          ],
        ),
      ),
    );
  }
}
