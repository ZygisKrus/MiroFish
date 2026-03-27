"""
本体生成服务
接口1：分析文本内容，生成适合社会模拟的实体和关系类型定义
"""

import json
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


# System prompt for ontology generation
ONTOLOGY_SYSTEM_PROMPT = """You are a professional knowledge graph ontology design expert. Your task is to analyse the given text content and simulation requirements, and design entity types and relationship types suitable for **social media opinion simulation**.

**Important: You must output valid JSON format data only. Do not output anything else.**

## Core Task Background

We are building a **social media opinion simulation system**. In this system:
- Every entity is an "account" or "actor" that can post, interact, and spread information on social media
- Entities influence each other, repost, comment, and respond
- We need to simulate the reactions of all parties in opinion events and the paths of information propagation

Therefore, **entities must be real-world actors that can speak and interact on social media**:

**Can be**:
- Specific individuals (public figures, involved parties, opinion leaders, experts, academics, ordinary people)
- Companies and businesses (including their official accounts)
- Organisations (universities, associations, NGOs, trade unions, etc.)
- Government departments and regulatory bodies
- Media organisations (newspapers, TV stations, self-media, websites)
- Social media platforms themselves
- Representatives of specific groups (e.g. alumni associations, fan clubs, rights advocacy groups)

**Cannot be**:
- Abstract concepts (e.g. "public opinion", "sentiment", "trends")
- Topics/themes (e.g. "academic integrity", "education reform")
- Viewpoints/stances (e.g. "supporters", "opponents")

## Output Format

Output JSON format with the following structure:

```json
{
    "entity_types": [
        {
            "name": "Entity type name (English, PascalCase)",
            "description": "Short description (English, max 100 characters)",
            "attributes": [
                {
                    "name": "attribute name (English, snake_case)",
                    "type": "text",
                    "description": "attribute description"
                }
            ],
            "examples": ["Example entity 1", "Example entity 2"]
        }
    ],
    "edge_types": [
        {
            "name": "Relationship type name (English, UPPER_SNAKE_CASE)",
            "description": "Short description (English, max 100 characters)",
            "source_targets": [
                {"source": "Source entity type", "target": "Target entity type"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis summary of the text and entity design rationale"
}
```

## Design Guidelines (Extremely Important!)

### 1. Entity Type Design — Must Be Strictly Followed

**Quantity requirement: Must output exactly 10 entity types**

**Hierarchical structure requirement (must include both specific types and fallback types)**:

Your 10 entity types must include the following levels:

A. **Fallback types (required, placed as the last 2 in the list)**:
   - `Person`: The fallback type for any individual person. When a person does not fit any other more specific person type, they belong here.
   - `Organization`: The fallback type for any organisation. When an organisation does not fit any other more specific organisation type, it belongs here.

B. **Specific types (8 types, designed based on the text content)**:
   - Design more specific types for the main roles appearing in the text
   - For example: if the text involves academic events, you might have `Student`, `Professor`, `University`
   - For example: if the text involves business events, you might have `Company`, `CEO`, `Employee`

**Why fallback types are needed**:
- The text will contain various characters, such as "primary school teachers", "passersby", "anonymous netizens"
- If there is no specific type to match them, they should be placed in `Person`
- Similarly, small organisations, temporary groups, etc. should go into `Organization`

**Principles for designing specific types**:
- Identify the most frequently appearing or key role types in the text
- Each specific type should have clear boundaries and avoid overlap
- The description must clearly explain how this type differs from the fallback type

### 2. Relationship Type Design

- Quantity: 6–10 types
- Relationships should reflect real connections in social media interactions
- Ensure the source_targets of relationships cover the entity types you have defined

### 3. Attribute Design

- 1–3 key attributes per entity type
- **Note**: Attribute names must NOT use `name`, `uuid`, `group_id`, `created_at`, `summary` (these are system-reserved words)
- Recommended: `full_name`, `title`, `role`, `position`, `location`, `description`, etc.

## Entity Type Reference

**Individual types (specific)**:
- Student: University student
- Professor: Professor/academic
- Journalist: Reporter
- Celebrity: Public figure / influencer
- Executive: Corporate executive
- Official: Government official

**Individual types (fallback)**:
- Person: Any individual (when no specific type matches)

**Organization types (specific)**:
- University: Higher education institution
- Company: Business / startup
- GovernmentAgency: Government body
- MediaOutlet: Media organization
- NGO: Non-governmental organization

**Organization types (fallback)**:
- Organization: Any organization (when no specific type matches)

**Location/Social types (for student simulation)**:
- DormFloor: A specific floor in a student dormitory (e.g., Kamciatka Floor 3)
- StudyGroup: A group of students who study together regularly
- LectureCohort: All students sharing a lecture course in a given year
- SocialCircle: Cross-year social group (bar regulars, sports teams, event organizers)

**Product/Marketing types**:
- MarketingChannel: A channel for reaching students (Instagram, stickers, ambassadors)
- DesignVariant: A specific UI/design version of the product being tested
- ProductFeature: A specific feature of the product (AI assistant, notes, quizzes)

## Relationship Type Reference

- WORKS_FOR: Employed by
- STUDIES_AT: Enrolled at
- AFFILIATED_WITH: Affiliated with
- REPRESENTS: Represents
- REGULATES: Regulates
- REPORTS_ON: Reports on
- COMMENTS_ON: Comments on
- RESPONDS_TO: Responds to
- SUPPORTS: Supports
- OPPOSES: Opposes
- COLLABORATES_WITH: Collaborates with
- COMPETES_WITH: Competes with
- ROOMMATE_OF: Lives on the same dorm floor (daily contact, high influence)
- STUDIES_WITH: Part of the same study group (weekly contact, academic influence)
- INFLUENCED_BY: Social influence relationship (trust-weighted)
- SAW_AD_ON: Was exposed to marketing on a specific channel
- SHARES_ACCOUNT_WITH: Shares a product account (economic relationship)
- MEMBER_OF: Member of a social circle or study group
- RECOMMENDED_TO: Recommended the product to another person

## Event Type Reference (for simulation tracking)

- TRIAL_STARTED: Student started a free trial
- TRIAL_EXPIRED: Free trial period ended
- CONVERTED: Student became a paying customer
- CHURNED: Student cancelled their subscription
- SHARED_ACCOUNT: Student joined an account-sharing group
- RECOMMENDED_TO: Student recommended the product to peers
- AD_EXPOSED: Student was exposed to marketing material
- VISITED_WEBSITE: Student visited the product website
"""


class OntologyGenerator:
    """
    本体生成器
    分析文本内容，生成实体和关系类型定义
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        from ..config import Config
        self.llm_client = llm_client or LLMClient(model=Config.LLM_REASONING_MODEL)
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成本体定义
        
        Args:
            document_texts: 文档文本列表
            simulation_requirement: 模拟需求描述
            additional_context: 额外上下文
            
        Returns:
            本体定义（entity_types, edge_types等）
        """
        # 构建用户消息
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # 调用LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
            timeout=120.0
        )
        
        # 验证和后处理
        result = self._validate_and_process(result)
        
        return result
    
    # 传给 LLM 的文本最大长度（5万字）
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """构建用户消息"""
        
        # 合并文本
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # 如果文本超过5万字，截断（仅影响传给LLM的内容，不影响图谱构建）
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...(Original text was {original_length} characters; first {self.MAX_TEXT_LENGTH_FOR_LLM} characters extracted for ontology analysis)..."
        
        message = f"""## Simulation Requirements

{simulation_requirement}

## Document Content

{combined_text}
"""

        if additional_context:
            message += f"""
## Additional Notes

{additional_context}
"""

        message += """
Based on the above content, design entity types and relationship types suitable for social opinion simulation.

**Rules that must be followed**:
1. Must output exactly 10 entity types
2. The last 2 must be the fallback types: Person (individual fallback) and Organization (organisation fallback)
3. The first 8 are specific types designed based on the text content
4. All entity types must be real-world actors that can speak out — they cannot be abstract concepts
5. Attribute names must not use reserved words such as name, uuid, group_id — use full_name, org_name, etc. instead
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证和后处理结果"""
        
        # 确保必要字段存在
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # 验证实体类型
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # 确保description不超过100字符
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # 验证关系类型
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API 限制：最多 10 个自定义实体类型，最多 10 个自定义边类型
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10
        
        # 兜底类型定义
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # 检查是否已有兜底类型
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # 需要添加的兜底类型
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # 如果添加后会超过 10 个，需要移除一些现有类型
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # 计算需要移除多少个
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # 从末尾移除（保留前面更重要的具体类型）
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # 添加兜底类型
            result["entity_types"].extend(fallbacks_to_add)
        
        # 最终确保不超过限制（防御性编程）
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        将本体定义转换为Python代码（类似ontology.py）
        
        Args:
            ontology: 本体定义
            
        Returns:
            Python代码字符串
        """
        code_lines = [
            '"""',
            '自定义实体类型定义',
            '由MiroFish自动生成，用于社会舆论模拟',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== 实体类型定义 ==============',
            '',
        ]
        
        # 生成实体类型
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== 关系类型定义 ==============')
        code_lines.append('')
        
        # 生成关系类型
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # 转换为PascalCase类名
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # 生成类型字典
        code_lines.append('# ============== 类型配置 ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # 生成边的source_targets映射
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)

