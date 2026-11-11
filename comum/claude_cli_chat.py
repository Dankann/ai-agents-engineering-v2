"""ChatClaudeCLI: um chat model do LangChain que chama o `claude -p` (Claude Code em modo não interativo).

Serve para rodar os notebooks pela assinatura do Claude quando não há crédito de API. O modelo não recebe
ferramentas nativas: os schemas vão no prompt de sistema e o modelo responde só com um JSON

    {"texto": "...", "chamadas": [{"nome": "...", "args": {...}}]}

que vira um AIMessage com tool_calls. Por isso funciona com bind_tools, create_agent e ToolStrategy.

Uso:
    from comum.claude_cli_chat import ChatClaudeCLI
    modelo = ChatClaudeCLI()                       # claude-haiku-4-5-20251001
    modelo = ChatClaudeCLI(model="claude-sonnet-4-5")
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from typing import Any, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

# Tokens que o próprio Claude Code acrescenta a cada chamada, mesmo com todo o contexto cortado
# (medido com prompt de sistema "x" e pergunta "x", sem raciocínio: 637 a 639 tokens de entrada).
BASELINE_TOKENS = 636

# Cada flag tira um pedaço do contexto do Claude Code: CLAUDE.md, memória, plugins, skills, hooks,
# servidores MCP e ferramentas embutidas. Sem elas, uma chamada trivial passa de 190 mil tokens.
FLAGS_SEM_CONTEXTO = [
    "--setting-sources", "",
    "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
    "--disable-slash-commands",
    "--no-session-persistence",
    "--max-turns", "1",
    "--tools", "",
]

# O Claude Code liga o raciocínio estendido por padrão: triplica os tokens de saída e não existe no gpt-4o-mini.
ENV_SEM_RACIOCINIO = {"MAX_THINKING_TOKENS": "0"}

INSTRUCOES_DE_FERRAMENTAS = """

# Ferramentas

Você pode chamar as ferramentas abaixo. Cada uma vem com nome, descrição e o JSON Schema dos argumentos.

{ferramentas}

# Formato da sua resposta

Responda SEMPRE e SOMENTE com um objeto JSON, sem texto antes ou depois e sem bloco de código:

{{"texto": "o que você quer dizer, ou vazio", "chamadas": [{{"nome": "nome_da_ferramenta", "args": {{...}}}}]}}

- Para chamar ferramentas, liste-as em "chamadas", com argumentos que obedeçam ao schema. Os resultados voltam na próxima mensagem.
- Para responder sem ferramenta, deixe "chamadas" vazia.
{obrigatorio}"""


def _caminho_do_claude() -> str:
    caminho = shutil.which("claude") or os.path.expanduser(r"~\.local\bin\claude.exe")
    if not os.path.exists(caminho):
        raise RuntimeError("Não encontrei o executável claude no PATH nem em ~/.local/bin.")
    return caminho


def _texto(conteudo: Any) -> str:
    if isinstance(conteudo, str):
        return conteudo
    partes = []
    for bloco in conteudo or []:
        if isinstance(bloco, str):
            partes.append(bloco)
        elif isinstance(bloco, dict) and bloco.get("type") == "text":
            partes.append(bloco.get("text", ""))
    return "\n".join(partes)


def _transcricao(mensagens: Sequence[BaseMessage]) -> tuple[str, str]:
    """Separa o prompt de sistema e escreve o resto da conversa como texto corrido."""
    sistema, blocos = [], []
    for m in mensagens:
        if isinstance(m, SystemMessage):
            sistema.append(_texto(m.content))
        elif isinstance(m, HumanMessage):
            blocos.append(f"[usuário]\n{_texto(m.content)}")
        elif isinstance(m, AIMessage):
            texto = _texto(m.content).strip()
            if m.tool_calls:
                chamadas = [{"nome": c["name"], "args": c["args"], "id": c.get("id")} for c in m.tool_calls]
                blocos.append("[assistente]\n" + json.dumps({"texto": texto, "chamadas": chamadas}, ensure_ascii=False))
            else:
                blocos.append(f"[assistente]\n{texto}")
        elif isinstance(m, ToolMessage):
            blocos.append(f"[resultado da ferramenta {m.name or ''} · id {m.tool_call_id}]\n{_texto(m.content)}")
        else:
            blocos.append(f"[{m.type}]\n{_texto(m.content)}")
    return "\n\n".join(sistema), "\n\n".join(blocos)


def _extrair_json(texto: str) -> dict | None:
    """O primeiro objeto JSON com "chamadas" ou "texto", tolerando bloco de código e texto em volta."""
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())
    decodificador = json.JSONDecoder()
    for m in re.finditer(r"\{", texto):
        try:
            obj, _ = decodificador.raw_decode(texto, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("chamadas" in obj or "texto" in obj):
            return obj
    return None


class ChatClaudeCLI(BaseChatModel):
    """Chat model que roda cada chamada como `claude -p --output-format json`."""

    model: str = "claude-haiku-4-5-20251001"
    timeout: int = 180
    baseline_tokens: int = BASELINE_TOKENS

    @property
    def _llm_type(self) -> str:
        return "claude-cli"

    @property
    def _identifying_params(self) -> dict:
        return {"model": self.model}

    def bind_tools(self, tools: Sequence[Any], *, tool_choice: Any = None, **kwargs: Any):
        return self.bind(tools=[convert_to_openai_tool(t) for t in tools], tool_choice=tool_choice, **kwargs)

    def _generate(self, messages: list[BaseMessage], stop: list[str] | None = None,
                  run_manager: CallbackManagerForLLMRun | None = None, tools: list[dict] | None = None,
                  tool_choice: Any = None, **kwargs: Any) -> ChatResult:
        sistema, conversa = _transcricao(messages)
        if tools:
            sistema += self._instrucoes(tools, tool_choice)
        resultado = self._chamar_cli(sistema, conversa)
        texto = resultado.get("result") or ""
        uso = self._uso(resultado)

        mensagem = self._mensagem(texto, tools) if tools else AIMessage(content=texto)
        if tools and self._exige_chamada(tool_choice) and not mensagem.tool_calls:
            nomes = ", ".join(t["function"]["name"] for t in tools)
            lembrete = (f"\n\n[assistente]\n{texto}\n\n[sistema]\nResposta recusada: ela não chamou nenhuma ferramenta, e "
                        f"aqui toda resposta precisa chamar pelo menos uma ({nomes}). Se o que você quer é falar com o "
                        "usuário, ponha esse conteúdo na ferramenta de resposta final. Responda só com o JSON "
                        "{\"texto\": ..., \"chamadas\": [...]}.")
            resultado = self._chamar_cli(sistema, conversa + lembrete)
            uso = {k: uso[k] + v for k, v in self._uso(resultado).items()}
            mensagem = self._mensagem(resultado.get("result") or "", tools)

        mensagem.usage_metadata = uso
        mensagem.response_metadata = {"model_name": self.model, "duration_api_ms": resultado.get("duration_api_ms"),
                                      "total_cost_usd": resultado.get("total_cost_usd")}
        return ChatResult(generations=[ChatGeneration(message=mensagem)])

    @staticmethod
    def _exige_chamada(tool_choice: Any) -> bool:
        return tool_choice not in (None, "auto", "none", False)

    def _instrucoes(self, tools: list[dict], tool_choice: Any) -> str:
        descritas = [{"nome": t["function"]["name"], "descricao": t["function"].get("description", ""),
                      "parametros": t["function"].get("parameters", {})} for t in tools]
        if isinstance(tool_choice, dict):
            tool_choice = tool_choice.get("function", {}).get("name") or tool_choice.get("name")
        if tool_choice in ("any", "required", True):
            obrigatorio = ("- Nesta resposta, \"chamadas\" precisa ter pelo menos uma ferramenta. Não existe resposta só em "
                           "texto: para falar com o usuário (responder, pedir um dado que falta ou encerrar), chame a "
                           "ferramenta de resposta final da lista.")
        elif isinstance(tool_choice, str) and tool_choice not in ("auto", "none"):
            obrigatorio = f"- Nesta resposta, \"chamadas\" precisa conter a ferramenta {tool_choice}."
        else:
            obrigatorio = ""
        return INSTRUCOES_DE_FERRAMENTAS.format(
            ferramentas=json.dumps(descritas, ensure_ascii=False, indent=1), obrigatorio=obrigatorio)

    @staticmethod
    def _mensagem(texto: str, tools: list[dict]) -> AIMessage:
        obj = _extrair_json(texto)
        if obj is None:
            return AIMessage(content=texto)
        chamadas = []
        for c in obj.get("chamadas") or []:
            if not isinstance(c, dict) or not (c.get("nome") or c.get("name")):
                continue
            args = c.get("args", c.get("arguments", {}))
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            chamadas.append({"name": c.get("nome") or c.get("name"), "args": args if isinstance(args, dict) else {},
                             "id": f"call_{uuid.uuid4().hex[:24]}", "type": "tool_call"})
        return AIMessage(content=str(obj.get("texto") or ""), tool_calls=chamadas)

    def _uso(self, resultado: dict) -> dict:
        u = resultado.get("usage") or {}
        bruto = (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                 + u.get("cache_read_input_tokens", 0))
        entrada = max(0, bruto - self.baseline_tokens)
        saida = u.get("output_tokens", 0)
        return {"input_tokens": entrada, "output_tokens": saida, "total_tokens": entrada + saida}

    def _chamar_cli(self, sistema: str, conversa: str) -> dict:
        with tempfile.TemporaryDirectory(prefix="claude-cli-") as pasta:
            arquivo = os.path.join(pasta, "sistema.txt")
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(sistema or "Você é um assistente prestativo.")
            comando = [_caminho_do_claude(), "-p", "--output-format", "json", "--model", self.model,
                       "--system-prompt-file", arquivo, *FLAGS_SEM_CONTEXTO]
            try:
                p = subprocess.run(comando, input=conversa, capture_output=True, text=True, encoding="utf-8",
                                   cwd=pasta, timeout=self.timeout, env={**os.environ, **ENV_SEM_RACIOCINIO})
            except subprocess.TimeoutExpired as e:
                raise RuntimeError(f"claude -p não respondeu em {self.timeout} s") from e
        try:
            resultado = json.loads(p.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"claude -p falhou (código {p.returncode}): {(p.stderr or p.stdout).strip()[:500]}")
        if p.returncode != 0 or resultado.get("is_error"):
            raise RuntimeError(f"claude -p devolveu erro: {str(resultado.get('result') or p.stderr)[:500]}")
        return resultado
