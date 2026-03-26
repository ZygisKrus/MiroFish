"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
import time
from typing import Optional, Dict, Any, List
from openai import OpenAI, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, retry_if_not_exception_type

from ..config import Config


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_not_exception_type(RateLimitError),  # Don't burn RPM quota on 429s
        reraise=True
    )
    def _create_completion_with_retry(self, **kwargs):
        """带有指数退避重试的底层调用"""
        return self.client.chat.completions.create(**kwargs)

    @staticmethod
    def _inject_language(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Prepend output-language instruction to the system message.

        All system prompts in this codebase are written in Chinese (original
        project language). When OUTPUT_LANGUAGE != 'Chinese' we prepend a
        short English override header so the model responds in the correct
        language for non-Chinese simulation contexts.
        """
        lang = Config.OUTPUT_LANGUAGE or "English"
        if lang.strip().lower() == "chinese":
            return messages  # Original Chinese behaviour — no injection needed
        header = (
            f"IMPORTANT: You must respond entirely in {lang}. "
            f"All text, field values, summaries, and analysis must be written in {lang}. "
            f"Do not use Chinese or any other language.\n\n"
        )
        result = []
        for msg in messages:
            if msg.get("role") == "system":
                result.append({**msg, "content": header + msg["content"]})
            else:
                result.append(msg)
        return result

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        timeout: float = 120.0
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            timeout: 超时时间（秒）
            
        Returns:
            模型响应文本
        """
        messages = self._inject_language(messages)
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        # 使用带有重试机制的调用，防止 OpenRouter 429 Rate Limit
        response = self._create_completion_with_retry(**kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        max_retries: int = 3,
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON，带自动重试机制
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: JSON解析失败时的最大重试次数
            timeout: 超时时间（秒）
            
        Returns:
            解析后的JSON对象
        """
        import time
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                    timeout=timeout
                )
                # 清理markdown代码块标记
                cleaned_response = response.strip()
                cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
                cleaned_response = cleaned_response.strip()

                return json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                last_error = e
                print(f"[LLM Client] JSON Decode Error on attempt {attempt + 1}: {e}")
                # 稍微调整温度以获得不同的输出
                temperature = min(1.0, temperature + 0.1)
                time.sleep(1)
            except RateLimitError as e:
                last_error = e
                # Parse suggested retry delay from error message if available (e.g. Google: "retry in 11.5s")
                import re as _re
                _delay_match = _re.search(r'retry in (\d+\.?\d*)s', str(e), _re.IGNORECASE)
                _wait = float(_delay_match.group(1)) + 3 if _delay_match else 30
                print(f"[LLM Client] Rate limit (429) on attempt {attempt + 1}, waiting {_wait:.0f}s for reset...")
                time.sleep(_wait)
            except Exception as e:
                last_error = e
                print(f"[LLM Client] API Error on attempt {attempt + 1}: {e}")
                time.sleep(2)
                
        raise ValueError(f"LLM在 {max_retries} 次尝试后仍未返回有效的JSON格式。最后一次错误: {last_error}")

