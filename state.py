from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from langgraph.channels import LastValue
from typing_extensions import Annotated
from schema import ResumeSchema, SonarRecommendations, ResumeImprovement, ProjectImprovement, GeneralRecommendation

class AgentState(BaseModel):
    """State for the resume processing workflow with 3 agents"""

    original_resume_text: Optional[str] = Field(
        default=None,
        description="The original raw resume text input"
    )

    target_industry: Optional[str] = Field(
        default=None,
        description="Target industry for resume optimization (e.g., 'finance', 'tech')"
    )

    tone_guidance: Optional[str] = Field(
        default="professional",
        description="Tone guidance for rewriting (e.g., 'professional', 'concise', 'ambitious')"
    )
    # Agent 1: Restructuring Agent outputs
    structured_resume: Optional[ResumeSchema] = Field(
        default=None,
        description="Structured resume data from restructuring_agent"
    )
    restructuring_status: Optional[str] = Field(
        default=None,
        description="Status of restructuring process ('pending', 'completed', 'error')"
    )
    restructuring_errors: Optional[List[str]] = Field(
        default_factory=list,
        description="Any errors encountered during restructuring"
    )

    # Agent 2: Recommendation Agent outputs
    industry_recommendations: Optional[SonarRecommendations] = Field(
        default=None,
        description="Industry-specific recommendations from recommendation_agent"
    )

    recommendation_status: Optional[str] = Field(
        default=None,
        description="Status of recommendation process ('pending', 'completed', 'error')"
    )

    recommendation_errors: Optional[List[str]] = Field(
        default_factory=list,
        description="Any errors encountered during recommendation generation"
    )

    # Agent 3: Rewriting Agent outputs
    rewritten_resume: Optional[ResumeSchema] = Field(
        default=None,
        description="Final rewritten resume from rewriting_agent"
    )


    # ChromaDB integration
    similar_documents: Optional[List[str]] = Field(
        default_factory=list,
        description="Most similar documents retrieved from ChromaDB"
    )

    dissimilar_documents: Optional[List[str]] = Field(
        default_factory=list,
        description="Least similar documents retrieved from ChromaDB"
    )



    # Workflow metadata
    workflow_status: Optional[str] = Field(
        default="initialized",
        description="Overall workflow status ('initialized', 'running', 'completed', 'error')"
    )

    current_agent: Optional[str] = Field(
        default=None,
        description="Currently executing agent ('restructuring', 'recommendation', 'rewriting')"
    )

    execution_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata about execution (timestamps, versions, etc.)"
    )

    # Final output
    resume_improvements: Optional[List[ResumeImprovement]] = Field(
        default_factory=list,
        description="Specific improvements for resume sections"
    )

    project_improvements: Optional[List[ProjectImprovement]] = Field(
        default_factory=list,
        description="Recommendations for improving project descriptions and presentation"
    )

    general_recommendations: Optional[List[GeneralRecommendation]] = Field(
        default_factory=list,
        description="General career and professional development recommendations"
    )

    overall_priority_score: Optional[int] = Field(
        default=None,
        description="Overall priority score from 1-10 indicating how urgently improvements are needed",
        ge=1,
        le=10
    )

    estimated_implementation_time: Optional[str] = Field(
        default=None,
        description="Estimated time to implement all recommendations (e.g., '2-4 weeks', '1-2 months')"
    )

    success_metrics: Optional[List[str]] = Field(
        default_factory=list,
        description="How to measure the success of implementing these recommendations"
    )

    final_resume_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Final resume as JSON dictionary for easy consumption"
    )
    project_recommendation: Optional[Dict[str,Any]] = Field(
        default = None,
        description = "Project recommendations the user can make based on its profile"
    )


    processing_summary: Optional[str] = Field(
        default=None,
        description="Summary of the entire processing workflow"
    )

    # Error handling
    global_errors: Optional[List[str]] = Field(
        default_factory=list,
        description="Global errors that affect the entire workflow"
    )

    # Annotations for LangGraph channels
    agent_description: Annotated[Any, LastValue] = Field(
        default=None,
        description="Latest agent description or status update"
    )

    prompt: Annotated[str, LastValue] = Field(
        default=None,
        description="Latest prompt used by any agent"
    )

    summary: Annotated[Any, LastValue] = Field(
        default=None,
        description="A detailed summary outlining a plan"
    )