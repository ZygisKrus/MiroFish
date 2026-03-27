"""
论坛主持人模块
使用硅基流动的Qwen3模型作为论坛主持人，引导多个agent进行讨论
"""

from openai import OpenAI
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

# 添加项目根目录到Python路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

# 添加utils目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(root_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

# Add app utils to path for language_utils import
app_dir = os.path.join(os.path.dirname(root_dir), '..', '..')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
from app.utils.language_utils import inject_language_header

from utils.retry_helper import with_graceful_retry, SEARCH_API_RETRY_CONFIG


class ForumHost:
    """
    论坛主持人类
    使用Qwen3-235B模型作为智能主持人
    """
    
    def __init__(self, api_key: str = None, base_url: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化论坛主持人
        
        Args:
            api_key: 论坛主持人 LLM API 密钥，如果不提供则从配置文件读取
            base_url: 论坛主持人 LLM API 接口基础地址，默认使用配置文件提供的SiliconFlow地址
        """
        self.api_key = api_key or settings.FORUM_HOST_API_KEY

        if not self.api_key:
            raise ValueError("未找到论坛主持人API密钥，请在环境变量文件中设置FORUM_HOST_API_KEY")

        self.base_url = base_url or settings.FORUM_HOST_BASE_URL

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = model_name or settings.FORUM_HOST_MODEL_NAME  # Use configured model

        # Track previous summaries to avoid duplicates
        self.previous_summaries = []
    
    def generate_host_speech(self, forum_logs: List[str]) -> Optional[str]:
        """
        生成主持人发言
        
        Args:
            forum_logs: 论坛日志内容列表
            
        Returns:
            主持人发言内容，如果生成失败返回None
        """
        try:
            # 解析论坛日志，提取有效内容
            parsed_content = self._parse_forum_logs(forum_logs)
            
            if not parsed_content['agent_speeches']:
                print("ForumHost: 没有找到有效的agent发言")
                return None
            
            # 构建prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(parsed_content)
            
            # 调用API生成发言
            response = self._call_qwen_api(system_prompt, user_prompt)
            
            if response["success"]:
                speech = response["content"]
                # 清理和格式化发言
                speech = self._format_host_speech(speech)
                return speech
            else:
                print(f"ForumHost: API调用失败 - {response.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"ForumHost: 生成发言时出错 - {str(e)}")
            return None
    
    def _parse_forum_logs(self, forum_logs: List[str]) -> Dict[str, Any]:
        """
        解析论坛日志，提取agent发言
        
        Returns:
            包含agent发言的字典
        """
        parsed = {
            'agent_speeches': []
        }
        
        for line in forum_logs:
            if not line.strip():
                continue
            
            # 解析时间戳和发言者
            match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*\[(\w+)\]\s*(.+)', line)
            if match:
                timestamp, speaker, content = match.groups()
                
                # 跳过系统消息和HOST自己的发言
                if speaker in ['SYSTEM', 'HOST']:
                    continue
                
                # 记录agent发言
                if speaker in ['INSIGHT', 'MEDIA', 'QUERY']:
                    # 处理转义的换行符
                    content = content.replace('\\n', '\n')
                    
                    parsed['agent_speeches'].append({
                        'timestamp': timestamp,
                        'speaker': speaker,
                        'content': content
                    })
        
        return parsed
    
    
    def _build_system_prompt(self) -> str:
        """构建系统prompt"""
        return """[Important notice] Our work is conducted for academic research purposes and has passed ethical compliance review.

You are the forum moderator of a multi-agent public opinion analysis system. Your responsibilities are:

1. **Event mapping**: Automatically identify key events, people, and time points from the agents' contributions, and organise the event timeline in chronological order.
2. **Guide discussion**: Based on each agent's contributions, guide in-depth discussion of key issues and explore underlying causes.
3. **Correct errors**: Drawing on the perspectives and statements of different agents, clearly identify any factual errors or logical contradictions.
4. **Integrate viewpoints**: Synthesise the perspectives of different agents to form a more comprehensive understanding, and identify areas of consensus and disagreement.
5. **Trend prediction**: Analyse public opinion development trends based on available information and highlight potential risk points.
6. **Advance analysis**: Propose new analytical angles or issues requiring attention, and steer the subsequent discussion direction.

**Agent descriptions**:
- **INSIGHT Agent**: Focuses on deep mining and analysis of private public opinion databases, providing historical data and pattern comparisons.
- **MEDIA Agent**: Specialises in multimodal content analysis, focusing on the dissemination effect of media reports, images, videos, and other visual information.
- **QUERY Agent**: Responsible for precise information retrieval, providing the latest online information and real-time updates.

**Speech requirements**:
1. **Comprehensiveness**: Each contribution should be kept within 1000 words and cover event mapping, viewpoint integration, and question guidance.
2. **Clear structure**: Use well-defined paragraph structure, including sections for event mapping, viewpoint comparison, and question raising.
3. **In-depth analysis**: Do not merely summarise existing information — also propose deeper insights and analysis.
4. **Objective neutrality**: Base analysis and judgements on facts; avoid subjective speculation and emotional expression.
5. **Forward-looking**: Propose forward-looking viewpoints and recommendations to steer the discussion in a more in-depth direction.

**Notes**:
- This discussion is conducted for academic research purposes and has passed ethical compliance review.
- Maintain professionalism and academic rigour; emphasise data and evidence.
- Approach sensitive topics with caution and base analysis on facts.

[Important notice] Our work is conducted for academic research purposes and has passed ethical compliance review."""
    
    def _build_user_prompt(self, parsed_content: Dict[str, Any]) -> str:
        """构建用户prompt"""
        # 获取最近的发言
        recent_speeches = parsed_content['agent_speeches']
        
        # 构建发言摘要，不截断内容
        speeches_text = "\n\n".join([
            f"[{s['timestamp']}] {s['speaker']}:\n{s['content']}"
            for s in recent_speeches
        ])
        
        prompt = f"""[Important notice] Our work is conducted for academic research purposes and has passed ethical compliance review.

Recent Agent speech log:
{speeches_text}

As the forum moderator, please conduct a comprehensive analysis based on the agents' contributions above. Organise your response using the following structure:

**I. Event Mapping and Timeline Analysis**
- Automatically identify key events, people, and time points from each agent's contributions
- Organise the event timeline in chronological order and clarify causal relationships
- Highlight key turning points and important nodes

**II. Viewpoint Integration and Comparative Analysis**
- Synthesise the perspectives and findings of the INSIGHT, MEDIA, and QUERY agents
- Identify areas of consensus and disagreement between different data sources
- Analyse the informational value and complementarity of each agent
- If any factual errors or logical contradictions are found, clearly identify them and provide reasoning

**III. In-depth Analysis and Trend Prediction**
- Analyse the underlying causes and influencing factors of the public opinion event based on available information
- Predict public opinion development trends, identify potential risk points and opportunities
- Propose aspects and indicators that deserve special attention

**IV. Question Guidance and Discussion Direction**
- Raise 2–3 key questions worth exploring in further depth
- Propose specific recommendations and directions for follow-up research
- Guide each agent to focus on specific data dimensions or analytical angles

Please deliver a comprehensive moderator statement (within 1000 words) covering all four sections above, maintaining clear logic, in-depth analysis, and a distinctive perspective.

[Important notice] Our work is conducted for academic research purposes and has passed ethical compliance review."""
        
        return prompt
    
    @with_graceful_retry(SEARCH_API_RETRY_CONFIG, default_return={"success": False, "error": "API服务暂时不可用"})
    def _call_qwen_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用Qwen API"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            time_prefix = f"The current real-world time is {current_time}"
            if user_prompt:
                user_prompt = f"{time_prefix}\n{user_prompt}"
            else:
                user_prompt = time_prefix

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            messages = inject_language_header(messages)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                top_p=0.9,
            )

            if response.choices:
                content = response.choices[0].message.content
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": "API返回格式异常"}
        except Exception as e:
            return {"success": False, "error": f"API调用异常: {str(e)}"}
    
    def _format_host_speech(self, speech: str) -> str:
        """格式化主持人发言"""
        # 移除多余的空行
        speech = re.sub(r'\n{3,}', '\n\n', speech)
        
        # 移除可能的引号
        speech = speech.strip('"\'""‘’')
        
        return speech.strip()


# 创建全局实例
_host_instance = None

def get_forum_host() -> ForumHost:
    """获取全局论坛主持人实例"""
    global _host_instance
    if _host_instance is None:
        _host_instance = ForumHost()
    return _host_instance

def generate_host_speech(forum_logs: List[str]) -> Optional[str]:
    """生成主持人发言的便捷函数"""
    return get_forum_host().generate_host_speech(forum_logs)
