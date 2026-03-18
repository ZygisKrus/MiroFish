"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

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
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            
        Returns:
            模型响应文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON，带自动重试机制
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: JSON解析失败时的最大重试次数
            
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
                    response_format={"type": "json_object"}
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
            except Exception as e:
                last_error = e
                print(f"[LLM Client] API Error on attempt {attempt + 1}: {e}")
                time.sleep(2)
                
        raise ValueError(f"LLM在 {max_retries} 次尝试后仍未返回有效的JSON格式。最后一次错误: {last_error}")

