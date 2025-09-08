from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Sonar Recommendation Schemas
class SkillRecommendation(BaseModel):
    """Schema for recommended skills"""
    skill_name: str
    reason: str
    priority: str = Field(description="High/Medium/Low priority for learning this skill")
    resources: Optional[List[str]] = Field(default_factory=list, description="Optional resources for learning this skill")

class IndustryTrend(BaseModel):
    """Schema for current industry trends"""
    trend_name: str
    description: str
    impact: str = Field(description="How this trend impacts the industry")
    related_skills: List[str] = Field(default_factory=list)

class SonarRecommendations(BaseModel):
    """Schema for Sonar's industry recommendations"""
    industry: str = Field(description="The industry being analyzed")
    skills_to_add: List[SkillRecommendation] = Field(
        default_factory=list,
        description="List of recommended skills to add to resume"
    )
    current_trends: List[IndustryTrend] = Field(
        default_factory=list,
        description="Current industry trends and their implications"
    )
    last_updated: str = Field(
        description="When these recommendations were last updated"
    )

# Resume Recommendation Agent Schemas
class ResumeImprovement(BaseModel):
    """Schema for specific resume improvement recommendations"""
    section: str = Field(description="Resume section to improve (e.g., 'Experience', 'Skills', 'Summary')")
    current_issue: str = Field(description="Comprehensive analysis of what's currently problematic or missing, including specific examples, impact assessment, and root cause analysis. Provide detailed context and supporting evidence.")
    recommended_change: str = Field(description="Extremely detailed specific change or addition recommended, including exact wording suggestions, implementation steps, rationale, expected outcomes, and success metrics. Provide comprehensive guidance with examples and best practices.")
    priority: str = Field(description="Detailed priority assessment (High/Medium/Low) with comprehensive justification, including market analysis, competitive positioning, timeline considerations, and strategic importance.")
    expected_impact: str = Field(description="Extensive analysis of expected benefit of making this change, including quantitative metrics, qualitative improvements, competitive advantages, and long-term career impact. Provide detailed success scenarios and measurement frameworks.")

class ProjectImprovement(BaseModel):
    """Schema for project-specific improvement recommendations"""
    project_name: str = Field(description="Name of the project to improve")
    current_description: str = Field(description="Comprehensive analysis of current project description including strengths, weaknesses, gaps, and improvement opportunities. Provide detailed assessment with specific examples.")
    improvement_suggestion: str = Field(description="Extremely detailed improvement recommendation with specific wording changes, structural enhancements, impact quantification methods, and competitive positioning strategies. Include implementation steps and success metrics.")
    technologies_to_highlight: List[str] = Field(default_factory=list, description="Detailed analysis of technology stack elements to emphasize, including rationale for each technology, market relevance, competitive advantages, and implementation impact.")
    metrics_to_add: List[str] = Field(default_factory=list, description="Comprehensive quantifiable results or metrics to include, with detailed measurement methodologies, benchmarking strategies, and success criteria.")
    priority: str = Field(description="Detailed priority assessment with comprehensive analysis of strategic importance, market impact, implementation complexity, and competitive positioning.")

class GeneralRecommendation(BaseModel):
    """Schema for general career/resume recommendations"""
    category: str = Field(description="Specific category of recommendation (e.g., 'Networking', 'Certifications', 'Personal Branding') with detailed context and market relevance.")
    recommendation: str = Field(description="Extremely detailed actionable recommendation with step-by-step implementation plan, specific actions, resource requirements, and success indicators. Provide comprehensive guidance with examples and best practices.")
    rationale: str = Field(description="Extensive analysis of why this recommendation is important, including market trends, competitive advantages, career impact assessment, and strategic positioning. Provide supporting evidence and success stories.")
    timeline: str = Field(description="Detailed suggested timeline for implementation with phase-by-phase breakdown, milestone definitions, resource allocation, and risk assessment.")
    resources_needed: List[str] = Field(default_factory=list, description="Comprehensive list of resources or prerequisites needed, including specific tools, training, networking opportunities, and budget considerations.")

class ResumeRecommendationSchema(BaseModel):
    """Complete schema for resume recommendation agent output"""
    target_industry: str = Field(description="Industry the recommendations are tailored for")

    resume_improvements: List[ResumeImprovement] = Field(
        default_factory=list,
        description="Specific improvements for resume sections"
    )

    project_improvements: List[ProjectImprovement] = Field(
        default_factory=list,
        description="Recommendations for improving project descriptions and presentation"
    )

    general_recommendations: List[GeneralRecommendation] = Field(
        default_factory=list,
        description="General career and professional development recommendations"
    )

    summary: str = Field(
        description="Executive summary of all recommendations with key priorities and expected outcomes"
    )

    overall_priority_score: int = Field(
        description="Overall priority score from 1-10 indicating how urgently improvements are needed",
        ge=1,
        le=10
    )

    estimated_implementation_time: str = Field(
        description="Estimated time to implement all recommendations (e.g., '2-4 weeks', '1-2 months')"
    )

    success_metrics: List[str] = Field(
        default_factory=list,
        description="How to measure the success of implementing these recommendations"
    )

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    career_vision: Optional[str] = None

class Education(BaseModel):
    university: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[str] = None
    coursework: List[str] = Field(default_factory=list)
    extracurriculars: List[str] = Field(default_factory=list)

class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)

class Leadership(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)

class Project(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)

class Skills(BaseModel):
    technical: List[str] = Field(default_factory=list)
    finance: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)

class CareerGoals(BaseModel):
    short_term: Optional[str] = None
    mid_term: Optional[str] = None
    long_term: Optional[str] = None

class ResumeSchema(BaseModel):
    """Schema for Resume Data"""
    personal: PersonalInfo
    education: Education
    experience: List[Experience] = Field(default_factory=list)
    leadership: List[Leadership] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: Skills
    career_goals: CareerGoals

class FinalOutputState(BaseModel):
    """Schema for the final output from the resume processing workflow"""

    updated_resume: Optional[ResumeSchema] = Field(
        default=None,
        description="The complete updated resume following the ResumeSchema structure"
    )

    changelog: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="List of changes made during resume optimization"
    )

    target_industry: Optional[str] = Field(
        default=None,
        description="The industry the recommendations are tailored for"
    )

    resume_improvements: Optional[List[ResumeImprovement]] = Field(
        default_factory=list,
        description="Detailed improvements for resume sections. Provide extremely comprehensive analysis with specific examples, detailed explanations of why each change is needed, step-by-step implementation guidance, and measurable outcomes. Each improvement should be at least 200-300 words with actionable details, industry benchmarks, and success metrics."
    )

    project_improvements: Optional[List[ProjectImprovement]] = Field(
        default_factory=list,
        description="Comprehensive recommendations for improving project descriptions and presentation. Provide in-depth analysis of each project with detailed enhancement strategies, specific wording suggestions, technology stack optimization, impact quantification methods, and competitive positioning. Each project improvement should be 250-400 words with detailed implementation plans and success measurement frameworks."
    )

    general_recommendations: Optional[List[GeneralRecommendation]] = Field(
        default_factory=list,
        description="Extensive general career and professional development recommendations. Provide comprehensive career strategy analysis, detailed networking strategies, certification pathways, personal branding guidance, industry trend analysis, and long-term career planning. Each recommendation should be 300-500 words with specific action plans, resource requirements, timeline breakdowns, and success indicators."
    )

    summary: Optional[str] = Field(
        default=None,
        description="Comprehensive executive summary of all recommendations with detailed analysis of key priorities, expected outcomes, implementation roadmap, risk assessment, and success measurement framework. Provide a detailed narrative of at least 400-600 words covering strategic positioning, competitive advantages, market trends, and long-term career impact."
    )

    overall_priority_score: Optional[int] = Field(
        default=None,
        description="Overall priority score from 1-10 indicating how urgently improvements are needed. Provide a detailed justification with comprehensive analysis of current market position, competitive landscape, industry trends, skill gaps, and strategic importance. Include detailed scoring methodology and supporting evidence.",
        ge=1,
        le=10
    )

    estimated_implementation_time: Optional[str] = Field(
        default=None,
        description="Detailed estimated time to implement all recommendations with comprehensive breakdown by category, phase-by-phase timeline, resource allocation requirements, and milestone definitions. Include risk factors, dependencies, and contingency planning."
    )

    success_metrics: Optional[List[str]] = Field(
        default_factory=list,
        description="Comprehensive framework for measuring the success of implementing these recommendations. Provide detailed KPIs, measurement methodologies, tracking mechanisms, benchmarking strategies, and success criteria for each recommendation category. Include both quantitative and qualitative metrics with specific measurement timelines."
    )




