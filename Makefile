.PHONY: help up down logs clean build rebuild restart backend-logs frontend-logs
.DEFAULT_GOAL := help

help:
	@echo "Basketball Tracker - Docker Commands"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  up              Start all services in detached mode"
	@echo "  down            Stop all services"
	@echo "  build           Build all Docker images"
	@echo "  rebuild         Clean rebuild (down, build --no-cache, up)"
	@echo "  restart         Restart all services"
	@echo "  logs            Follow logs from all services"
	@echo "  backend-logs    Follow logs from backend only"
	@echo "  frontend-logs   Follow logs from frontend only"
	@echo "  clean           Stop services and remove volumes"

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

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

clean:
	docker-compose down -v
