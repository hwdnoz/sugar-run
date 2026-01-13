.PHONY: help up down logs clean build rebuild restart backend-logs frontend-logs eval eval-latest view-scores list-sessions clean-detections clean-evals
.DEFAULT_GOAL := help

help:
	@echo "🏀 Basketball Tracker - Commands"
	@echo "================================"
	@echo ""
	@echo "📊 Evaluation Commands:"
	@echo "  make eval VIDEO=trim.mp4 SESSION=<id>  Evaluate a specific session"
	@echo "  make eval-latest VIDEO=trim.mp4        Evaluate the most recent session"
	@echo "  make view-scores                       View evaluation history"
	@echo "  make list-sessions                     List all available sessions"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make up              Start all services in detached mode"
	@echo "  make down            Stop all services"
	@echo "  make build           Build all Docker images"
	@echo "  make rebuild         Clean rebuild (down, build --no-cache, up)"
	@echo "  make restart         Restart all services"
	@echo "  make logs            Follow logs from all services"
	@echo "  make backend-logs    Follow logs from backend only"
	@echo "  make frontend-logs   Follow logs from frontend only"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  make clean           Stop services and remove volumes"
	@echo "  make clean-detections Remove all detection sessions"
	@echo "  make clean-evals      Remove evaluation history"
	@echo ""
	@echo "📖 Examples:"
	@echo "  make eval VIDEO=trim.mp4 SESSION=20260113_055543"
	@echo "  make eval-latest VIDEO=trim.mp4"

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

# Evaluation Commands

eval:
	@if [ -z "$(VIDEO)" ] || [ -z "$(SESSION)" ]; then \
		echo "❌ Error: VIDEO and SESSION are required"; \
		echo "Usage: make eval VIDEO=trim.mp4 SESSION=<session_id>"; \
		echo ""; \
		echo "Available sessions:"; \
		docker exec basketball-tracker-backend ls -1 /tmp/detections/ 2>/dev/null | grep metadata.json | sed 's/_metadata.json//' || echo "No sessions found"; \
		exit 1; \
	fi
	@echo "🚀 Running evaluation for $(VIDEO) with session $(SESSION)..."
	@cd evaluations && ./run_evaluation.sh $(VIDEO) $(SESSION)

eval-latest:
	@if [ -z "$(VIDEO)" ]; then \
		echo "❌ Error: VIDEO is required"; \
		echo "Usage: make eval-latest VIDEO=trim.mp4"; \
		exit 1; \
	fi
	@echo "🔍 Finding latest session..."
	@LATEST=$$(docker exec basketball-tracker-backend ls -1t /tmp/detections/ 2>/dev/null | grep metadata.json | head -1 | sed 's/_metadata.json//' || echo ""); \
	if [ -z "$$LATEST" ]; then \
		echo "❌ No sessions found. Upload a video first at http://localhost:5173"; \
		exit 1; \
	fi; \
	echo "📊 Latest session: $$LATEST"; \
	cd evaluations && ./run_evaluation.sh $(VIDEO) $$LATEST

view-scores:
	@cd evaluations && ./view_scores.sh

list-sessions:
	@echo "📋 Available Detection Sessions:"
	@echo "================================"
	@docker exec basketball-tracker-backend ls -1t /tmp/detections/ 2>/dev/null | grep metadata.json | sed 's/_metadata.json//' | nl || echo "No sessions found"
	@echo ""
	@echo "Use: make eval VIDEO=trim.mp4 SESSION=<session_id>"

clean-detections:
	@echo "⚠️  This will delete all detection sessions and saved frames"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker exec basketball-tracker-backend rm -rf /tmp/detections/*; \
		docker exec basketball-tracker-backend mkdir -p /tmp/detections; \
		echo "✅ All detections cleared"; \
	else \
		echo "❌ Cancelled"; \
	fi

clean-evals:
	@echo "⚠️  This will delete all evaluation history"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f evaluations/results/evaluation_history.jsonl; \
		echo "✅ Evaluation history cleared"; \
	else \
		echo "❌ Cancelled"; \
	fi
