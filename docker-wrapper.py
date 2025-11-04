# !/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def select_environment():
	"""Выбор окружения"""
	print("Выберите окружение:")
	print("1) dev")
	print("2) prod")

	try:
		choice = input("Введите номер [1]: ").strip()
	except (EOFError, KeyboardInterrupt):
		print("\nПрервано пользователем")
		sys.exit(130)

	if choice == "" or choice == "1":
		return "dev"
	elif choice == "2":
		return "prod"
	else:
		print("Неверный выбор")
		sys.exit(1)

def main():
	project_root = Path.cwd()

	env = select_environment()
	env_dir = project_root / ".deployment" / env

	if not env_dir.exists():
		print(f"Директория {env_dir} не найдена!")
		sys.exit(1)

	compose_file = env_dir / "docker-compose.yml"
	env_file = env_dir / ".env"

	if not compose_file.exists():
		print(f"❌ Файл {compose_file} не найден!")
		sys.exit(1)

	if not env_file.exists():
		print(f"❌ Файл {env_file} не найден!")
		sys.exit(1)

	print(f"🎯 Работаю с окружением: {env}")
	print(f"📁 Директория: {env_dir}")
	print(f"📄 Docker compose: {compose_file}")
	print(f"📄 Env file: {env_file}")
	print(f"📁 Корень проекта: {project_root}")
	print()

	docker_args = sys.argv[1:]  # Все аргументы кроме имени скрипта

	if not docker_args:
		print("❌ Не указана команда для docker compose")
		print("Примеры:")
		print("  python docker-wrapper.py up -d")
		print("  python docker-wrapper.py ps")
		print("  python docker-wrapper.py logs -f")
		print("  python docker-wrapper.py down")
		sys.exit(1)

	command = [
		"docker", "compose",
		"--project-directory", str(project_root),
		"-f", str(compose_file),
		"--env-file", str(env_file)
	] + docker_args

	# Запускаем команду
	try:
		subprocess.run(command, check=True)
	except subprocess.CalledProcessError as e:
		sys.exit(e.returncode)
	except KeyboardInterrupt:
		print("\nПрервано пользователем")
		sys.exit(130)

if __name__ == "__main__":
	main()