# GitHub Actions Workflows

This directory contains GitHub Actions workflows for continuous integration, delivery, and security scanning.

## Available Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Trigger:** Push to `main` branch or pull requests targeting `main`

**Jobs:**
- **Test**: Runs pytest with coverage and uploads results to Codecov
- **Lint**: Runs pylint, mypy, and safety checks
- **Build**: Builds and pushes Docker image to Docker Hub (on main branch only)
- **CodeQL Analysis**: Advanced code analysis using GitHub's CodeQL engine
- **Security Scan**: Runs Bandit and Safety security scanners

**Secrets Required:**
- `CODECOV_TOKEN`: For uploading coverage reports
- `DOCKER_HUB_USERNAME`: Docker Hub username
- `DOCKER_HUB_TOKEN`: Docker Hub access token

**CodeQL Features:**
- Advanced static analysis for Python code
- Security vulnerability detection
- Code quality analysis
- Integrated with GitHub security alerts

### 2. Scheduled Security Scan (`security-scan.yml`)

**Trigger:** Every Sunday at midnight (00:00 UTC) or manually via workflow_dispatch

**Jobs:**
- **Security Scan**: Runs comprehensive security scans and generates reports

**Artifacts:**
- `security-scan-results-<run_id>`: JSON results from Bandit and Safety
- `security-report-<run_id>`: Human-readable security report

### 3. Documentation (`docs.yml`)

**Trigger:** Push to `main` branch affecting documentation files, or manually

**Jobs:**
- **Build Documentation**: Builds documentation artifacts
- **Deploy Documentation**: (Commented out) Would deploy to GitHub Pages

## Setup Instructions

1. **Add required secrets to your GitHub repository:**
   - Go to Settings > Secrets and variables > Actions
   - Add `CODECOV_TOKEN`, `DOCKER_HUB_USERNAME`, and `DOCKER_HUB_TOKEN`

2. **Enable Codecov integration:**
   - Sign up at codecov.io
   - Add your repository
   - Copy the repository upload token to `CODECOV_TOKEN` secret

3. **Docker Hub setup:**
   - Create a Docker Hub account
   - Create an access token with read/write permissions
   - Add credentials to GitHub secrets

## Usage

### Running workflows manually

1. Go to the Actions tab in your GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow" button
4. Select branch and any required parameters
5. Click "Run workflow"

### Monitoring workflows

- View workflow runs in the Actions tab
- Check logs for each step
- Download artifacts from completed runs
- Set up notifications for workflow failures

## Customization

### Modifying existing workflows

1. Edit the YAML files in `.github/workflows/`
2. Commit and push changes to trigger workflow validation
3. Monitor the workflow run to ensure changes work correctly

### Adding new workflows

1. Create a new `.yml` file in `.github/workflows/`
2. Define triggers, jobs, and steps
3. Test the workflow by pushing changes or using workflow_dispatch

## Best Practices

- **Keep workflows focused**: Each workflow should have a single responsibility
- **Use caching**: Cache dependencies and build artifacts to speed up workflows
- **Parallelize jobs**: Run independent jobs in parallel when possible
- **Use artifacts**: Store build outputs and reports as artifacts
- **Monitor costs**: Be aware of GitHub Actions usage limits and costs

## Troubleshooting

### Common issues

1. **Workflow not triggering**: Check branch filters and path filters
2. **Permission errors**: Ensure secrets are correctly set up
3. **Dependency issues**: Check Python version compatibility
4. **Docker build failures**: Verify Dockerfile syntax and dependencies

### Debugging

- Check workflow logs in the Actions tab
- Use `actions/upload-artifact` to preserve intermediate files
- Add debug steps with `echo` commands to troubleshoot
- Use `workflow_dispatch` to test changes without pushing code