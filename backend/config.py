#!/usr/bin/env python3
"""
CPQ Agent 配置加载器

从 config/config.yaml 加载配置，支持 ${VAR_NAME} 环境变量替换。
"""

import os
import re
import sys
import traceback
import yaml
from dataclasses import dataclass, field
from typing import Optional


def _resolve_env_vars(value: str) -> str:
    """递归替换字符串中的 ${VAR_NAME} 占位符"""
    if not isinstance(value, str):
        return value

    def _replace(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))

    result = re.sub(r'\$\{(\w+)\}', _replace, value)
    return result


def _deep_resolve(obj):
    """深度遍历数据结构，解析所有字符串中的环境变量"""
    if isinstance(obj, str):
        return _resolve_env_vars(obj)
    elif isinstance(obj, dict):
        return {k: _deep_resolve(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_resolve(v) for v in obj]
    return obj


@dataclass
class ModelConfig:
    provider: str = "deepseek"
    model_name: str = "deepseek-v4-pro"
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9


@dataclass
class CPQConfig:
    base_url: str = "http://localhost:30000"
    client_id: str = "e5cd7e4891bf95d1d19206ce24a7b32e"
    username: str = "admin"
    password: str = "admin123"
    timeout: int = 30
    max_retries: int = 3


@dataclass
class AgentConfig:
    system_prompt: str = ""
    max_turns: int = 20
    enable_subagents: bool = True


@dataclass
class MemoryConfig:
    storage_path: str = "./data/memory"
    preferences_file: str = "preferences.md"
    max_file_size_kb: int = 500


@dataclass
class SkillsConfig:
    paths: list[str] = field(default_factory=lambda: [
        "./backend/skills/cpq-agent",
        "./backend/skills/product-search",
        "./backend/skills/bom-config",
        "./backend/skills/pricing-rules",
    ])


@dataclass
class HumanInLoopConfig:
    interrupt_on: dict = field(default_factory=lambda: {
        "create_quote": True,
        "send_quote": True,
    })


@dataclass
class SecurityConfig:
    backend: str = "state"
    permissions: dict = field(default_factory=lambda: {
        "allow_paths": ["./workspace/**"],
        "deny_paths": ["./config/**", "./data/**/*.key"],
    })


@dataclass
class LoggingConfig:
    level: str = "info"
    file: str = "./logs/agent.log"
    max_size_mb: int = 10
    backup_count: int = 3


@dataclass
class UIConfig:
    language: str = "zh-CN"
    theme: str = "auto"
    typewriter_delay_ms: int = 20
    history_retention_days: int = 30


@dataclass
class Config:
    """CPQ Agent 全局配置"""

    model: ModelConfig = field(default_factory=ModelConfig)
    cpq: CPQConfig = field(default_factory=CPQConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    skills: SkillsConfig = field(default_factory=SkillsConfig)
    human_in_loop: HumanInLoopConfig = field(default_factory=HumanInLoopConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    @classmethod
    def from_dict(cls, d: dict) -> "Config":
        """从字典构建 Config 对象"""
        resolved = _deep_resolve(d)

        cfg = cls()

        if "model" in resolved:
            m = resolved["model"]
            cfg.model = ModelConfig(
                provider=m.get("provider", "deepseek"),
                model_name=m.get("model_name", "deepseek-v4-pro"),
                api_key=m.get("api_key", ""),
                base_url=m.get("base_url", "https://api.deepseek.com"),
                temperature=float(m.get("temperature", 0.7)),
                max_tokens=int(m.get("max_tokens", 4096)),
                top_p=float(m.get("top_p", 0.9)),
            )

        if "cpq" in resolved:
            c = resolved["cpq"]
            cfg.cpq = CPQConfig(
                base_url=c.get("base_url", "http://localhost:30000"),
                client_id=c.get("client_id", "e5cd7e4891bf95d1d19206ce24a7b32e"),
                username=c.get("username", "admin"),
                password=c.get("password", "admin123"),
                timeout=int(c.get("timeout", 30)),
                max_retries=int(c.get("max_retries", 3)),
            )

        if "agent" in resolved:
            a = resolved["agent"]
            cfg.agent = AgentConfig(
                system_prompt=a.get("system_prompt", ""),
                max_turns=int(a.get("max_turns", 20)),
                enable_subagents=bool(a.get("enable_subagents", True)),
            )

        if "memory" in resolved:
            me = resolved["memory"]
            cfg.memory = MemoryConfig(
                storage_path=me.get("storage_path", "./data/memory"),
                preferences_file=me.get("preferences_file", "preferences.md"),
                max_file_size_kb=int(me.get("max_file_size_kb", 500)),
            )

        if "skills" in resolved:
            s = resolved["skills"]
            cfg.skills = SkillsConfig(
                paths=s.get("paths", []),
            )

        return cfg

    def to_dict_safe(self) -> dict:
        """返回配置字典，敏感信息脱敏"""
        d = {
            "model": {
                "provider": self.model.provider,
                "model_name": self.model.model_name,
                "api_key": self.model.api_key[:6] + "..." if self.model.api_key else "",
                "base_url": self.model.base_url,
                "temperature": self.model.temperature,
                "max_tokens": self.model.max_tokens,
                "top_p": self.model.top_p,
            },
            "cpq": {
                "base_url": self.cpq.base_url,
                "client_id": self.cpq.client_id,
                "username": self.cpq.username,
                "password": "******" if self.cpq.password else "",
                "timeout": self.cpq.timeout,
                "max_retries": self.cpq.max_retries,
            },
            "agent": {
                "system_prompt": self.agent.system_prompt[:200] + "..." if len(self.agent.system_prompt) > 200 else self.agent.system_prompt,
                "max_turns": self.agent.max_turns,
                "enable_subagents": self.agent.enable_subagents,
            },
            "skills": {
                "paths": self.skills.paths,
            },
            "logging": {
                "level": self.logging.level,
            },
            "ui": {
                "language": self.ui.language,
            },
        }
        return d


def _find_config_path(config_path: str | None = None) -> str | None:
    """定位配置文件路径（与 load_config 搜索逻辑一致）"""
    if config_path and os.path.exists(config_path):
        return os.path.abspath(config_path)

    # 环境变量（Electron 生产模式必传，优先级最高）
    env_path = os.environ.get("CONFIG_PATH")
    if env_path and os.path.exists(env_path):
        return os.path.abspath(env_path)

    # PyInstaller 打包后: 相对于 exe 所在目录的 ../config/config.yaml
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        exe_candidate = os.path.join(exe_dir, '..', 'config', 'config.yaml')
        if os.path.exists(exe_candidate):
            return os.path.abspath(exe_candidate)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(this_dir, "..", "config", "config.yaml")
    if os.path.exists(candidate):
        return os.path.abspath(candidate)

    return None


def save_config(cfg: Config, config_path: str | None = None) -> bool:
    """
    将当前配置写回 YAML 文件。

    写入路径与 load_config 搜索顺序一致，优先写入第一个找到的文件。
    如果所有候选路径都不存在，则在 backend/../config/config.yaml 创建新文件。
    返回 True 表示写入成功，False 表示失败。
    """
    target = _find_config_path(config_path)

    if target is None:
        # 所有路径都不存在 → 创建新文件
        this_dir = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(this_dir, "..", "config", "config.yaml")
        os.makedirs(os.path.dirname(target), exist_ok=True)

    try:
        d = {
            "model": {
                "provider": cfg.model.provider,
                "model_name": cfg.model.model_name,
                "api_key": cfg.model.api_key,
                "base_url": cfg.model.base_url,
                "temperature": cfg.model.temperature,
                "max_tokens": cfg.model.max_tokens,
                "top_p": cfg.model.top_p,
            },
            "cpq": {
                "base_url": cfg.cpq.base_url,
                "client_id": cfg.cpq.client_id,
                "username": cfg.cpq.username,
                "password": cfg.cpq.password,
                "timeout": cfg.cpq.timeout,
                "max_retries": cfg.cpq.max_retries,
            },
            "agent": {
                "system_prompt": cfg.agent.system_prompt,
                "max_turns": cfg.agent.max_turns,
                "enable_subagents": cfg.agent.enable_subagents,
            },
            "memory": {
                "storage_path": cfg.memory.storage_path,
                "preferences_file": cfg.memory.preferences_file,
                "max_file_size_kb": cfg.memory.max_file_size_kb,
            },
            "skills": {
                "paths": cfg.skills.paths,
            },
            "human_in_loop": {
                "interrupt_on": cfg.human_in_loop.interrupt_on,
            },
            "security": {
                "backend": cfg.security.backend,
                "permissions": cfg.security.permissions,
            },
            "logging": {
                "level": cfg.logging.level,
                "file": cfg.logging.file,
                "max_size_mb": cfg.logging.max_size_mb,
                "backup_count": cfg.logging.backup_count,
            },
            "ui": {
                "language": cfg.ui.language,
                "theme": cfg.ui.theme,
                "typewriter_delay_ms": cfg.ui.typewriter_delay_ms,
                "history_retention_days": cfg.ui.history_retention_days,
            },
        }

        # 写入临时文件再原子替换，防止写一半崩溃导致配置损坏
        import tempfile
        tmpdir = os.path.dirname(target)
        os.makedirs(tmpdir, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=tmpdir,
            delete=False,
            suffix=".yaml",
        ) as tmp:
            yaml.dump(d, tmp, allow_unicode=True, default_flow_style=False, sort_keys=False)
            tmp_path = tmp.name

        os.replace(tmp_path, target)
        print(f"[config] 配置已保存: {target}")
        return True

    except Exception as e:
        print(f"[config] 保存配置失败: {e}")
        traceback.print_exc()
        # 清理可能残留的临时文件
        if 'tmp_path' in dir() and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return False


def load_config(config_path: str | None = None) -> Config:
    """
    加载配置文件。

    搜索顺序（按优先级）：
    1. 显式指定的路径（最高优先级）
    2. 环境变量 CONFIG_PATH（Electron 生产模式下传参用）
    3. PyInstaller 打包后: 相对于 exe 所在目录的 ../config/config.yaml
    4. 相对于 backend/ 目录的 ../config/config.yaml（开发模式）
    5. 默认值（Config()）
    """
    search_paths = []

    if config_path:
        search_paths.append(config_path)

    # 环境变量（Electron 生产模式下必传，优先级最高）
    env_path = os.environ.get("CONFIG_PATH")
    if env_path:
        search_paths.append(env_path)

    # PyInstaller 打包后: 相对于 exe 所在目录的 ../config/config.yaml
    # 适用于独立运行 cpq-backend.exe 的场景
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        search_paths.append(os.path.join(exe_dir, '..', 'config', 'config.yaml'))

    # 相对于当前文件所在目录的 ../config/config.yaml（开发模式）
    this_dir = os.path.dirname(os.path.abspath(__file__))
    search_paths.append(os.path.join(this_dir, "..", "config", "config.yaml"))

    for path in search_paths:
        abspath = os.path.abspath(path)
        if os.path.exists(abspath):
            try:
                with open(abspath, "r", encoding="utf-8") as f:
                    raw = yaml.safe_load(f)
                if raw is None:
                    raw = {}
                return Config.from_dict(raw)
            except Exception as e:
                print(f"[config] WARN: failed to load {abspath}: {e}")
                continue

    print("[config] no config file found, using defaults")
    return Config()
