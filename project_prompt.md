
# AI Lesson Planner SaaS Application Development Prompt

## Project Overview
Create a complete Software-as-a-Service (SaaS) application called "AI Lesson Planner" that helps educators quickly generate comprehensive lesson plans using AI. The application should have a modern, responsive UI, user authentication, plan generation capabilities, and saving/export functionality.

## Core Features

### 1. User Interface
- Modern, responsive design that works on both desktop and mobile
- Landing page showcasing features and benefits
- Main application page with template selection and plan generation
- History sidebar for quick access to previously created plans
- Modal-based interfaces for template selection and customization
- Expandable/collapsible sections in generated lesson plans

### 2. AI Plan Generation
- Integration with OpenAI's GPT-4o API for generating lesson plans
- Multiple template options (lesson plans, assessments, feedback)
- Subtemplates for more specialized content
- Customization options (grade level, duration, subject, requirements)
- Structured output with sections for objectives, materials, procedures, etc.

### 3. User Features
- Save and access history of generated plans
- Export plans to PDF and Word formats
- Easy sharing of generated content

### 4. Technical Requirements
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript with Bootstrap 5
- OpenAI API integration
- Responsive design principles
- Local storage for plan history
- Session management

## Implementation Details

### Backend (Flask)
- Create REST API endpoints for plan generation
- Implement OpenAI API integration
- Set up template and subtemplate structures
- Handle user input validation and sanitization
- Implement export functionality

### Frontend
- Build responsive UI using Bootstrap 5
- Implement modal-based workflows
- Create expandable/collapsible sections for plan display
- Add PDF/Word export functionality
- Implement local storage for plan history
- Add form validation

### Authentication (Future Enhancement)
- User registration and login
- Secure password storage
- User-specific plan history
- Subscription management

### Deployment
- Configure for deployment on Replit
- Set up proper environment variables
- Configure proper CORS settings

## User Flows

1. **First-time User**
   - Land on marketing page
   - Click "Try Demo Free"
   - Select a template
   - Enter lesson details
   - Generate plan
   - Export or save plan

2. **Returning User**
   - Access saved plans from history
   - Create new plans
   - Modify existing plans

## Data Structures

### Template Object
```json
{
  "template_key": {
    "description": "Template description",
    "subtemplates": {
      "Category1": ["Subtemplate1", "Subtemplate2"],
      "Category2": ["Subtemplate3", "Subtemplate4"]
    }
  }
}
```

### Lesson Plan Object
```json
{
  "title": "Plan Title",
  "overview": "Plan overview text",
  "overview_summary": ["Summary points"],
  "objectives": ["Objective1", "Objective2"],
  "objectives_summary": ["Summary points"],
  "materials": ["Material1", "Material2"],
  "materials_summary": ["Summary points"],
  "procedure": ["Step1", "Step2"],
  "procedure_summary": ["Summary points"],
  "assessment": "Assessment details",
  "assessment_summary": ["Summary points"],
  "extensions": ["Extension1", "Extension2"],
  "extensions_summary": ["Summary points"]
}
```

## Enhancement Roadmap
1. User accounts and authentication
2. Premium templates and features
3. Collaboration features
4. Integration with LMS platforms
5. AI-based improvement suggestions
6. Analytics dashboard for usage patterns

## Technical Implementation Notes
- Use environment variables for API keys and secrets
- Structure code for maintainability and scalability
- Implement proper error handling and user feedback
- Ensure mobile responsiveness at all stages
- Follow accessibility best practices

## Deployment Instructions
1. Configure Flask application with proper settings
2. Set up environment variables for API keys
3. Configure deployment settings on Replit
4. Test deployment thoroughly before release

This comprehensive prompt should provide all necessary details to implement a complete, production-ready AI Lesson Planner SaaS application.
