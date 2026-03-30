# 序境Symphony AI Kernel - Makefile
# 方便自动化脚本调用

.PHONY: build dev clean dev-start prod-start

all: build

build:
	@pnpm build

dev-start: build
	@node scripts/dev-start.js

prod-start: build
	@node scripts/prod-start.js

clean:
	@if [ -d dist ]; then rm -rf dist; fi
	@mkdir dist

dev-watch:
	@pnpm dev:watch

install:
	@pnpm install

info:
	@echo "📻 序境Symphony AI Kernel"
	@echo "🔧 开发模式: make dev-start (端口 18901)"
	@echo "🏭 生产模式: make prod-start (端口 18789)"
	@echo "🔄 自动构建: make dev-watch"
