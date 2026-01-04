# IAM-Maturity-API

**IAM-Maturity-API** is a FastAPI-based service that provides automated assessment of Identity and Access Management (IAM) maturity, specifically for the banking industry. This project uses AI (Groq API) to evaluate general IAM governance questions and produces structured YAML outputs to guide downstream IAM domain evaluations.  

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Folder Structure](#folder-structure)  
- [Setup and Installation](#setup-and-installation)  
- [Environment Variables](#environment-variables)  
- [Running Locally](#running-locally)  
- [Testing the API](#testing-the-api)  
- [Handling Multiple Questions](#handling-multiple-questions)  
- [Deployment to Render](#deployment-to-render)  
- [Future Enhancements](#future-enhancements)  
- [References](#references)  

---

## Project Overview

The API allows:

1. **General IAM Question Assessment**: Users can submit general IAM governance questions in YAML format.  
2. **Structured YAML Output**: The response is a fully structured YAML indicating:  
   - Governance maturity signals  
   - Domain influence  
   - Assessment rationale  
   - Confidence level  
3. **Domain Maturity Evaluation** (planned): Normalized outputs of multiple general questions can be used to evaluate **specific IAM domains** such as Access Governance, Monitoring & Audit, etc.

The system is **AI-powered** but uses clear **structured prompts and rules** for banking compliance and regulatory adherence.

---

## Features

- FastAPI backend with CORS enabled  
- AI evaluation using **Groq API**  
- Input: YAML-formatted IAM question  
- Output: YAML-formatted structured assessment  
- Supports multi-question aggregation and normalization  
- Ready for future integration with **LangChain** for full agentic evaluation

---

## Folder Structure

## Run main.py
You can run if from the folder "python main.py" or  
uvicorn main:app --reload --host 0.0.0.0 --port 8000
