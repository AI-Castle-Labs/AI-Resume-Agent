
import json
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from tools import extractiontool
import os
from dotenv import load_dotenv
import tweepy
from fpdf import FPDF
import json
from schema import ResumeSchema,SonarRecommendations,FinalOutputState
from langchain_openai import ChatOpenAI
from prompt import rewrite_prompt
from state import AgentState
from langchain.tools import StructuredTool
from main import extend_api


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class ResumeAgent:

    def __init__(self,document_id):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.extractiontool = extractiontool(document = document_id)
        self.document_id = document_id
        self.document = extend_api(document_id)
        self.similar_document = self.extractiontool.similar_document(self.document,self.api_key)


    def restructuring_agent(self,State):
        try:
            prompt = """You are part of an AI Resume Extraction Tool. Your task is to extract and structure the provided resume information into a clear JSON format.
            Your job is to take the information and reword it more professionally, classify the industry of the resunme and add that to the output"""
            llm = init_chat_model("gpt-4o-2024-08-06", temperature = 0.0, model_provider = "openai", api_key = self.api_key)
            llm = llm.with_structured_output(ResumeSchema)
            result = llm.invoke([
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': f"Extract and structure this resume information:\n\n{State.original_resume_text}"}
            ])
            
            State.structured_resume = result
            State.restructuring_status = "completed"
            return State
        except Exception as e:
            State.restructuring_status = "error"
            State.restructuring_errors.append(str(e))
            return State


    def recommendation_agent(self,State):
        """Get industry-specific resume recommendations based on current trends"""
        try:
            llm = ChatOpenAI(
                model="sonar",
                base_url="https://api.perplexity.ai",  # Important: override base URL
                api_key= os.getenv(sonar_key)
            )
            structured_llm = llm.with_structured_output(SonarRecommendations)

            result = structured_llm.invoke([
                {"role": "system", "content": "You are an expert industry advisor for a resume company."},
                {"role": "user", "content": "Provide detailed recommendations for the finance industry, keep every point within 30 words"}
            ])
            State.industry_recommendations = result
            State.recommendation_status = "completed"
            return State
        except Exception as e:
            State.recommendation_status = "error"
            State.recommendation_errors.append(str(e))
            return State

    def rewriting_agent(self,State):
        """Generates improved resume lines"""
        recommendation = State.industry_recommendations
        similar_docs = self.similar_document if hasattr(self, 'similar_document') else []
        industry_insights = recommendation.current_trends 

        # Format the prompt with available context
        context_prompt = f"""
        <Context>
        The agent will receive the following inputs at runtime:
        - resume_text: the original resume text (string)
        - similar_docs: {similar_docs}
        - industry insight: {industry_insights}
        </Context>
        """

        full_prompt = rewrite_prompt.replace("<Context>", context_prompt)

        llm = init_chat_model("gpt-4o-2024-08-06", temperature = 0.0, model_provider = "openai", api_key = self.api_key)
        llm = llm.with_structured_output(FinalOutputState)

        resume = State.original_resume_text

        result = llm.invoke([
            {'role':'system', 'content': full_prompt},
            {'role':'user','content': f"Analyze the following resume and provide improvements:\n\n{resume}"}
        ])

        # Return only the final output without internal state information
        State.resume_improvements = result.resume_improvements
        State.project_improvements = result.project_improvements
        State.general_recommendations = result.general_recommendations
        State.summary = result.summary
        State.overall_priority_score = result.overall_priority_score
        State.estimated_implementation_time = result.estimated_implementation_time
        State.success_metrics = result.success_metrics
        
        # Set the structured resume output
        if hasattr(result, 'updated_resume') and result.updated_resume:
            print(f"Setting rewritten_resume: {type(result.updated_resume)}")
            State.rewritten_resume = result.updated_resume
        else:
            print("No updated_resume found in result")
            State.rewritten_resume = None
        

        return State

    def generate_resume_pdf(self, resume_data, output_path="updated_resume.pdf"):
        """Generate a professional one-page PDF resume from the final resume data"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(15, 15, 15)  # Set margins for better layout
        pdf.set_auto_page_break(auto=True, margin=15)

        try:
            # Title
            pdf.set_font("Arial", size=18)
            pdf.cell(0, 12, txt="PROFESSIONAL RESUME", ln=True, align='C')
            pdf.ln(8)

            # Personal Information
            if hasattr(resume_data, 'personal') and resume_data.personal:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="PERSONAL INFORMATION", ln=True)
                pdf.set_font("Arial", size=11)

                if hasattr(resume_data.personal, 'name') and resume_data.personal.name:
                    pdf.set_font("Arial", size=13)
                    pdf.cell(0, 8, txt=resume_data.personal.name, ln=True, align='C')
                    pdf.set_font("Arial", size=11)

                if hasattr(resume_data.personal, 'summary') and resume_data.personal.summary:
                    pdf.ln(3)
                    # Handle multi-line summary with proper wrapping
                    summary_lines = resume_data.personal.summary.split('\n')
                    for line in summary_lines:
                        if line.strip():
                            pdf.multi_cell(0, 5, txt=line.strip(), align='L')
                    pdf.ln(4)

                if hasattr(resume_data.personal, 'career_vision') and resume_data.personal.career_vision:
                    pdf.multi_cell(0, 5, txt=f"Career Vision: {resume_data.personal.career_vision}", align='L')
                    pdf.ln(2)

                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Education Section
            if hasattr(resume_data, 'education') and resume_data.education:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="EDUCATION", ln=True)
                pdf.set_font("Arial", size=11)

                if hasattr(resume_data.education, 'university') and resume_data.education.university:
                    pdf.set_font("Arial", size=11)
                    pdf.cell(0, 7, txt=resume_data.education.university, ln=True)

                if hasattr(resume_data.education, 'major') and resume_data.education.major:
                    pdf.cell(0, 6, txt=resume_data.education.major, ln=True)

                if hasattr(resume_data.education, 'gpa') and resume_data.education.gpa:
                    pdf.cell(0, 6, txt=f"GPA: {resume_data.education.gpa}", ln=True)

                if hasattr(resume_data.education, 'coursework') and resume_data.education.coursework:
                    pdf.cell(0, 6, txt=f"Relevant Coursework: {', '.join(resume_data.education.coursework)}", ln=True)

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Experience Section
            if hasattr(resume_data, 'experience') and resume_data.experience:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="PROFESSIONAL EXPERIENCE", ln=True)
                pdf.set_font("Arial", size=11)

                for exp in resume_data.experience:
                    # Company and Role
                    if hasattr(exp, 'company') and exp.company:
                        pdf.set_font("Arial", size=11)
                        pdf.cell(0, 7, txt=exp.company, ln=True)

                    if hasattr(exp, 'role') and exp.role:
                        pdf.cell(0, 6, txt=exp.role, ln=True)

                    if hasattr(exp, 'duration') and exp.duration:
                        pdf.cell(0, 5, txt=f"Duration: {exp.duration}", ln=True)

                    # Responsibilities
                    if hasattr(exp, 'responsibilities') and exp.responsibilities:
                        for resp in exp.responsibilities:
                            if resp.strip():
                                pdf.cell(8, 5, txt="-", ln=0)
                                pdf.multi_cell(0, 5, txt=resp.strip(), align='L')

                    pdf.ln(2)

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Skills Section
            if hasattr(resume_data, 'skills') and resume_data.skills:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="SKILLS", ln=True)
                pdf.set_font("Arial", size=11)

                if hasattr(resume_data.skills, 'technical') and resume_data.skills.technical:
                    pdf.cell(0, 7, txt="Technical Skills:", ln=True)
                    pdf.multi_cell(0, 5, txt=', '.join(resume_data.skills.technical), align='L')

                if hasattr(resume_data.skills, 'finance') and resume_data.skills.finance:
                    pdf.cell(0, 7, txt="Finance Skills:", ln=True)
                    pdf.multi_cell(0, 5, txt=', '.join(resume_data.skills.finance), align='L')

                if hasattr(resume_data.skills, 'soft_skills') and resume_data.skills.soft_skills:
                    pdf.cell(0, 7, txt="Soft Skills:", ln=True)
                    pdf.multi_cell(0, 5, txt=', '.join(resume_data.skills.soft_skills), align='L')

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Projects Section
            if hasattr(resume_data, 'projects') and resume_data.projects:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="PROJECTS", ln=True)
                pdf.set_font("Arial", size=11)

                for project in resume_data.projects:
                    if hasattr(project, 'name') and project.name:
                        pdf.cell(0, 7, txt=project.name, ln=True)

                    if hasattr(project, 'description') and project.description:
                        pdf.multi_cell(0, 5, txt=project.description, align='L')

                    if hasattr(project, 'technologies') and project.technologies:
                        pdf.cell(0, 5, txt=f"Technologies: {', '.join(project.technologies)}", ln=True)

                    pdf.ln(2)

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Leadership Section
            if hasattr(resume_data, 'leadership') and resume_data.leadership:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="LEADERSHIP & ACTIVITIES", ln=True)
                pdf.set_font("Arial", size=11)

                for leadership in resume_data.leadership:
                    if hasattr(leadership, 'name') and leadership.name:
                        pdf.cell(0, 7, txt=leadership.name, ln=True)

                    if hasattr(leadership, 'role') and leadership.role:
                        pdf.cell(0, 6, txt=leadership.role, ln=True)

                    if hasattr(leadership, 'achievements') and leadership.achievements:
                        for achievement in leadership.achievements:
                            if achievement.strip():
                                pdf.cell(8, 5, txt="-", ln=0)
                                pdf.multi_cell(0, 5, txt=achievement.strip(), align='L')

                    pdf.ln(2)

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Career Goals Section (Condensed)
            if hasattr(resume_data, 'career_goals') and resume_data.career_goals:
                pdf.set_font("Arial", size=14)
                pdf.cell(0, 10, txt="CAREER OBJECTIVES", ln=True)
                pdf.set_font("Arial", size=11)

                if hasattr(resume_data.career_goals, 'short_term') and resume_data.career_goals.short_term:
                    pdf.cell(0, 7, txt="Short-term:", ln=True)
                    pdf.multi_cell(0, 5, txt=resume_data.career_goals.short_term, align='L')

                if hasattr(resume_data.career_goals, 'long_term') and resume_data.career_goals.long_term:
                    pdf.cell(0, 7, txt="Long-term:", ln=True)
                    pdf.multi_cell(0, 5, txt=resume_data.career_goals.long_term, align='L')

                pdf.ln(2)
                # Horizontal line after section
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)

            # Save the PDF
            pdf.output(output_path)
            print(f"Professional one-page resume PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
    def generate_recommendations_pdf(self, final_output, output_path="resume_recommendations.pdf"):
        """Generate a PDF with resume analysis and recommendations"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)

        try:
            # Title
            pdf.set_font("Arial", 'B', 20)
            pdf.cell(0, 15, txt="RESUME ANALYSIS & RECOMMENDATIONS", ln=True, align='C')
            pdf.ln(10)

            # Summary Section
            if final_output.get("summary"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="EXECUTIVE SUMMARY", ln=True)
                pdf.set_font("Arial", size=12)
                # Split summary into paragraphs for better readability
                summary_paragraphs = final_output["summary"].split('\n\n')
                for paragraph in summary_paragraphs:
                    if paragraph.strip():
                        pdf.multi_cell(0, 6, txt=paragraph.strip(), align='L')
                        pdf.ln(4)
                pdf.ln(3)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Overall Priority Score
            if final_output.get("overall_priority_score"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="OVERALL PRIORITY SCORE", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 8, txt=f"Score: {final_output['overall_priority_score']}/10", ln=True)
                pdf.ln(3)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Estimated Implementation Time
            if final_output.get("estimated_implementation_time"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="ESTIMATED IMPLEMENTATION TIME", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 6, txt=final_output["estimated_implementation_time"], align='L')
                pdf.ln(3)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Resume Improvements
            if final_output.get("resume_improvements"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="RESUME IMPROVEMENTS", ln=True)
                pdf.set_font("Arial", size=12)

                for improvement in final_output["resume_improvements"]:
                    if hasattr(improvement, 'recommended_change') and improvement.recommended_change:
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(0, 10, txt=f"Section: {improvement.section}", ln=True)
                        pdf.set_font("Arial", size=12)

                        if hasattr(improvement, 'current_issue') and improvement.current_issue:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Current Issue:", ln=True)
                            pdf.set_font("Arial", size=11)
                            pdf.multi_cell(0, 5, txt=improvement.current_issue, align='L')
                            pdf.ln(3)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt="Recommended Change:", ln=True)
                        pdf.set_font("Arial", size=11)
                        pdf.multi_cell(0, 5, txt=improvement.recommended_change, align='L')
                        pdf.ln(3)

                        if hasattr(improvement, 'expected_impact') and improvement.expected_impact:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Expected Impact:", ln=True)
                            pdf.set_font("Arial", size=11)
                            pdf.multi_cell(0, 5, txt=improvement.expected_impact, align='L')
                            pdf.ln(3)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt=f"Priority: {improvement.priority}", ln=True)
                        pdf.ln(4)
                    pdf.ln(3)

                pdf.ln(2)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Project Improvements
            if final_output.get("project_improvements"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="PROJECT IMPROVEMENTS", ln=True)
                pdf.set_font("Arial", size=12)

                for improvement in final_output["project_improvements"]:
                    if hasattr(improvement, 'improvement_suggestion') and improvement.improvement_suggestion:
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(0, 10, txt=f"Project: {improvement.project_name}", ln=True)
                        pdf.set_font("Arial", size=12)

                        if hasattr(improvement, 'current_description') and improvement.current_description:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Current Description:", ln=True)
                            pdf.set_font("Arial", size=11)
                            pdf.multi_cell(0, 5, txt=improvement.current_description, align='L')
                            pdf.ln(3)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt="Improvement Suggestion:", ln=True)
                        pdf.set_font("Arial", size=11)
                        pdf.multi_cell(0, 5, txt=improvement.improvement_suggestion, align='L')
                        pdf.ln(3)

                        if hasattr(improvement, 'technologies_to_highlight') and improvement.technologies_to_highlight:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Technologies to Highlight:", ln=True)
                            pdf.set_font("Arial", size=11)
                            pdf.multi_cell(0, 5, txt=', '.join(improvement.technologies_to_highlight), align='L')
                            pdf.ln(3)

                        if hasattr(improvement, 'metrics_to_add') and improvement.metrics_to_add:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Metrics to Add:", ln=True)
                            pdf.set_font("Arial", size=11)
                            for metric in improvement.metrics_to_add:
                                pdf.cell(8, 5, txt="-", ln=0)
                                pdf.multi_cell(0, 5, txt=metric, align='L')
                            pdf.ln(3)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt=f"Priority: {improvement.priority}", ln=True)
                        pdf.ln(4)
                    pdf.ln(3)

                pdf.ln(2)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # General Recommendations
            if final_output.get("general_recommendations"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="GENERAL RECOMMENDATIONS", ln=True)
                pdf.set_font("Arial", size=12)

                for recommendation in final_output["general_recommendations"]:
                    if hasattr(recommendation, 'recommendation') and recommendation.recommendation:
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(0, 10, txt=f"Category: {recommendation.category}", ln=True)
                        pdf.set_font("Arial", size=12)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt="Recommendation:", ln=True)
                        pdf.set_font("Arial", size=11)
                        pdf.multi_cell(0, 5, txt=recommendation.recommendation, align='L')
                        pdf.ln(3)

                        if hasattr(recommendation, 'rationale') and recommendation.rationale:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Rationale:", ln=True)
                            pdf.set_font("Arial", size=11)
                            pdf.multi_cell(0, 5, txt=recommendation.rationale, align='L')
                            pdf.ln(3)

                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt=f"Timeline: {recommendation.timeline}", ln=True)
                        pdf.ln(3)

                        if hasattr(recommendation, 'resources_needed') and recommendation.resources_needed:
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(0, 8, txt="Resources Needed:", ln=True)
                            pdf.set_font("Arial", size=11)
                            for resource in recommendation.resources_needed:
                                pdf.cell(8, 5, txt="-", ln=0)
                                pdf.multi_cell(0, 5, txt=resource, align='L')
                            pdf.ln(3)

                        pdf.ln(4)
                    pdf.ln(3)

                pdf.ln(2)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Success Metrics
            if final_output.get("success_metrics"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="SUCCESS METRICS", ln=True)
                pdf.set_font("Arial", size=12)

                for i, metric in enumerate(final_output["success_metrics"], 1):
                    if metric.strip():
                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, txt=f"Metric {i}:", ln=True)
                        pdf.set_font("Arial", size=11)
                        pdf.multi_cell(0, 5, txt=metric.strip(), align='L')
                        pdf.ln(3)

                pdf.ln(2)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Target Industry
            if final_output.get("target_industry"):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, txt="TARGET INDUSTRY", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 8, txt=final_output["target_industry"], ln=True)
                pdf.ln(3)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(6)

            # Save the PDF
            pdf.output(output_path)
            print(f"Resume recommendations PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error generating recommendations PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def run(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("restructuring_agent",self.restructuring_agent)
        workflow.add_node("recommendation_agent", self.recommendation_agent)
        workflow.add_node("rewriting_agent", self.rewriting_agent)
        
        workflow.add_edge(START, "restructuring_agent")
        workflow.add_edge("restructuring_agent","recommendation_agent")
        workflow.add_edge("recommendation_agent","rewriting_agent")
        workflow.add_edge("rewriting_agent", END)
        # Compile and run the workflow
        app = workflow.compile()

        initial_state = AgentState(
            original_resume_text= str(self.document)
        )
        result = app.invoke(input = initial_state)

        # Return only the final output from the rewriting_agent
        # Extract the clean recommendations that were generated
        final_output = {
            "updated_resume": result.get("rewritten_resume"),
            "changelog": result.get("changelog", []),
            "target_industry": result.get("target_industry"),
            "resume_improvements": result.get("resume_improvements", []),
            "project_improvements": result.get("project_improvements", []),
            "general_recommendations": result.get("general_recommendations", []),
            "summary": result.get("summary"),
            "overall_priority_score": result.get("overall_priority_score"),
            "estimated_implementation_time": result.get("estimated_implementation_time"),
            "success_metrics": result.get("success_metrics", [])
        }

        # Generate PDF if updated resume is available
        pdf_path = None
        recommendations_pdf_path = None
        if result.get("rewritten_resume"):
            print(f"Found rewritten_resume: {type(result.get('rewritten_resume'))}")
            try:
                print("Generating PDF resume...")
                pdf_path = self.generate_resume_pdf(result["rewritten_resume"])
                if pdf_path:
                    print(f"PDF generated successfully: {pdf_path}")
                else:
                    print("PDF generation returned None")
            except Exception as e:
                print(f"Error generating PDF: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("No rewritten_resume found in result")

        # Generate recommendations PDF
        try:
            print("Generating recommendations PDF...")
            recommendations_pdf_path = self.generate_recommendations_pdf(final_output)
            if recommendations_pdf_path:
                print(f"Recommendations PDF generated successfully: {recommendations_pdf_path}")
            else:
                print("Recommendations PDF generation returned None")
        except Exception as e:
            print(f"Error generating recommendations PDF: {str(e)}")
            import traceback
            traceback.print_exc()

        # Add PDF paths to output if generated
        if pdf_path:
            final_output["pdf_path"] = pdf_path
        if recommendations_pdf_path:
            final_output["recommendations_pdf_path"] = recommendations_pdf_path

        return final_output


agent = ResumeAgent("file_JAisL9XtC7lAdqRnhdzLp")

print(agent.run())
