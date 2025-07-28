# Semantic Zones Usage Examples

This document provides practical examples of using semantic zones in real-world scenarios.

## Complete Project Analysis Workflow

### Scenario: Understanding a New Codebase

```bash
# Step 1: Learn about the technology stack (conversational)
@deepseek explain what FastAPI is and how it differs from Flask

# Step 2: Get a high-level overview (analysis)
@deepseek analyze this project's overall architecture

# Step 3: Examine the actual files (tool operation)
@deepseek use your tools and read all Python files in the main directory

# Step 4: Study specific components (tool operation)
@deepseek use your tools and examine the database models and API routes

# Step 5: Understand patterns (analysis)
@deepseek analyze the authentication and authorization patterns used

# Step 6: Check for issues (debug)
@deepseek debug any potential security vulnerabilities in the auth system
```

## Bug Investigation Workflow

### Scenario: API Endpoint Returning 500 Errors

```bash
# Step 1: Understand the error (conversational)
@deepseek explain what causes 500 Internal Server Error responses

# Step 2: Analyze the problem space (analysis)
@deepseek analyze the error patterns in this API application

# Step 3: Examine logs and code (tool operation)
@deepseek use your tools and read the error logs and the failing endpoint code

# Step 4: Investigate dependencies (tool operation)
@deepseek use your tools and check the database connection and external service calls

# Step 5: Debug the specific issue (debug)
@deepseek debug why the user authentication endpoint returns 500 errors

# Step 6: Create a solution (creative)
@deepseek create robust error handling and logging for the authentication system
```

## Code Review and Improvement Workflow

### Scenario: Modernizing Legacy Code

```bash
# Step 1: Learn about modern practices (conversational)
@deepseek explain current Python best practices for web API development

# Step 2: Assess current state (analysis)
@deepseek analyze this codebase for adherence to modern Python standards

# Step 3: Examine specific files (tool operation)
@deepseek use your tools and audit all Python files for code quality issues

# Step 4: Understand legacy patterns (analysis)
@deepseek analyze why this code might have been written this way originally

# Step 5: Identify specific problems (debug)
@deepseek debug the performance bottlenecks in the database queries

# Step 6: Implement improvements (creative)
@deepseek create modernized versions of the legacy database access patterns
```

## Learning and Documentation Workflow

### Scenario: Learning Docker for Deployment

```bash
# Step 1: Learn fundamentals (conversational)
@deepseek explain how Docker containers work and why they're useful

# Step 2: Study existing setup (analysis)
@deepseek analyze the Docker configuration in this project

# Step 3: Examine configuration files (tool operation)
@deepseek use your tools and read the Dockerfile, docker-compose.yml, and any deployment scripts

# Step 4: Understand current issues (debug)
@deepseek debug why the Docker build process is failing in CI/CD

# Step 5: Create improvements (creative)
@deepseek create a multi-stage Dockerfile optimized for production deployment

# Step 6: Document the setup (creative)
@deepseek create comprehensive documentation for the Docker deployment process
```

## Security Audit Workflow

### Scenario: Security Assessment

```bash
# Step 1: Learn about security principles (conversational)
@deepseek explain common web application security vulnerabilities

# Step 2: Assess security posture (analysis)
@deepseek analyze this application for potential security vulnerabilities

# Step 3: Examine sensitive code (tool operation)
@deepseek use your tools and audit authentication, authorization, and data validation code

# Step 4: Check dependencies (tool operation)
@deepseek use your tools and examine the requirements.txt and package.json for vulnerable dependencies

# Step 5: Investigate specific issues (debug)
@deepseek debug potential SQL injection vulnerabilities in the database queries

# Step 6: Implement security measures (creative)
@deepseek create secure input validation and sanitization functions
```

## Performance Optimization Workflow

### Scenario: Slow Application Performance

```bash
# Step 1: Understand performance concepts (conversational)
@deepseek explain common causes of web application performance issues

# Step 2: Analyze performance patterns (analysis)
@deepseek analyze this application's performance characteristics

# Step 3: Profile the application (tool operation)
@deepseek use your tools and examine profiling data and performance logs

# Step 4: Identify bottlenecks (debug)
@deepseek debug why the user dashboard loads slowly

# Step 5: Create optimizations (creative)
@deepseek create optimized database queries and caching strategies

# Step 6: Validate improvements (tool operation)
@deepseek use your tools and implement performance monitoring and benchmarking
```

## API Development Workflow

### Scenario: Building New REST Endpoints

```bash
# Step 1: Learn API design principles (conversational)
@deepseek explain REST API best practices and design patterns

# Step 2: Analyze existing API structure (analysis)
@deepseek analyze the current API design and patterns in this project

# Step 3: Study existing endpoints (tool operation)
@deepseek use your tools and examine the existing API route definitions and handlers

# Step 4: Understand data models (tool operation)
@deepseek use your tools and read the database models and schemas

# Step 5: Create new endpoints (creative)
@deepseek create REST endpoints for user profile management with proper validation

# Step 6: Add comprehensive testing (creative)
@deepseek create unit tests and integration tests for the new API endpoints
```

## Database Design and Migration Workflow

### Scenario: Database Schema Changes

```bash
# Step 1: Learn database design principles (conversational)
@deepseek explain database normalization and modern schema design practices

# Step 2: Analyze current schema (analysis)
@deepseek analyze the current database schema design and relationships

# Step 3: Examine schema files (tool operation)
@deepseek use your tools and read all database migration files and model definitions

# Step 4: Identify schema issues (debug)
@deepseek debug potential database performance issues and design problems

# Step 5: Design improvements (creative)
@deepseek create optimized database schema with proper indexing and relationships

# Step 6: Create migration scripts (creative)
@deepseek create safe database migration scripts for the schema changes
```

## Team Collaboration Workflow

### Scenario: Onboarding New Team Members

```bash
# Step 1: Understand project context (conversational)
@deepseek explain this project's purpose and how it fits in the business context

# Step 2: Get architecture overview (analysis)
@deepseek analyze the overall system architecture and component relationships

# Step 3: Study codebase structure (tool operation)
@deepseek use your tools and create a comprehensive map of the codebase structure

# Step 4: Identify learning resources (analysis)
@deepseek analyze what documentation and examples would help new developers

# Step 5: Create onboarding materials (creative)
@deepseek create a developer onboarding guide with setup instructions

# Step 6: Document development workflows (creative)
@deepseek create documentation for common development tasks and workflows
```

## Tips for Effective Zone Usage

### 1. Start Broad, Then Narrow
- Begin with conversational questions to understand concepts
- Use analysis to get overviews
- Use tool operations for detailed examination
- Use debug for specific problem-solving
- Use creative for implementation

### 2. Use Progressive Disclosure
- Don't jump straight to file operations
- Build understanding first with explanations
- Analyze before you examine files
- Debug specific issues after understanding the context

### 3. Combine Zones Strategically
- **Learn → Analyze → Examine → Debug → Create**
- **Explain → Review → Investigate → Fix → Improve**
- **Understand → Assess → Audit → Troubleshoot → Implement**

### 4. Match Complexity to Zone
- Simple questions: conversational
- Overview needs: analysis
- File access: tool operation
- Problem solving: debug
- Building new things: creative

### 5. Use Explicit Triggers
- Always use clear zone triggers
- Be specific about what you want
- Don't rely on the AI to guess your intent
- Use the pattern that matches your goal

These workflows demonstrate how semantic zones create a natural progression from learning to implementation, ensuring you get the right type of help at each stage of your development process.
