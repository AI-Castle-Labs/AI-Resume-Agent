# AI Resume Agent

An AI-powered resume processing system that analyzes resumes, provides intelligent recommendations, and generates professional PDF reports.

## 🚀 Features

- **Multi-Agent Workflow**: Uses LangChain with specialized agents for restructuring, recommendations, and rewriting
- **PDF Generation**: Creates professional resume PDFs and detailed recommendation reports
- **Vector Database**: Integrates with ChromaDB for document similarity and embeddings
- **Structured Output**: Uses Pydantic schemas for consistent, structured data
- **Document Processing**: Supports various document formats via Extend AI API

## 🔧 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AI-Castle-Labs/AI-Resume-Agent.git
   cd AI-Resume-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     EXTEND_API_KEY=your_extend_api_key_here
     CHROMA_API_KEY=your_chroma_api_key_here
     CHROMA_TENANT=your_chroma_tenant_here
     CHROMA_DATABASE=Resume
     ```

4. **Run the system**:
   ```bash
   python main.py
   ```

## 🔒 Security

- **API Keys**: Never commit real API keys to the repository
- **Environment Variables**: Use `.env` files (automatically ignored by `.gitignore`)
- **Git History**: If keys were accidentally committed, they have been removed from this repository

## 📁 Project Structure

```
├── agents.py          # Main agent classes and workflow
├── main.py           # Entry point and API integration
├── schema.py         # Pydantic models for structured data
├── state.py          # Agent state management
├── tools.py          # Utility functions and ChromaDB integration
├── prompt.py         # AI prompts and instructions
├── database.py       # Database operations
├── .env             # Environment variables (not committed)
├── .gitignore       # Git ignore rules
└── *.pdf           # Generated PDF outputs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
