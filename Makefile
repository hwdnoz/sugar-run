.PHONY: help up down logs build rebuild restart
.DEFAULT_GOAL := help

help:
	@echo "🏀 Basketball Tracker - Commands"
	@echo "================================"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make up                Start all services in detached mode"
	@echo "  make down              Stop all services"
	@echo "  make build             Build all Docker images"
	@echo "  make rebuild           Clean rebuild (down, build --no-cache, up)"
	@echo "  make restart           Restart all services"
	@echo "  make logs              Follow logs from all services"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

rebuild:
	docker-compose down && docker-compose build --no-cache && docker-compose up -d

restart:
	docker-compose restart

logs:
	docker-compose logs -f
