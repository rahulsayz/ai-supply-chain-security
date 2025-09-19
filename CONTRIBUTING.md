# Contributing to AI-Powered Supply Chain Attack Prevention System

Thank you for your interest in contributing to our AI-powered cybersecurity platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn package manager
- TypeScript knowledge
- Basic understanding of cybersecurity concepts
- Google Cloud Platform account (for BigQuery AI features)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/supply-chain-cybersecurity.git
   cd supply-chain-cybersecurity
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Build and Test**
   ```bash
   npm run build
   npm test
   ```

5. **Start Development Server**
   ```bash
   npm run dev
   ```

## 📝 Development Guidelines

### Code Style

- **TypeScript**: All code must be written in TypeScript
- **ESLint**: Follow the project's ESLint configuration
- **Prettier**: Code formatting is handled by Prettier
- **Naming**: Use descriptive names for variables, functions, and classes

### Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(api): add new threat prediction endpoint
fix(websocket): resolve connection timeout issue
docs(readme): update installation instructions
test(threats): add unit tests for threat service
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing

### Running Tests

```bash
# All tests
npm test

# With coverage
npm run test:coverage

# Specific test file
npm test -- --grep "health"

# Watch mode
npm run test:watch
```

### Test Requirements

- **Unit Tests**: All new functions and classes must have unit tests
- **Integration Tests**: API endpoints require integration tests
- **Coverage**: Maintain >80% test coverage
- **Mock Data**: Use appropriate mocks for external services

### Test Structure

```typescript
describe('ThreatService', () => {
  beforeEach(() => {
    // Setup
  });

  it('should predict threats accurately', async () => {
    // Test implementation
  });

  afterEach(() => {
    // Cleanup
  });
});
```

## 🏗️ Architecture Guidelines

### Project Structure

```
src/
├── routes/          # API endpoint handlers
├── services/        # Business logic
├── types/           # TypeScript interfaces
├── utils/           # Utility functions
└── __tests__/       # Test files
```

### API Design

- **RESTful**: Follow REST principles
- **Error Handling**: Consistent error responses
- **Validation**: Input validation using TypeScript interfaces
- **Documentation**: OpenAPI/Swagger documentation

### Service Layer

- **Single Responsibility**: Each service has one clear purpose
- **Dependency Injection**: Use constructor injection
- **Error Propagation**: Proper error handling and logging

## 📚 Documentation

### Code Documentation

- **JSDoc**: Document all public methods and classes
- **README**: Update relevant README files
- **API Docs**: Update OpenAPI specifications
- **Examples**: Provide usage examples

### Documentation Structure

All documentation should be placed in the `/docs` folder:

- `/docs/api/` - API documentation
- `/docs/guides/` - User guides
- `/docs/implementation/` - Technical implementation details
- `/docs/integration/` - Integration documentation

## 🔒 Security Guidelines

### Security Best Practices

- **Input Validation**: Validate all inputs
- **Authentication**: Proper authentication mechanisms
- **Authorization**: Role-based access control
- **Data Sanitization**: Sanitize all outputs
- **Error Handling**: Don't expose sensitive information

### Security Review

All security-related changes require:
1. Security impact assessment
2. Code review by security team
3. Penetration testing (if applicable)

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed reproduction steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Node.js version, etc.
6. **Logs**: Relevant error logs or screenshots

### Feature Requests

For feature requests, provide:

1. **Use Case**: Why is this feature needed?
2. **Description**: Detailed feature description
3. **Acceptance Criteria**: How to know it's complete
4. **Priority**: Business priority and urgency

## 🔄 Pull Request Process

### Before Submitting

1. **Tests**: Ensure all tests pass
2. **Linting**: Fix all linting errors
3. **Documentation**: Update relevant documentation
4. **Changelog**: Update CHANGELOG.md if applicable

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one approving review required
3. **Security Review**: Required for security-related changes
4. **Final Testing**: Manual testing in staging environment

## 🌟 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributors page
- Annual contributor highlights

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: development-team@your-domain.com
- **Documentation**: Check `/docs` folder first

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what's best for the community
- Show empathy towards others

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to supply chain cybersecurity!** 🛡️
