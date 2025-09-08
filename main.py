


"""


Use extend api 


Resume -> Extend API -> data -> Scrapper/ AI Agents -> Updated Resume


"""
import requests

api_key = "sk_-gYuCSHcFt9fVzWsKj1Av"


def extend_api(id):
    response = requests.post(
        "https://api.extend.ai/processor_runs",
        json={
            "processorId": "dp_EeQuIXO_Lh5QOfVfOXRAk",
            "file": {
                "fileId": id
            },
            "sync": True,
            "config": {
            "type": "EXTRACT",
            "baseProcessor": "extraction_performance",
            "baseVersion": "4.2.0",
            "schema": {
                "type": "object",
                "required": [
                "Name",
                "Experience",
                "Projects",
                "Skills",
                "Education"
                ],
                "properties": {
                "Name": {
                    "type": [
                    "string",
                    "null"
                    ]
                },
                "Skills": {
                    "type": [
                    "string",
                    "null"
                    ]
                },
                "Projects": {
                    "type": [
                    "string",
                    "null"
                    ]
                },
                "Education": {
                    "type": [
                    "string",
                    "null"
                    ]
                },
                "Experience": {
                    "type": [
                    "string",
                    "null"
                    ]
                }
                },
                "additionalProperties": False
            },
            "advancedOptions": {
                "citationsEnabled": True,
                "chunkingOptions": {
                "chunkSelectionStrategy": "intelligent"
                },
                "advancedFigureParsingEnabled": True
            }
            }
        },
        headers={
            "x-extend-api-version": "2025-04-21",
            "Authorization": "Bearer sk_U-NBXpmL0ofRvYCltxoh7",
            "Content-Type": "application/json",
        },
    )
    final_output = {}

    final_output['Name'] =  response.json().get('processorRun').get("output").get("value").get("Name")
    final_output['Education'] = response.json().get('processorRun').get("output").get("value").get("Education")
    final_output['Experience'] = response.json().get('processorRun').get("output").get("value").get("Experience")
    final_output['Skills'] = response.json().get('processorRun').get("output").get("value").get("Skills")
    final_output['projects'] = response.json().get('processorRun').get("output").get("value").get("projects")

    return final_output






def info_dump():
    random_information = """Name: Ashleyn Castelino. Senior at the University of Illinois Urbana-Champaign (UIUC), majoring in Finance and Computer Science with a GPA of 3.3. Accepted into an MS Business Analytics program. Career vision is to build both a macro hedge fund and an AI software holding company by age 35, running them in parallel. Entrepreneurial focus includes macro advisory, AI startups, automation tools, and B2B SaaS solutions.

Education: University of Illinois Urbana-Champaign, Finance & Computer Science major, GPA 3.3. Coursework includes equity analysis, fixed income, commodities, macroeconomics, data structures, databases, machine learning, and business analytics. Extracurriculars include co-founding clubs, developing apps, and TA positions.

Professional Experience: Equity Research Intern at Westlake Securities in Austin, Texas (Oct 2024 – Present). Responsibilities: analyzed 10-K and 10-Q filings in the energy and financial sectors, conducted industry and macroeconomic research, built DCF and three-statement models, and supported senior analysts with client-ready reports. Tech Consultant for a Fortune 500 client: integrated AI into hardware and software systems, attended weekly client calls, and evaluated AI in data centers, fiber optics, PCIEs, and interconnect technologies. Nonprofit experience includes assisting in fundraising strategies and donor engagement.

Leadership & Student Organizations: Co-Founder of the Equity Research Association, leading workshops on valuation, financial modeling, and equity pitches. Founder of the Macro Investing Association (MIA), a club focused on macroeconomics, trading, and FX, teaching weekly modules on equities, fixed income, commodities, and currencies, and running a semester-long PM program. Council of Presidents (COP) member for Gies College of Business, promoting collaboration among business RSOs and aligning them with the college brand. Teaching Assistant at UIUC, mentoring students in finance and technical skills. Project lead in the Data Science Club, developing a Python-based model to predict economic defaults using sector data.

Technical Projects: College Marketplace App using React and Django backend, allowing students to upload items for sale with features like pictures, chat, friend requests, and transactions. Healthcare AI Bot using Retrieval-Augmented Generation (RAG) for document-based insights. Client Scooping Software that records Zoom call transcripts, enables post-call querying, generates PowerPoint slides and PDF summaries, and gives pass/fail recommendations based on historical data. Resume Recommendation AI System using indexing and retrieval layers with embeddings for semantic search. Code Program Management Tool that scrapes GitHub data, generates weekly reports, and tracks project leads’ updates.

Skills: Finance & Investing (equity research, DCF, financial modeling, macroeconomic analysis, fixed income, commodities, FX, private equity research). Programming (Python, SQL, React, Django, TypeScript, Apache Kafka, Apache Spark). AI/ML (RAG, LangGraph, GraphRAG, summarization, chatbot development, semantic search, NLP). Business Analytics Tools (Excel, Bloomberg, FactSet). Soft Skills (leadership, teaching, public speaking, consulting, client management).

Career Goals: Short-term goal is to gain experience in finance and AI/tech roles such as equity research, AI strategy, or data analytics. Mid-term goal is to launch AI software ventures in B2B automation. Long-term goal is to run a macro hedge fund and AI company in parallel.
"""
