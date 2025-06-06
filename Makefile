.PHONY: help install dev test build run clean

help:
	@echo "Commandes disponibles:"
	@echo "  install     - Installer les dépendances"
	@echo "  dev         - Lancer en mode développement"
	@echo "  test        - Exécuter les tests"
	@echo "  build       - Construire l'image Docker"
	@echo "  run         - Lancer avec Docker Compose"
	@echo "  clean       - Nettoyer les fichiers temporaires"

install:
	pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app

build:
	docker build -t ai-assistant-mc .

run:
	docker-compose up -d

clean:
	docker-compose down
	docker system prune -f
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
