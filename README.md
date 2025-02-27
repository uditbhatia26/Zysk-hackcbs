# Zysk

Zysk is a fintech web platform developed for CodeKshetra, aimed at providing personalized financial insights and investment guidance. Through a structured questionnaire, Zysk assesses a user's financial mindset, generating customized reports and real-time investment suggestions. The platform leverages AI and real-time data integration to offer a modern financial advisory experience.

## Overview

Zysk simplifies financial decision-making by assessing users' financial mindsets through a detailed 15-question questionnaire. Based on the responses, the platform uses AI to generate a tailored report that includes investment strategies and a mindset analysis. Users can receive reports via email and get real-time stock updates through WhatsApp notifications.

## Features

- **Financial Mindset Assessment**: Users answer 15 questions to gauge their financial mindset.
- **AI-Generated Reports**: A generative AI model analyzes responses to provide personalized insights and investment suggestions.
- **WhatsApp Integration**: Real-time updates on trending stocks and market news sent directly to users' WhatsApp.
- **Email Notifications**: Users receive detailed reports of their financial profile and suggested strategies.
- **Real-time Market Updates**: Access to trending stock information and other relevant updates.

## Tech Stack

- **Frontend**:

  - HTML5, CSS3, JavaScript

- **Backend**:

  - Python (Flask): For the AI model and backend processes

- **AI Model**:

  - Generative AI (Gemini) trained to analyze user responses and generate financial insights
  - Model tuning using libraries like `Transformers` and `scikit-learn`

- **APIs**:
  - **UltraMsg API**: To send WhatsApp updates
  - **SMTP**: For sending email reports

## Architecture

Zysk's architecture follows a microservices approach, with clear separation between user management, AI processing, and notification modules. Key components include:

1. **Frontend**: Collects user responses and displays results.
2. **Backend (Flask)**: Manages API requests, handles user data, and triggers AI processes.
3. **AI Service (Python)**: Processes user data and generates financial insights using an Gemini.
4. **Notification Services**: Uses UltraMsg for WhatsApp and SMTP for emails.
