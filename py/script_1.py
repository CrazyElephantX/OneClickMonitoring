# Сохраняем все файлы
files_created = {
    "setup.sh": main_setup_script,
    "stop.sh": stop_script,
    "cleanup.sh": cleanup_script,
    "status.sh": status_script,
    "generate-more-logs.sh": generate_more_logs_script,
    "README.md": readme_content,
    "setup.bat": windows_setup
}

print("\n" + "="*60)
print("СОЗДАНЫ СЛЕДУЮЩИЕ ФАЙЛЫ:")
print("="*60)
for filename, content in files_created.items():
    print(f"\n📄 {filename}")
    print(f"   Размер: {len(content):,} байт")
    print(f"   Строк: {content.count(chr(10)):,}")

print("\n" + "="*60)
print("ИТОГО:")
print("="*60)
print(f"Всего файлов: {len(files_created)}")
print(f"Общий размер: {sum(len(c) for c in files_created.values()):,} байт")
print("="*60)
